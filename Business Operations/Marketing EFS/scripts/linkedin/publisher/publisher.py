"""Local, approval-gated LinkedIn publisher. Python standard library only."""
import argparse
import base64
import ctypes
import getpass
import hashlib
import hmac
import html
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs, quote
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
WORKSPACE = next((p for p in ROOT.parents if (p / 'AGENTS.md').is_file()), None)
DEFAULT_DATA = WORKSPACE / 'output/Linkedin/publisher' if WORKSPACE else ROOT / 'local-data'
ROLES = {'ADMINISTRATOR', 'CONTENT_ADMIN'}

class GuardError(Exception):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def protect(data, decrypt=False):
    """Windows DPAPI, current-user scope; never fall back to plaintext."""
    if os.name != 'nt':
        raise GuardError('Credential storage requires Windows DPAPI on this installation.')
    from ctypes import wintypes
    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_byte))]
    buf = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))
    result = Blob()
    fn = ctypes.windll.crypt32.CryptUnprotectData if decrypt else ctypes.windll.crypt32.CryptProtectData
    ok = fn(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result))
    if not ok:
        raise GuardError('Windows credential encryption failed.')
    try:
        return ctypes.string_at(result.data, result.size)
    finally:
        ctypes.windll.kernel32.LocalFree(result.data)

class Vault:
    def __init__(self, directory):
        self.path = directory / 'credentials.dpapi'
    def read(self):
        return json.loads(protect(self.path.read_bytes(), True)) if self.path.exists() else {}
    def save(self, value):
        temp = self.path.with_suffix('.tmp')
        temp.write_bytes(protect(canonical(value).encode('utf-8')))
        os.replace(str(temp), str(self.path))

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class LinkedIn:
    """No automatic retries or redirects, and no token-bearing diagnostics."""
    def __init__(self, token, version):
        self.token, self.version = token, version
    def request(self, method, path, payload=None):
        if not path.startswith('/rest/'):
            raise GuardError('Unsupported API path.')
        headers = {'Authorization': 'Bearer '+self.token, 'LinkedIn-Version': self.version,
                   'X-Restli-Protocol-Version': '2.0.0', 'Content-Type': 'application/json'}
        data = canonical(payload).encode('utf-8') if payload is not None else None
        return self.send(Request('https://api.linkedin.com'+path, data=data, headers=headers, method=method))
    @staticmethod
    def send(req):
        try:
            with build_opener(NoRedirect).open(req, timeout=25) as res:
                raw = res.read(2_000_000)
                return (json.loads(raw) if raw else {}), dict(res.headers)
        except HTTPError as exc:
            raise GuardError('LinkedIn HTTP %s. Check permissions/connection; no automatic retry.' % exc.code) from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise GuardError('LinkedIn request outcome could not be verified. No automatic retry.') from None
    def organizations(self):
        result = []
        for start in range(0, 10000, 100):
            body, _ = self.request('GET', '/rest/organizationAcls?q=roleAssignee&state=APPROVED&count=100&start='+str(start))
            elements = body.get('elements', [])
            for item in elements:
                org = item.get('organization') or item.get('organizationTarget')
                if item.get('state') == 'APPROVED' and item.get('role') in ROLES and org:
                    result.append({'urn': org, 'role': item['role'], 'member': item.get('roleAssignee')})
            if len(elements) < 100:
                return result
        raise GuardError('Organization enumeration incomplete; publishing blocked.')
    def upload(self, author, media, content):
        body, _ = self.request('POST', '/rest/images?action=initializeUpload', {'initializeUploadRequest': {'owner': author}})
        value = body['value']
        url = urlparse(value['uploadUrl'])
        if url.scheme != 'https' or not (url.hostname == 'www.linkedin.com' or (url.hostname or '').endswith('.linkedin.com')):
            raise GuardError('Unexpected upload host; upload blocked.')
        self.send(Request(value['uploadUrl'], data=content, method='PUT', headers={
            'Authorization': 'Bearer '+self.token, 'Content-Type': media['mime']}))
        for _ in range(10):
            status, _ = self.request('GET', '/rest/images/'+quote(value['image'], safe=''))
            if status.get('status') == 'AVAILABLE':
                return value['image']
            if status.get('status') == 'PROCESSING_FAILED':
                break
            time.sleep(1)
        raise GuardError('Image is not available yet; no post created.')

class Publisher:
    def __init__(self, directory=DEFAULT_DATA, vault=None):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / 'media').mkdir(exist_ok=True)
        self.vault = vault or Vault(self.directory)
        self.config_path = self.directory / 'settings.json'
        if not self.config_path.exists():
            self.config_path.write_text(json.dumps({'api_access': 'under_review', 'live_enabled': False,
                'api_version': '202609', 'organization': None, 'page_url': 'https://www.linkedin.com/company/efitsys/',
                'redirect_uri': '', 'scopes': ['w_organization_social', 'r_organization_social', 'rw_organization_admin']}, indent=2), encoding='utf-8')
        self.db = sqlite3.connect(str(self.directory / 'publisher.sqlite3'), timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, body TEXT NOT NULL, status TEXT NOT NULL, approval TEXT, post_urn TEXT);
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, at TEXT NOT NULL, kind TEXT NOT NULL, post_id TEXT, detail TEXT NOT NULL);
        ''')
        self.db.commit()
    def config(self):
        return json.loads(self.config_path.read_text(encoding='utf-8-sig'))
    def event(self, kind, post_id, detail):
        self.db.execute('INSERT INTO events(at,kind,post_id,detail) VALUES(?,?,?,?)', (now(),kind,post_id,canonical(detail)))
    def list(self):
        return [dict(r) for r in self.db.execute('SELECT id,revision,status,post_urn FROM drafts ORDER BY id')]
    def get(self, post_id):
        row = self.db.execute('SELECT * FROM drafts WHERE id=?',(post_id,)).fetchone()
        if not row:
            raise GuardError('Draft not found.')
        result = dict(row)
        result['body'] = json.loads(result['body'])
        result['approval'] = json.loads(result['approval']) if result['approval'] else None
        return result
    def save_draft(self, post_id, commentary, media_path=None, alt_text='', blockers=None, expected_revision=0):
        if not re.fullmatch(r'[A-Z0-9][A-Z0-9_-]{0,63}', post_id):
            raise GuardError('Use an uppercase post ID, e.g. EFS-001.')
        if not isinstance(commentary, str) or not commentary.strip() or len(commentary) > 2500:
            raise GuardError('Bilingual commentary must contain 1–2,500 characters.')
        if not isinstance(blockers or [], list) or any(not isinstance(x,str) for x in blockers or []):
            raise GuardError('Blockers must be a list of strings.')
        if len(alt_text) > 4086:
            raise GuardError('Alt text is too long.')
        media = None
        if media_path:
            p = Path(media_path).resolve()
            if not p.is_file() or p.suffix.lower() not in ('.png','.jpg','.jpeg') or p.stat().st_size > 10_000_000:
                raise GuardError('Select a PNG/JPEG file no larger than 10 MB.')
            data = p.read_bytes()
            mime = 'image/png' if data.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if data.startswith(b'\xff\xd8\xff') else None
            if not mime:
                raise GuardError('Image bytes do not match a PNG/JPEG.')
            sha = hashlib.sha256(data).hexdigest()
            filename = sha + ('.png' if mime == 'image/png' else '.jpg')
            (self.directory/'media'/filename).write_bytes(data)
            media = {'file':filename,'sha256':sha,'mime':mime,'alt_text':alt_text}
        body = {'commentary':commentary,'media':media,'blockers':blockers or [],'publication':'manual_after_approval','timezone':'Europe/Rome'}
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            old = self.db.execute('SELECT revision,status FROM drafts WHERE id=?',(post_id,)).fetchone()
            if (old['revision'] if old else 0) != expected_revision:
                raise GuardError('Revision conflict; reload before editing.')
            if old and old['status'] in ('publishing','outcome_unknown','published'):
                raise GuardError('This job cannot be edited; reconcile it or create a new post ID.')
            rev = expected_revision+1
            self.db.execute('INSERT OR REPLACE INTO drafts VALUES(?,?,?,?,NULL,NULL)',(post_id,rev,canonical(body),'needs_review'))
            self.event('draft_saved',post_id,{'revision':rev})
        return self.get(post_id)
    def media_bytes(self, media):
        if not media:
            raise GuardError('Final image missing.')
        if not re.fullmatch(r'[a-f0-9]{64}\.(png|jpg)', media['file']):
            raise GuardError('Invalid media reference.')
        data = (self.directory/'media'/media['file']).read_bytes()
        if hashlib.sha256(data).hexdigest() != media['sha256']:
            raise GuardError('Media changed after review; save a new revision.')
        return data
    def envelope(self, draft):
        c = self.config()
        return {'id':draft['id'],'revision':draft['revision'],'body':draft['body'],
                'organization':c['organization'],'page_url':c['page_url'],
                'mode':'live' if c['live_enabled'] else 'dry_run'}
    def dry_run(self, post_id):
        d = self.get(post_id)
        errors = list(d['body']['blockers'])
        try:
            self.media_bytes(d['body']['media'])
        except (GuardError, OSError) as exc:
            errors.append(str(exc) if isinstance(exc,GuardError) else 'Final image missing.')
        if not self.config()['organization']:
            errors.append('LinkedIn organization has not been verified and selected.')
        return {'mode':'dry_run','network_calls':0,'post_id':post_id,'revision':d['revision'],
                'characters':len(d['body']['commentary']),'payload_hash':digest(self.envelope(d)),
                'ready_for_review':not errors,'blockers':errors,'status':d['status']}
    def authenticate(self, password):
        v = self.vault.read()
        review = v.get('reviewer')
        if not review:
            raise GuardError('Reviewer not enrolled. Run reviewer-setup in your terminal.')
        candidate = hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(review['salt']),600000).hex()
        if not hmac.compare_digest(candidate,review['hash']):
            time.sleep(1)
            raise GuardError('Reviewer authentication failed.')
        return v
    def approve(self, post_id, password, expected_hash):
        v = self.authenticate(password)
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            d = self.get(post_id)
            if d['status'] not in ('needs_review','approved'):
                raise GuardError('Job is not available for approval.')
            validation = self.dry_run(post_id)
            if validation['blockers']:
                raise GuardError('Resolve the review blockers first.')
            actual = digest(self.envelope(d))
            if not hmac.compare_digest(actual, expected_hash):
                raise GuardError('Payload changed; review it again.')
            record = {'hash':actual,'at':now(),'reviewer':v['reviewer']['name'],'mode':self.envelope(d)['mode']}
            record['signature'] = hmac.new(bytes.fromhex(v['approval_key']),canonical(record).encode(),hashlib.sha256).hexdigest()
            self.db.execute('UPDATE drafts SET status=?,approval=? WHERE id=?',('approved',canonical(record),post_id))
            self.event('authenticated_approval',post_id,record)
        return {'status':'approved','mode':record['mode'],'revision':d['revision']}
    def client(self):
        c, v = self.config(), self.vault.read()
        if c['api_access'] != 'approved':
            raise GuardError('LinkedIn API access is under review.')
        token = v.get('token', {})
        if token.get('expires_at',0) <= time.time()+60:
            raise GuardError('LinkedIn connection missing or expired; reconnect.')
        if not re.fullmatch(r'20\d{4}',c['api_version']):
            raise GuardError('Set a supported LinkedIn API version.')
        return LinkedIn(token['access_token'],c['api_version'])
    def status(self):
        c = self.config()
        v = self.vault.read()
        return {'api_access':c['api_access'],'live_enabled':c['live_enabled'],
                'organization':c['organization'],'reviewer_enrolled':bool(v.get('reviewer')),
                'credentials_configured':bool(v.get('client_secret')),
                'token_valid':v.get('token',{}).get('expires_at',0)>time.time()+60,
                'review_url':'http://127.0.0.1:8787/','scheduler':'not configured'}
    def publish(self, post_id):
        if not self.config()['live_enabled']:
            raise GuardError('Live publishing disabled. Use dry_run; nothing was sent.')
        client = self.client()
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            d = self.get(post_id)
            if d['status'] == 'published':
                return {'status':'published','post_urn':d['post_urn'],'duplicate_prevented':True}
            if d['status'] != 'approved' or not d['approval']:
                raise GuardError('Exact revision needs authenticated approval, or prior outcome requires reconciliation.')
            a = dict(d['approval'])
            signature = a.pop('signature')
            key = bytes.fromhex(self.vault.read()['approval_key'])
            if not hmac.compare_digest(signature,hmac.new(key,canonical(a).encode(),hashlib.sha256).hexdigest()):
                raise GuardError('Invalid approval record.')
            if a['mode'] != 'live' or a['hash'] != digest(self.envelope(d)):
                raise GuardError('Approval no longer matches payload, destination or publishing mode.')
            if self.dry_run(post_id)['blockers']:
                raise GuardError('Review blockers remain.')
            content = self.media_bytes(d['body']['media'])
            author = self.envelope(d)['organization']
            self.db.execute('UPDATE drafts SET status=? WHERE id=?',('publishing',post_id))
            self.event('publishing_started',post_id,{'revision':d['revision']})
        post_started = False
        try:
            if author not in [r['urn'] for r in client.organizations()]:
                raise GuardError('Page authorization could not be verified.')
            image = client.upload(author,d['body']['media'],content)
            payload = {'author':author,'commentary':d['body']['commentary'],'visibility':'PUBLIC',
                'distribution':{'feedDistribution':'MAIN_FEED','targetEntities':[],'thirdPartyDistributionChannels':[]},
                'lifecycleState':'PUBLISHED','isReshareDisabledByAuthor':False,
                'content':{'media':{'id':image,'altText':d['body']['media']['alt_text']}}}
            post_started = True
            _, headers = client.request('POST','/rest/posts',payload)
            urn = next((v for k,v in headers.items() if k.lower()=='x-restli-id'),None)
            if not urn:
                raise GuardError('Post response lacks its identifier; manual reconciliation required.')
            with self.db:
                self.db.execute('UPDATE drafts SET status=?,post_urn=? WHERE id=?',('published',urn,post_id))
                self.event('published',post_id,{'post_urn':urn})
            return {'status':'published','post_urn':urn,'url':'https://www.linkedin.com/feed/update/'+quote(urn,safe=':')+'/'}
        except Exception:
            status = 'outcome_unknown' if post_started else 'needs_review'
            with self.db:
                self.db.execute('UPDATE drafts SET status=?,approval=NULL WHERE id=?',(status,post_id))
                self.event(status,post_id,{'reason':'Publication stopped; no automatic retry.'})
            raise GuardError('Publication stopped. Status: '+status+'. Check connection or reconcile the result.') from None

    def oauth_start(self):
        c, v = self.config(), self.vault.read()
        if c['api_access'] != 'approved':
            raise GuardError('OAuth is disabled while API access is under review.')
        uri = urlparse(c['redirect_uri'])
        if uri.scheme!='https' or not uri.netloc or uri.query or uri.fragment:
            raise GuardError('Configure the exact registered HTTPS callback URL first.')
        if not v.get('client_id') or not v.get('client_secret'):
            raise GuardError('Run credentials-setup in your own terminal.')
        state = secrets.token_urlsafe(32)
        v['oauth'] = {'state':state,'expires_at':time.time()+600,'redirect_uri':c['redirect_uri'],'scopes':c['scopes']}
        self.vault.save(v)
        return 'https://www.linkedin.com/oauth/v2/authorization?'+urlencode({'response_type':'code','client_id':v['client_id'],
            'redirect_uri':c['redirect_uri'],'state':state,'scope':' '.join(c['scopes'])})
    def oauth_complete(self, callback):
        v = self.vault.read()
        pending = v.pop('oauth',None)
        self.vault.save(v) # one use, including failed exchanges
        if not pending or pending['expires_at'] < time.time():
            raise GuardError('OAuth request expired; start again.')
        uri, expected = urlparse(callback), urlparse(pending['redirect_uri'])
        q = parse_qs(uri.query)
        if (uri.scheme,uri.netloc,uri.path)!=(expected.scheme,expected.netloc,expected.path) or not hmac.compare_digest(q.get('state',[''])[0],pending['state']):
            raise GuardError('OAuth callback/state mismatch.')
        if q.get('error') or not q.get('code'):
            raise GuardError('LinkedIn authorization was not completed.')
        form = urlencode({'grant_type':'authorization_code','code':q['code'][0],'redirect_uri':pending['redirect_uri'],
                          'client_id':v['client_id'],'client_secret':v['client_secret']}).encode()
        token,_ = LinkedIn.send(Request('https://www.linkedin.com/oauth/v2/accessToken',data=form,
            headers={'Content-Type':'application/x-www-form-urlencoded'},method='POST'))
        if not token.get('access_token') or not token.get('expires_in'):
            raise GuardError('Incomplete token response.')
        v['token'] = {'access_token':token['access_token'],'expires_at':time.time()+int(token['expires_in'])}
        self.vault.save(v)
        return {'connected':True,'next':'Run organizations, then select the verified ElectroFit organization.'}

def review_server(directory, port=8787):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            if self.headers.get('Host') not in ('127.0.0.1:'+str(port),'localhost:'+str(port)):
                self.send_error(403); return
            p = Publisher(directory)
            try:
                path = urlparse(self.path).path
                if path.startswith('/media/'):
                    filename = path.split('/')[-1]
                    if not re.fullmatch(r'[a-f0-9]{64}\.(png|jpg)', filename):
                        self.send_error(404); return
                    target = p.directory/'media'/filename
                    if not target.is_file():
                        self.send_error(404); return
                    self.send_response(200); self.send_header('Content-Type','image/png' if filename.endswith('.png') else 'image/jpeg'); self.end_headers(); self.wfile.write(target.read_bytes()); return
                if path != '/':
                    self.send_error(404); return
                status = p.status()
                cards = []
                for row in p.list():
                    d = p.get(row['id']); check = p.dry_run(row['id']); body = d['body']
                    visual = '<img src="/media/%s" alt="%s">' % (body['media']['file'],html.escape(body['media']['alt_text'],quote=True)) if body['media'] else '<div class="missing">Final image not attached</div>'
                    cards.append('<article><h2>%s · revision %s</h2><span class="badge">%s</span><pre>%s</pre>%s<h3>Before publication</h3><ul>%s</ul><details><summary>Review fingerprint</summary><code>%s</code></details></article>' % (html.escape(d['id']),d['revision'],html.escape(d['status']),html.escape(body['commentary']),visual,''.join('<li>'+html.escape(x)+'</li>' for x in check['blockers']) or '<li>Ready for authenticated review</li>',check['payload_hash']))
                page = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ElectroFit publishing review</title><style>body{font:15px/1.55 system-ui,sans-serif;background:#f3f5f8;color:#172138;margin:0}main{max-width:760px;padding:28px 18px;margin:auto}h1{font-size:28px}article{background:white;border:1px solid #d9dfeb;padding:25px;border-radius:12px;margin:22px 0}h2{font-size:20px;margin-top:0}h3{font-size:15px}pre{white-space:pre-wrap;font:inherit}img{max-width:100%%;max-height:650px;display:block;margin:auto}.badge{background:#e7eef8;padding:5px 10px;border-radius:14px;font-size:12px}.missing{padding:25px;background:#f1f3f7;color:#566276}code{word-break:break-all}a{color:#0866bf}</style></head><body><main><h1>Publishing review</h1><p>Local drafts · LinkedIn access: %s · Live publishing: %s</p><p>Review the exact text and final media here. Approval is recorded separately in your terminal after reviewer authentication. No publication is scheduled.</p>%s</main></body></html>''' % (html.escape(status['api_access']),'enabled' if status['live_enabled'] else 'disabled',''.join(cards))
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Cache-Control','no-store')
                self.send_header('X-Content-Type-Options','nosniff')
                self.send_header('Content-Security-Policy',"default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
                self.end_headers(); self.wfile.write(page.encode('utf-8'))
            finally:
                p.db.close()
    HTTPServer(('127.0.0.1',port),Handler).serve_forever()

def interactive():
    if not sys.stdin.isatty():
        raise GuardError('Run this command yourself in an interactive terminal; do not supply credentials through agent tools.')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-dir',type=Path,default=DEFAULT_DATA)
    ap.add_argument('command',choices=['status','list','dry-run','serve','reviewer-setup','credentials-setup','oauth-start','oauth-complete','organizations','select-organization','approve','publish','import'])
    ap.add_argument('value',nargs='?')
    args=ap.parse_args(); p=Publisher(args.data_dir)
    try:
        cmd=args.command
        if cmd=='status': result=p.status()
        elif cmd=='list': result=p.list()
        elif cmd=='dry-run': result=p.dry_run(args.value)
        elif cmd=='serve': return review_server(args.data_dir)
        elif cmd=='import':
            body=json.loads(Path(args.value).read_text(encoding='utf-8-sig')); result=p.save_draft(**body)
        elif cmd=='reviewer-setup':
            interactive(); v=p.vault.read()
            if v.get('reviewer'): raise GuardError('Reviewer already enrolled; existing identity preserved.')
            name=input('Reviewer name: ').strip(); password=getpass.getpass('New review passphrase (at least 14 characters): ')
            if not name or len(password)<14 or password!=getpass.getpass('Repeat passphrase: '): raise GuardError('Enrollment did not match requirements.')
            salt=secrets.token_bytes(32); v['reviewer']={'name':name,'salt':salt.hex(),'hash':hashlib.pbkdf2_hmac('sha256',password.encode(),salt,600000).hex()}; v['approval_key']=secrets.token_hex(32); p.vault.save(v); result={'reviewer_enrolled':True}
        elif cmd=='credentials-setup':
            interactive(); v=p.vault.read(); v['client_id']=input('LinkedIn client ID: ').strip(); v['client_secret']=getpass.getpass('LinkedIn client secret: ')
            if not v['client_id'] or not v['client_secret']: raise GuardError('Both credentials are required.')
            v.pop('token',None); v.pop('oauth',None); p.vault.save(v); result={'credentials_saved':True}
        elif cmd=='oauth-start': result={'authorization_url':p.oauth_start()}
        elif cmd=='oauth-complete': interactive(); result=p.oauth_complete(getpass.getpass('Paste the complete HTTPS callback URL (hidden): '))
        elif cmd=='organizations': result=p.client().organizations()
        elif cmd=='select-organization':
            interactive(); org=args.value
            if org not in [x['urn'] for x in p.client().organizations()]: raise GuardError('Organization is not authorized.')
            if input('Confirm this is ElectroFit Systems by typing the full organization URN: ')!=org: raise GuardError('Selection cancelled.')
            c=p.config(); c['organization']=org; p.config_path.write_text(json.dumps(c,indent=2),encoding='utf-8'); result={'organization':org}
        elif cmd=='approve':
            interactive(); d=p.get(args.value); envelope=p.envelope(d); fingerprint=digest(envelope)
            print(json.dumps(envelope,ensure_ascii=False,indent=2)); print('Review the image in http://127.0.0.1:8787/ before approval.')
            if input('Type APPROVE '+fingerprint[:12]+': ')!='APPROVE '+fingerprint[:12]: raise GuardError('Approval cancelled.')
            result=p.approve(args.value,getpass.getpass('Review passphrase: '),fingerprint)
        elif cmd=='publish': result=p.publish(args.value)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except GuardError as exc:
        print(str(exc),file=sys.stderr); sys.exit(1)
    finally: p.db.close()

if __name__=='__main__': main()

