"""Persistent guards for connector-driven Operations conversations. No network."""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import secrets
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / ".local/operations-teams"

class GuardError(Exception):
    pass

def utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def digest(text):
    value = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    value = re.sub(r"\\([\-_*])", r"\1", value)
    return hashlib.sha256(" ".join(value.split()).encode()).hexdigest()

def verify_chat(chat, members, users, config):
    if chat.get("chat_type") != "oneOnOne":
        raise GuardError("not_one_on_one")
    url = urlsplit(chat.get("webUrl") or chat.get("display_url") or "")
    if url.scheme != "https" or url.hostname != "teams.microsoft.com":
        raise GuardError("unverified_chat_url")
    if parse_qs(url.query).get("tenantId") != [config["tenant_id"]]:
        raise GuardError("wrong_tenant")
    if len(members) != 2:
        raise GuardError("membership_not_exactly_two")
    emails = [m.get("email", "").strip().lower() for m in members]
    if len(set(emails)) != 2 or config["owner_email"] not in emails:
        raise GuardError("owner_or_members_missing")
    pair = []
    for email in emails:
        if email.rsplit("@", 1)[-1] not in config["allowed_domains"]:
            raise GuardError("external_member")
        matches = [u for u in users if u.get("email", "").lower() == email
                   and u.get("user_principal_name", "").lower() == email
                   and u.get("match_type") == "exact" and u.get("id")]
        if len(matches) != 1 or "#ext#" in matches[0]["user_principal_name"].lower():
            raise GuardError("unverified_directory_identity")
        pair.append(matches[0])
    owner = next(u for u in pair if u["email"].lower() == config["owner_email"])
    if owner["id"] != config["owner_id"]:
        raise GuardError("wrong_owner")
    peer = next(u for u in pair if u["id"] != config["owner_id"])
    return {"chat_id": chat["id"], "peer_id": peer["id"], "peer_email": peer["email"].lower()}

class Store:
    def __init__(self, state=STATE, clock=time.time):
        self.state, self.clock = Path(state), clock
        self.state.mkdir(parents=True, exist_ok=True)
        self.config = json.loads((self.state / "config.json").read_text(encoding="utf-8-sig"))
        self.db = sqlite3.connect(self.state / "state.sqlite3", timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS lease (singleton INTEGER PRIMARY KEY, token TEXT, expires REAL);
        CREATE TABLE IF NOT EXISTS requests (chat TEXT, message TEXT, sender TEXT, created TEXT,
          body_hash TEXT, state TEXT, token TEXT, response_hash TEXT, response_id TEXT, updated REAL,
          PRIMARY KEY(chat,message));
        CREATE TABLE IF NOT EXISTS cursors (chat TEXT PRIMARY KEY, since TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS acknowledgements (chat TEXT, message TEXT, token TEXT,
          body_hash TEXT, state TEXT, response_id TEXT, PRIMARY KEY(chat,message));
        """)

    def enabled(self):
        if not self.config.get("enabled") or not (self.state / "service.enabled").is_file():
            raise GuardError("service_disabled")

    def acquire(self):
        self.enabled()
        self.db.execute("BEGIN IMMEDIATE")
        row = self.db.execute("SELECT * FROM lease WHERE singleton=1").fetchone()
        if row and row["expires"] > self.clock():
            self.db.rollback()
            raise GuardError("run_already_active")
        # Expired work remains visible for review; never retry an uncertain send.
        self.db.execute("UPDATE requests SET state='needs_review' WHERE state IN ('claimed','sending')")
        token = secrets.token_hex(20)
        self.db.execute("INSERT OR REPLACE INTO lease VALUES (1,?,?)", (token, self.clock()+1800))
        self.db.commit()
        return {"run_token": token, "activated_at": self.config["activated_at"]}

    def check_token(self, token):
        self.enabled()
        row = self.db.execute("SELECT * FROM lease WHERE singleton=1").fetchone()
        if not row or row["token"] != token or row["expires"] <= self.clock():
            raise GuardError("invalid_run_token")

    def release(self, token):
        self.db.execute("DELETE FROM lease WHERE token=?", (token,))
        self.db.commit()
        return {"released": True}

    def renew(self, token):
        self.check_token(token)
        self.db.execute("UPDATE lease SET expires=? WHERE token=?", (self.clock()+1800, token))
        self.db.commit()

    def failed(self, token, chat, message):
        self.db.execute("UPDATE requests SET state='needs_review',updated=? WHERE chat=? AND message=? AND token=? AND state='claimed'",
            (self.clock(), chat, message, token))
        self.db.commit()

    def ack_prepare(self, payload):
        self.check_token(payload['run_token'])
        row=self.db.execute('SELECT * FROM requests WHERE chat=? AND message=?',
            (payload['chat_id'],payload['message_id'])).fetchone()
        if not row or row['state']!='claimed' or row['token']!=payload['run_token']:
            raise GuardError('ack_request_not_owned')
        binding=verify_chat(payload['chat'],payload['members'],payload['users'],self.config)
        if binding['chat_id']!=row['chat'] or binding['peer_id']!=row['sender']:
            raise GuardError('ack_recipient_changed')
        original=payload['original']
        if (original.get('message_id')!=row['message'] or original.get('chat_id')!=row['chat']
            or original.get('author_user_id')!=row['sender'] or original.get('deleted_at')
            or digest(original.get('content'))!=row['body_hash']):
            raise GuardError('ack_request_changed')
        text=payload['text_content']
        try:
            self.db.execute('INSERT INTO acknowledgements VALUES (?,?,?,?,'
                "'sending',NULL)",(row['chat'],row['message'],payload['run_token'],digest(text)))
            self.db.commit()
        except sqlite3.IntegrityError:
            self.db.rollback()
            raise GuardError('ack_already_prepared')
        return {'chat_id':row['chat'],'text_content':text}

    def ack_sent(self,payload):
        row=self.db.execute('SELECT * FROM acknowledgements WHERE chat=? AND message=?',
            (payload['chat_id'],payload['message_id'])).fetchone()
        reply=payload['reply']
        if (not row or row['token']!=payload['run_token'] or row['state']!='sending'
            or reply.get('chat_id')!=row['chat'] or reply.get('author_user_id')!=self.config['owner_id']
            or not reply.get('message_id') or digest(reply.get('content'))!=row['body_hash']):
            raise GuardError('ack_receipt_mismatch')
        self.db.execute("UPDATE acknowledgements SET state='sent',response_id=? WHERE chat=? AND message=?",
            (reply['message_id'],row['chat'],row['message']))
        self.db.commit()

    def scan(self, payload):
        self.check_token(payload["run_token"])
        binding = verify_chat(payload["chat"], payload["members"], payload["users"], self.config)
        chat_id, peer = binding["chat_id"], binding["peer_id"]
        since = self.config["activated_at"]
        candidates, ignored = [], []
        messages = sorted(payload["messages"], key=lambda m:(m.get("created_at") or "", m.get("message_id") or ""))
        self.db.execute("BEGIN IMMEDIATE")
        try:
            for message in messages:
                mid = message.get("message_id")
                if (message.get("chat_id") != chat_id or message.get("path") != f"/chats/{chat_id}/messages/{mid}"):
                    raise GuardError("message_chat_mismatch")
                if not mid or not message.get("created_at"):
                    raise GuardError("missing_message_identity")
                if (utc(message["created_at"]) < utc(since)
                    or message.get("author_user_id") != peer
                    or message.get("author_application_id")
                    or message.get("message_type") != "message"
                    or message.get("deleted_at")):
                    ignored.append(mid)
                    continue
                fingerprint = digest(message.get("content"))
                existing = self.db.execute("SELECT * FROM requests WHERE chat=? AND message=?", (chat_id,mid)).fetchone()
                if existing:
                    if existing["body_hash"] != fingerprint:
                        self.db.execute("UPDATE requests SET state='edited_needs_review',updated=? WHERE chat=? AND message=?", (self.clock(),chat_id,mid))
                        continue
                    if not (self.config.get('retry_unsent_claims') and existing['state']=='needs_review'
                            and existing['response_hash'] is None and existing['token']!=payload['run_token']):continue
                    self.db.execute("UPDATE requests SET state='claimed',token=?,updated=? WHERE chat=? AND message=?",
                        (payload['run_token'],self.clock(),chat_id,mid))
                else:
                    self.db.execute("INSERT INTO requests VALUES (?,?,?,?,?,'claimed',?,NULL,NULL,?)",
                        (chat_id,mid,peer,message["created_at"],fingerprint,payload["run_token"],self.clock()))
                candidates.append({**binding, "message_id":mid, "created_at":message["created_at"],
                    "content":message.get("content"), "has_attachments":message.get("has_attachments",False),
                    "body_hash":fingerprint})
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"requests": candidates, "ignored":ignored,
                "coverage_complete":bool(payload.get("coverage_complete")), "binding":binding}

    def prepare(self, payload):
        self.check_token(payload["run_token"])
        row = self.db.execute("SELECT * FROM requests WHERE chat=? AND message=?", (payload["chat_id"],payload["message_id"])).fetchone()
        if not row or row["state"] != "claimed" or row["token"] != payload["run_token"]:
            raise GuardError("request_not_owned_or_already_handled")
        binding = verify_chat(payload["chat"],payload["members"],payload["users"],self.config)
        if binding["chat_id"] != row["chat"] or binding["peer_id"] != row["sender"]:
            raise GuardError("reply_recipient_changed")
        original = payload["original"]
        if (original.get("chat_id") != row["chat"] or original.get("message_id") != row["message"]
            or original.get("author_user_id") != row["sender"] or original.get("deleted_at")
            or original.get("path") != f"/chats/{row['chat']}/messages/{row['message']}"
            or digest(original.get("content")) != row["body_hash"]):
            raise GuardError("request_changed")
        response = payload["text_content"]
        if not isinstance(response,str) or not response.strip() or len(response)>20000:
            raise GuardError("invalid_response")
        self.db.execute("UPDATE requests SET state='sending',response_hash=?,updated=? WHERE chat=? AND message=?",
            (digest(response),self.clock(),row["chat"],row["message"]))
        self.db.commit()
        return {"chat_id":row["chat"],"text_content":response,"request_message_id":row["message"],"response_hash":digest(response)}

    def sent(self,payload):
        # A receipt may arrive after the lease expired; match it to the prepared reply.
        row = self.db.execute("SELECT * FROM requests WHERE chat=? AND message=?",(payload["chat_id"],payload["message_id"])).fetchone()
        if not row or row["state"] not in ("sending","needs_review") or row["token"] != payload["run_token"]:
            raise GuardError("no_prepared_send")
        reply = payload["reply"]
        if (reply.get("chat_id") != row["chat"] or reply.get("author_user_id") != self.config["owner_id"]
            or not reply.get("message_id") or digest(reply.get("content")) != row["response_hash"]):
            raise GuardError("receipt_mismatch")
        self.db.execute("UPDATE requests SET state='sent',response_id=?,updated=? WHERE chat=? AND message=?",
            (reply["message_id"],self.clock(),row["chat"],row["message"]))
        self.db.commit()
        return {"state":"sent","response_id":reply["message_id"]}

    def checkpoint(self,payload):
        self.check_token(payload["run_token"])
        if not payload.get("coverage_complete"):
            raise GuardError("incomplete_scan")
        if utc(payload["since"]) < utc(self.config["activated_at"]):
            raise GuardError("invalid_checkpoint")
        old = self.db.execute("SELECT since FROM cursors WHERE chat=?",(payload["chat_id"],)).fetchone()
        if not old or utc(old["since"]) < utc(payload["since"]):
            self.db.execute("INSERT OR REPLACE INTO cursors VALUES (?,?)",(payload["chat_id"],payload["since"]))
            self.db.commit()
        return {"checkpoint_saved":True}

    def status(self):
        return {"enabled":bool(self.config.get("enabled") and (self.state/"service.enabled").is_file()),
            "activated_at":self.config["activated_at"],
            "counts":{r[0]:r[1] for r in self.db.execute("SELECT state,count(*) FROM requests GROUP BY state")},
            "cursors":{r[0]:r[1] for r in self.db.execute("SELECT chat,since FROM cursors")},
            "unresolved":[dict(r) for r in self.db.execute("SELECT chat,message,state,response_hash,response_id,token FROM requests WHERE state NOT IN ('sent','ignored')")]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=["acquire","release","scan","prepare","sent","checkpoint","status"])
    parser.add_argument("--state",type=Path,default=STATE)
    args=parser.parse_args()
    store=Store(args.state)
    try:
        data={} if args.command in ("acquire","status") else json.load(sys.stdin)
        if args.command=="acquire":result=store.acquire()
        elif args.command=="status":result=store.status()
        elif args.command=="release":result=store.release(data["run_token"])
        else:result=getattr(store,args.command)(data)
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (GuardError,KeyError,ValueError) as error:
        print(json.dumps({"error":str(error)}))
        return 2
    finally:store.db.close()

if __name__=="__main__":raise SystemExit(main())
