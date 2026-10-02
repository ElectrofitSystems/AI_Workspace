"""My Avatar v0.1 local MCP Events bridge (Windows prototype)."""
from __future__ import annotations

import argparse
import base64
import ctypes
import hashlib
import hmac
import http.client
import ipaddress
import json
import os
import secrets
import socket
import sqlite3
import ssl
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

LIMIT = 16_384
STATUS_TOOL = "get_myavatar_status"
PENDING_TOOL = "get_pending_internal_teams_message"


class Rejected(Exception):
    pass


def compact(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


class Dpapi:
    class Blob(ctypes.Structure):
        _fields_ = [("size", ctypes.c_ulong), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    def transform(self, value: bytes, protect: bool) -> bytes:
        if os.name != "nt":
            raise Rejected("Windows DPAPI is required")
        buffer = ctypes.create_string_buffer(value)
        source = self.Blob(len(value), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
        target = self.Blob()
        api = ctypes.windll.crypt32
        function = api.CryptProtectData if protect else api.CryptUnprotectData
        if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
            raise Rejected("Secret protection failed")
        try:
            return ctypes.string_at(target.data, target.size)
        finally:
            ctypes.windll.kernel32.LocalFree(ctypes.cast(target.data, ctypes.c_void_p))

    def seal(self, value: object) -> bytes:
        return self.transform(compact(value), True)

    def open(self, value: bytes) -> object:
        return json.loads(self.transform(value, False))


def signing_key(secret: str) -> bytes:
    try:
        if not isinstance(secret, str) or not secret.startswith("whsec_"):
            raise ValueError
        key = base64.b64decode(secret[6:], validate=True)
        if not 24 <= len(key) <= 64:
            raise ValueError
        return key
    except (ValueError, TypeError):
        raise Rejected("Invalid signing secret") from None


def signed_headers(keys: list[str], event_id: str, body: bytes, subscription_id: str, now: float) -> dict[str, str]:
    stamp = str(int(now))
    source = event_id.encode() + b"." + stamp.encode() + b"." + body
    signatures = ["v1," + base64.b64encode(hmac.digest(signing_key(key), source, "sha256")).decode() for key in keys]
    return {
        "Content-Type": "application/json",
        "webhook-id": event_id,
        "webhook-timestamp": stamp,
        "webhook-signature": " ".join(signatures),
        "X-MCP-Subscription-Id": subscription_id,
    }


def callback_target(url: str, allowed_hosts: set[str]):
    try:
        parts = urlsplit(url)
        if (parts.scheme != "https" or parts.username or parts.password or parts.fragment
                or parts.port not in (None, 443) or parts.hostname not in allowed_hosts):
            raise ValueError
        return parts
    except (ValueError, TypeError):
        raise Rejected("Callback host not approved") from None


def public_addresses(host: str) -> list[str]:
    addresses = {item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise Rejected("Callback resolved to a non-public address")
    return sorted(addresses)


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host: str, address: str):
        super().__init__(host, 443, timeout=10, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


class CallbackTransport:
    def __init__(self, allowed_hosts: set[str]):
        self.allowed_hosts = allowed_hosts

    def __call__(self, url: str, headers: dict[str, str], body: bytes):
        parts = callback_target(url, self.allowed_hosts)
        connection = PinnedHTTPS(parts.hostname, public_addresses(parts.hostname)[0])
        try:
            path = parts.path or "/"
            if parts.query:
                path += "?" + parts.query
            connection.request("POST", path, body, headers)
            response = connection.getresponse()
            result = response.read(LIMIT + 1)
            if len(result) > LIMIT:
                raise Rejected("Callback response too large")
            return response.status, result
        finally:
            connection.close()


class Bridge:
    def __init__(self, root: Path, settings: dict, transport=None, vault=None, clock=time.time):
        self.root = root
        self.settings = settings
        self.event = settings["bridge"]["eventName"]
        self.switch = root / "config" / "auto-reply.enabled"
        self.skill_root = root / "skills"
        self.clock = clock
        self.started = clock()
        self.lock = threading.RLock()
        hosts = set(settings["bridge"]["callbackHosts"])
        self.transport = transport or CallbackTransport(hosts)
        self.vault = vault or Dpapi()
        database = root / "data" / "state.sqlite3"
        database.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(database, check_same_thread=False)
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS subscriptions
            (id TEXT PRIMARY KEY, url TEXT NOT NULL, expires REAL NOT NULL, secret BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS deliveries
            (subscription TEXT, event TEXT, payload BLOB NOT NULL, status TEXT NOT NULL,
             attempts INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(subscription,event));
          CREATE TABLE IF NOT EXISTS teams_events
            (conversation_key TEXT NOT NULL, message_key TEXT NOT NULL,
             conversation_id TEXT NOT NULL, message_id TEXT NOT NULL,
             created REAL NOT NULL, PRIMARY KEY(conversation_key,message_key));
          CREATE TABLE IF NOT EXISTS teams_reply_claims
            (conversation_id TEXT NOT NULL, message_id TEXT NOT NULL,
             claimed REAL NOT NULL, state TEXT NOT NULL,
             PRIMARY KEY(conversation_id,message_id));
        """)
        self.db.commit()

    def identity(self, params: dict):
        if params.get("name") != self.event or params.get("arguments") != {"queue": "verified_internal"}:
            raise Rejected("Unsupported event or queue")
        delivery = params.get("delivery", {})
        if delivery.get("mode") != "webhook":
            raise Rejected("Webhook delivery required")
        url = delivery.get("url")
        callback_target(url, set(self.settings["bridge"]["callbackHosts"]))
        return "sub_" + hashlib.sha256(compact([url, self.event])).hexdigest(), url

    def subscribe(self, params: dict):
        with self.lock:
            subscription_id, url = self.identity(params)
            secret = params.get("delivery", {}).get("secret")
            signing_key(secret)
            ttl = params.get("ttlMs", 3_600_000)
            if isinstance(ttl, bool) or not isinstance(ttl, (int, float)) or ttl <= 0:
                raise Rejected("Invalid subscription lifetime")
            now = self.clock()
            challenge = secrets.token_urlsafe(32)
            body = compact({"type": "verification", "challenge": challenge})
            headers = signed_headers([secret], "verify_" + secrets.token_hex(16), body, subscription_id, now)
            status, response = self.transport(url, headers, body)
            try:
                echoed = json.loads(response).get("challenge", "")
                verified = isinstance(echoed, str) and hmac.compare_digest(challenge, echoed)
            except (ValueError, AttributeError):
                verified = False
            if not 200 <= status < 300 or not verified:
                raise Rejected("Callback verification failed")
            expires = now + min(float(ttl) / 1000, 86_400)
            self.db.execute("INSERT OR REPLACE INTO subscriptions VALUES (?,?,?,?)",
                            (subscription_id, url, expires, self.vault.seal({"current": secret})))
            self.db.commit()
            return {"id": subscription_id, "refreshBefore": datetime.fromtimestamp(expires, timezone.utc).isoformat(),
                    "cursor": None, "truncated": False}

    def skills(self):
        result = []
        if not self.skill_root.is_dir():
            return result
        for entry in sorted(self.skill_root.iterdir()):
            skill = entry / "SKILL.md"
            if skill.is_file():
                text = skill.read_text(encoding="utf-8")
                lines = text.splitlines()
                metadata = {}
                if lines and lines[0].strip() == "---":
                    for line in lines[1:]:
                        if line.strip() == "---":
                            break
                        if ":" in line:
                            key, value = line.split(":", 1)
                            if key.strip() in ("name", "description"):
                                metadata[key.strip()] = value.strip().strip('"').strip("'")
                if metadata.get("name") != entry.name or not metadata.get("description"):
                    raise Rejected(f"Invalid skill frontmatter: {entry.name}")
                resources = []
                for path in sorted(entry.rglob("*")):
                    if path.is_file():
                        relative = path.relative_to(self.skill_root).as_posix()
                        content = path.read_bytes()
                        resources.append({"uri": f"skill://my-avatar/{relative}",
                                          "digest": "sha256:" + hashlib.sha256(content).hexdigest()})
                result.append({"uri": f"skill://my-avatar/{entry.name}/SKILL.md",
                               "frontmatter": metadata,
                               "resources": resources})
        return result

    def rpc(self, method: str, params: dict | None):
        params = params or {}
        if method == "server/discover":
            return {"resultType": "complete", "supportedVersions": ["2026-07-28"],
                    "capabilities": {"tools": {"listChanged": False}, "events": {},
                                     "extensions": {"io.modelcontextprotocol/skills": {}}}}
        if method == "events/list":
            return {"events": [{"name": self.event,
                "description": "Verified internal Teams event containing opaque references only.",
                "delivery": ["webhook"],
                "inputSchema": {"type": "object", "properties": {"queue": {"const": "verified_internal"}},
                                "required": ["queue"], "additionalProperties": False},
                "payloadSchema": {"type": "object", "properties": {
                    "queue": {"const": "verified_internal"},
                    "conversationId": {"type": "string"}, "messageId": {"type": "string"}},
                    "required": ["queue", "conversationId", "messageId"], "additionalProperties": False}}]}
        if method == "events/subscribe":
            return self.subscribe(params)
        if method == "events/unsubscribe":
            subscription_id, _ = self.identity(params)
            self.db.execute("DELETE FROM subscriptions WHERE id=?", (subscription_id,))
            self.db.commit()
            return {"unsubscribed": True}
        if method == "skills/list":
            return {"skills": self.skills(), "nextCursor": None}
        if method == "skills/get":
            skill = next((item for item in self.skills() if item["uri"] == params.get("uri")), None)
            if not skill:
                raise Rejected("Unknown skill")
            return {"skill": skill}
        if method == "resources/read":
            uri = params.get("uri", "")
            prefix = "skill://my-avatar/"
            if not uri.startswith(prefix):
                raise Rejected("Unknown resource")
            relative = Path(uri[len(prefix):])
            if relative.is_absolute() or ".." in relative.parts:
                raise Rejected("Unsafe resource path")
            path = (self.skill_root / relative).resolve()
            if not path.is_file() or self.skill_root.resolve() not in path.parents:
                raise Rejected("Unknown resource")
            return {"contents": [{"uri": uri, "mimeType": "text/markdown",
                                  "text": path.read_text(encoding="utf-8")}]}
        if method == "tools/list":
            empty = {"type": "object", "properties": {}, "additionalProperties": False}
            annotations = {"readOnlyHint": True, "openWorldHint": False,
                           "destructiveHint": False, "idempotentHint": True}
            return {"tools": [
                {"name": STATUS_TOOL, "title": "Get My Avatar status",
                 "description": "Check bridge readiness without returning Teams content.",
                 "inputSchema": empty, "annotations": annotations},
                {"name": PENDING_TOOL, "title": "Claim latest verified Teams event",
                 "description": "Atomically claim the latest verified event and return its exact Teams path.",
                 "inputSchema": empty, "annotations": annotations},
            ]}
        if method == "tools/call":
            name, arguments = params.get("name"), params.get("arguments", {})
            if arguments != {}:
                raise Rejected("Invalid arguments")
            if name == STATUS_TOOL:
                return {"structuredContent": {"status": "ready", "event": self.event,
                                                "autoReplyEnabled": self.switch.is_file()},
                        "content": [{"type": "text", "text": "My Avatar bridge is ready."}]}
            if name == PENDING_TOOL:
                with self.lock:
                    if not self.switch.is_file():
                        raise Rejected("Automatic replies are disabled")
                    row = self.db.execute(
                        "SELECT e.conversation_id,e.message_id FROM teams_events e "
                        "LEFT JOIN teams_reply_claims c ON c.conversation_id=e.conversation_id "
                        "AND c.message_id=e.message_id WHERE c.conversation_id IS NULL AND e.created>=? "
                        "ORDER BY e.created DESC LIMIT 1", (self.started,)).fetchone()
                    if not row:
                        raise Rejected("No unclaimed event")
                    self.db.execute("INSERT INTO teams_reply_claims VALUES (?,?,?,?)",
                                    (row[0], row[1], self.clock(), "claimed"))
                    self.db.commit()
                payload = {"path": f"/chats/{row[0]}/messages/{row[1]}", "verifiedInternal": True,
                           "autoReplyEnabled": True, "killSwitchEngaged": False,
                           "duplicate": False, "claimState": "claimed"}
                return {"content": [{"type": "text", "text": json.dumps(payload, separators=(",", ":"))}]}
            raise Rejected("Unknown tool")
        raise Rejected("Unknown method")

    def ingest(self, payload: dict):
        if not isinstance(payload, dict) or set(payload) != {"conversationId", "messageId"}:
            raise Rejected("Unexpected ingress schema")
        conversation_id, message_id = payload["conversationId"], payload["messageId"]
        if any(not isinstance(value, str) or not 1 <= len(value) <= 512 for value in (conversation_id, message_id)):
            raise Rejected("Invalid identifier")
        salt = os.environ.get("MYAVATAR_EVENT_SALT", "")
        if len(salt) < 32:
            raise Rejected("Event salt is not configured")
        conversation_key = "conv_" + hmac.new(salt.encode(), conversation_id.encode(), "sha256").hexdigest()
        message_key = "msg_" + hmac.new(salt.encode(), message_id.encode(), "sha256").hexdigest()
        with self.lock:
            self.db.execute("INSERT OR IGNORE INTO teams_events VALUES (?,?,?,?,?)",
                            (conversation_key, message_key, conversation_id, message_id, self.clock()))
            self.db.commit()
            subscriptions = self.db.execute("SELECT id,url,expires,secret FROM subscriptions WHERE expires>?",
                                            (self.clock(),)).fetchall()
        event_payload = {"queue": "verified_internal", "conversationId": conversation_key,
                         "messageId": message_key}
        body = compact({"type": "event", "name": self.event, "arguments": event_payload})
        event_id = "evt_" + hashlib.sha256(compact(event_payload)).hexdigest()
        delivered = False
        for subscription_id, url, _, sealed in subscriptions:
            existing = self.db.execute("SELECT status FROM deliveries WHERE subscription=? AND event=?",
                                       (subscription_id, event_id)).fetchone()
            if existing and existing[0] == "accepted":
                delivered = True
                continue
            key = self.vault.open(sealed)["current"]
            status, _ = self.transport(url, signed_headers([key], event_id, body, subscription_id, self.clock()), body)
            outcome = "accepted" if 200 <= status < 300 else "failed"
            self.db.execute("INSERT OR REPLACE INTO deliveries VALUES (?,?,?,?,COALESCE((SELECT attempts FROM deliveries WHERE subscription=? AND event=?),0)+1)",
                            (subscription_id, event_id, body, outcome, subscription_id, event_id))
            self.db.commit()
            delivered = delivered or outcome == "accepted"
        return 202 if delivered else 409


def handler_for(bridge: Bridge, mcp_token: str, ingress_token: str):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, status: int, payload: object):
            body = compact(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            token = self.headers.get("Authorization", "")
            expected = {"/mcp": mcp_token, "/ingress/teams": ingress_token}.get(self.path)
            if not expected or not hmac.compare_digest(token, "Bearer " + expected):
                self.reply(401, {"error": "unauthorized"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= LIMIT:
                    raise Rejected("Invalid body size")
                request = json.loads(self.rfile.read(length))
                if self.path == "/ingress/teams":
                    self.reply(bridge.ingest(request), {"accepted": True})
                    return
                result = bridge.rpc(request.get("method"), request.get("params"))
                self.reply(200, {"jsonrpc": "2.0", "id": request.get("id"), "result": result})
            except (Rejected, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
                self.reply(400, {"error": str(error)})

    return Handler


def load_settings(root: Path) -> dict:
    return json.loads((root / "config" / "settings.json").read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    settings = load_settings(root)
    mcp_token = os.environ.get("MYAVATAR_MCP_TOKEN", "")
    ingress_token = os.environ.get("MYAVATAR_INGRESS_TOKEN", "")
    if min(len(mcp_token), len(ingress_token)) < 32 or hmac.compare_digest(mcp_token, ingress_token):
        parser.error("Two distinct tokens of at least 32 characters are required")
    bridge = Bridge(root, settings)
    host = settings["bridge"]["bindHost"]
    port = int(settings["bridge"]["port"])
    if host not in ("127.0.0.1", "::1", "localhost"):
        parser.error("The v0.1 bridge must bind to loopback")
    server = ThreadingHTTPServer((host, port), handler_for(bridge, mcp_token, ingress_token))
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
