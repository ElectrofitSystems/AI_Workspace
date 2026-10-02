"""Local MCP Events protocol spike. Synthetic events only; not production MCP hosting.

No model calls, background polling, automatic startup, or Teams access.
Run --serve after supplying two distinct bearer tokens via environment.
Callback host allowlist is empty by default. Do not deploy publicly as-is:
ChatGPT authentication/transport compatibility must first be tested.
"""
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

EVENT = 'myavatar.test.ready'
OWNER = 'matteo.ravera@efitsys.com'
LIMIT = 16384
STATUS_TOOL = 'get_myavatar_status'
RESOLVE_TOOL = 'resolve_internal_teams_event'
PENDING_TOOL = 'get_pending_internal_teams_message'
AUTO_REPLY_SWITCH = Path(__file__).resolve().parents[2] / 'config' / 'teams-auto-reply.enabled'
SKILL_NAME = 'teams-auto-responder'
SKILL_DESCRIPTION = ('Gestisce un messaggio Teams interno che ha risvegliato la chat, recupera il '
                     'messaggio esatto, applica la policy aziendale e risponde automaticamente solo '
                     'alle richieste semplici e sicure; altrimenti avvisa Matteo con motivo e bozza. '
                     'Non usare per chat esterne, miste o non verificate.')
SKILL_ROOT = Path(__file__).resolve().parents[2] / 'skills' / SKILL_NAME
SKILL_URIS = {
    f'skill://my-avatar/{SKILL_NAME}/SKILL.md': SKILL_ROOT / 'SKILL.md',
    f'skill://my-avatar/{SKILL_NAME}/references/policy.md': SKILL_ROOT / 'references' / 'policy.md',
}


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


class Rejected(Exception):
    pass


class Dpapi:
    """Encrypt callback secrets with the current Windows user's DPAPI key."""
    class Blob(ctypes.Structure):
        _fields_ = [('size', ctypes.c_ulong), ('data', ctypes.POINTER(ctypes.c_ubyte))]

    def transform(self, value, protect):
        if os.name != 'nt':
            raise Rejected('Windows DPAPI required')
        buf = ctypes.create_string_buffer(value)
        source = self.Blob(len(value), ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)))
        target = self.Blob()
        api = ctypes.windll.crypt32
        fn = api.CryptProtectData if protect else api.CryptUnprotectData
        if not fn(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
            raise Rejected('Secret protection failed')
        try:
            return ctypes.string_at(target.data, target.size)
        finally:
            ctypes.windll.kernel32.LocalFree(ctypes.cast(target.data, ctypes.c_void_p))

    def seal(self, value):
        return self.transform(encode(value), True)

    def open(self, value):
        return json.loads(self.transform(value, False))


def signing_key(secret):
    try:
        if not isinstance(secret, str) or not secret.startswith('whsec_'):
            raise ValueError()
        key = base64.b64decode(secret[6:], validate=True)
        if not 24 <= len(key) <= 64:
            raise ValueError()
        return key
    except (ValueError, TypeError):
        raise Rejected('Invalid signing secret') from None


def signed_headers(keys, event_id, body, subscription_id, now):
    stamp = str(int(now))
    message = event_id.encode() + b'.' + stamp.encode() + b'.' + body
    signatures = ['v1,' + base64.b64encode(hmac.digest(signing_key(k), message, 'sha256')).decode()
                  for k in keys]
    return {'Content-Type': 'application/json', 'webhook-id': event_id,
            'webhook-timestamp': stamp, 'webhook-signature': ' '.join(signatures),
            'X-MCP-Subscription-Id': subscription_id}


def callback_target(url, allowed_hosts):
    try:
        parts = urlsplit(url)
        if (parts.scheme != 'https' or parts.username or parts.password or parts.fragment
                or parts.port not in (None, 443) or parts.hostname not in allowed_hosts):
            raise ValueError()
        return parts
    except (ValueError, TypeError):
        raise Rejected('Callback host not approved or invalid URL') from None


def public_addresses(host):
    addresses = {item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
    if not addresses or any(not ipaddress.ip_address(x).is_global for x in addresses):
        raise Rejected('Callback resolved to a non-public address')
    return sorted(addresses)


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, address):
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
    def __init__(self, allowed_hosts):
        self.allowed_hosts = allowed_hosts

    def __call__(self, url, headers, body):
        parts = callback_target(url, self.allowed_hosts)
        # Resolve on each connection; pin the checked address and preserve TLS hostname.
        addresses = public_addresses(parts.hostname)
        connection = PinnedHTTPS(parts.hostname, addresses[0])
        try:
            path = parts.path or '/'
            if parts.query:
                path += '?' + parts.query
            connection.request('POST', path, body, headers)
            response = connection.getresponse()
            result = response.read(LIMIT + 1)
            if len(result) > LIMIT:
                raise Rejected('Callback response too large')
            # No redirect following. Status alone never proves ChatGPT ran a task.
            return response.status, result
        finally:
            connection.close()


class Bridge:
    def __init__(self, database, allowed_hosts=(), transport=None, vault=None, clock=time.time,
                 auto_reply_switch=AUTO_REPLY_SWITCH):
        self.db = sqlite3.connect(database, check_same_thread=False)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS subscriptions
            (id TEXT PRIMARY KEY, url TEXT NOT NULL, expires REAL NOT NULL, secret BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS deliveries
            (subscription TEXT, event TEXT, payload BLOB NOT NULL, status TEXT NOT NULL,
             attempts INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(subscription,event));
          CREATE TABLE IF NOT EXISTS subscription_attempts
            (requested REAL NOT NULL, callback_host TEXT NOT NULL, outcome TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS teams_events
            (conversation_key TEXT NOT NULL, message_key TEXT NOT NULL,
             conversation_id TEXT NOT NULL, message_id TEXT NOT NULL,
             created REAL NOT NULL, PRIMARY KEY(conversation_key,message_key));
          CREATE TABLE IF NOT EXISTS teams_reply_claims
            (conversation_id TEXT NOT NULL, message_id TEXT NOT NULL,
             claimed REAL NOT NULL, state TEXT NOT NULL,
             PRIMARY KEY(conversation_id,message_id));
        ''')
        self.db.commit()
        self.hosts = set(allowed_hosts)
        self.transport = transport or CallbackTransport(self.hosts)
        self.vault = vault or Dpapi()
        self.clock = clock
        self.started = clock()
        self.auto_reply_switch = Path(auto_reply_switch)
        self.lock = threading.RLock()

    def identity(self, params):
        if params.get('name') != EVENT or params.get('arguments') != {'queue': 'synthetic'}:
            raise Rejected('Only the synthetic queue is enabled')
        delivery = params.get('delivery', {})
        if delivery.get('mode') != 'webhook':
            raise Rejected('Webhook delivery required')
        url = delivery.get('url')
        callback_target(url, self.hosts)
        identity = encode([OWNER, url, EVENT, {'queue': 'synthetic'}])
        return 'sub_' + hashlib.sha256(identity).hexdigest(), url

    def subscribe(self, params):
        with self.lock:
            # Retain only a sanitized hostname to diagnose and build the callback
            # allowlist. Never store the callback path, query, secret, or payload.
            candidate = params.get('delivery', {}).get('url')
            try:
                parts = urlsplit(candidate)
                host = parts.hostname.lower() if parts.scheme == 'https' and parts.hostname else 'invalid'
            except (ValueError, TypeError, AttributeError):
                host = 'invalid'
            self.db.execute('INSERT INTO subscription_attempts VALUES (?,?,?)',
                            (self.clock(), host, 'received'))
            self.db.commit()
            sid, url = self.identity(params)
            secret = params['delivery'].get('secret')
            signing_key(secret)
            ttl = params.get('ttlMs', 3600000)
            if ttl is None:
                ttl = 3600000  # This prototype grants only finite subscriptions.
            if isinstance(ttl, bool) or not isinstance(ttl, (int, float)) or ttl <= 0:
                raise Rejected('Invalid subscription lifetime')
            if params.get('cursor') is not None:
                raise Rejected('Replay cursors are not supported')
            now = self.clock()
            challenge = secrets.token_urlsafe(32)
            body = encode({'type': 'verification', 'challenge': challenge})
            headers = signed_headers([secret], 'verify_' + secrets.token_hex(16), body, sid, now)
            status, response = self.transport(url, headers, body)
            try:
                echoed = json.loads(response).get('challenge', '')
                verified = isinstance(echoed, str) and hmac.compare_digest(challenge, echoed)
            except (ValueError, AttributeError):
                verified = False
            if not 200 <= status < 300 or not verified:
                raise Rejected('Callback verification failed')
            keys = {'current': secret, 'previous': None, 'rotateUntil': 0}
            old = self.db.execute('SELECT secret FROM subscriptions WHERE id=?', (sid,)).fetchone()
            if old:
                previous = self.vault.open(old[0])
                if previous['current'] != secret:
                    keys.update(previous=previous['current'], rotateUntil=now + 300)
                else:
                    keys = previous
            expires = now + min(ttl / 1000, 86400)
            self.db.execute('INSERT OR REPLACE INTO subscriptions VALUES (?,?,?,?)',
                            (sid, url, expires, self.vault.seal(keys)))
            self.db.commit()
            return {'id': sid, 'refreshBefore': datetime.fromtimestamp(expires, timezone.utc).isoformat(),
                    'cursor': None, 'truncated': False}

    def rpc(self, method, params):
        if method == 'server/discover':
            return {'resultType': 'complete', 'supportedVersions': ['2026-07-28'],
                    'capabilities': {'tools': {'listChanged': False}, 'events': {},
                        'extensions': {'io.modelcontextprotocol/skills': {}}}}
        if method in ('skills/list', 'skills/get'):
            if method == 'skills/list' and params not in ({}, None):
                raise Rejected('Skill pagination is not supported')
            catalog_uri = f'skill://my-avatar/{SKILL_NAME}/SKILL.md'
            if method == 'skills/get' and params != {'uri': catalog_uri}:
                raise Rejected('Unknown skill')
            resources = []
            for uri, path in SKILL_URIS.items():
                content = path.read_bytes()
                resources.append({'uri': uri, 'digest': 'sha256:' + hashlib.sha256(content).hexdigest()})
            skill = {'uri': catalog_uri,
                     'frontmatter': {'name': SKILL_NAME, 'description': SKILL_DESCRIPTION},
                     'resources': resources}
            return {'skill': skill} if method == 'skills/get' else {'skills': [skill], 'nextCursor': None}
        if method == 'resources/read':
            if not isinstance(params, dict) or set(params) != {'uri'} or params['uri'] not in SKILL_URIS:
                raise Rejected('Unknown skill resource')
            uri = params['uri']
            return {'contents': [{'uri': uri, 'mimeType': 'text/markdown',
                                  # Preserve the exact bytes hashed in skills/list,
                                  # including CRLF line endings on Windows.
                                  'text': SKILL_URIS[uri].read_bytes().decode('utf-8')}]}
        if method == 'tools/list':
            return {'tools': [{
                'name': STATUS_TOOL,
                'title': 'Get My Avatar bridge status',
                'description': ('Check whether the My Avatar bridge is ready for verified internal Teams '
                                'events. Returns no Teams message content.'),
                'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False},
                'outputSchema': {'type': 'object', 'properties': {
                    'status': {'type': 'string'},
                    'event': {'type': 'string'},
                    'queue': {'type': 'string'},
                    'teamsEnabled': {'type': 'boolean'}},
                    'required': ['status', 'event', 'queue', 'teamsEnabled'],
                    'additionalProperties': False},
                'annotations': {'readOnlyHint': True, 'openWorldHint': False,
                                'destructiveHint': False, 'idempotentHint': True}
            }, {
                'name': RESOLVE_TOOL,
                'title': 'Resolve a verified internal Teams event',
                'description': ('Resolve the opaque identifiers from a verified internal Teams wake event '
                                'to the exact Microsoft Teams message path. Returns no message content.'),
                'inputSchema': {'type': 'object', 'properties': {
                    'conversationId': {'type': 'string', 'minLength': 20, 'maxLength': 120},
                    'messageId': {'type': 'string', 'minLength': 20, 'maxLength': 120}},
                    'required': ['conversationId', 'messageId'], 'additionalProperties': False},
                'annotations': {'readOnlyHint': True, 'openWorldHint': False,
                                'destructiveHint': False, 'idempotentHint': True}
            }, {
                'name': PENDING_TOOL,
                'title': 'Get the latest verified internal Teams message',
                'description': ('Return the exact Microsoft Teams message path for the latest event already '
                                'verified as internal by the EFitsys ingestion flow. Atomically checks the '
                                'auto-reply kill switch and claims the event so it cannot be processed twice. '
                                'Returns no message content.'),
                'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False},
                'annotations': {'readOnlyHint': True, 'openWorldHint': False,
                                'destructiveHint': False, 'idempotentHint': True}
            }]}
        if method == 'tools/call':
            name = params.get('name')
            arguments = params.get('arguments', {})
            if name == STATUS_TOOL and arguments == {}:
                status = {'status': 'internal_teams_ready', 'event': EVENT,
                          'queue': 'verified_internal', 'teamsEnabled': True}
                return {'structuredContent': status,
                        'content': [{'type': 'text', 'text':
                            'My Avatar bridge is ready for verified internal Teams events.'}]}
            if name == RESOLVE_TOOL:
                if not isinstance(arguments, dict):
                    raise Rejected('Invalid event reference')
                conversation = arguments.get('conversationId', arguments.get('conversation_id'))
                message = arguments.get('messageId', arguments.get('message_id'))
                keys = tuple(value.strip() if isinstance(value, str) else value
                             for value in (conversation, message))
                if (not all(isinstance(value, str) and 20 <= len(value) <= 120
                            and any(ord(character) < 32 for character in value) is False
                            for value in keys)):
                    raise Rejected('Invalid event reference')
                row = self.db.execute(
                    'SELECT conversation_id,message_id FROM teams_events '
                    'WHERE conversation_key=? AND message_key=?', keys).fetchone()
                if not row:
                    raise Rejected('Unknown or unverified Teams event')
                path = f'/chats/{row[0]}/messages/{row[1]}'
                result = {'path': path, 'verifiedInternal': True}
                return {'structuredContent': result,
                        'content': [{'type': 'text', 'text':
                            'Verified internal Teams message reference resolved.'}]}
            if name == PENDING_TOOL and arguments == {}:
                with self.lock:
                    if not self.auto_reply_switch.is_file():
                        raise Rejected('Automatic Teams replies are disabled by the kill switch')
                    row = self.db.execute(
                        'SELECT e.conversation_id,e.message_id FROM teams_events e '
                        'LEFT JOIN teams_reply_claims c '
                        'ON c.conversation_id=e.conversation_id AND c.message_id=e.message_id '
                        'WHERE c.conversation_id IS NULL AND e.created>=? '
                        'ORDER BY e.created DESC LIMIT 1', (self.started,)).fetchone()
                    if not row:
                        raise Rejected('No unclaimed verified internal Teams event is available')
                    self.db.execute(
                        'INSERT INTO teams_reply_claims VALUES (?,?,?,?)',
                        (row[0], row[1], self.clock(), 'claimed'))
                    self.db.commit()
                path = f'/chats/{row[0]}/messages/{row[1]}'
                return {'content': [{'type': 'text', 'text': json.dumps({
                    'path': path, 'verifiedInternal': True, 'autoReplyEnabled': True,
                    'killSwitchEngaged': False,
                    'duplicate': False, 'claimState': 'claimed'}, separators=(',', ':'))}]}
            raise Rejected('Unknown tool or invalid arguments')
        if method == 'events/list':
            return {'events': [{'name': EVENT, 'description': ('Verified internal Teams wake event. The payload '
                                                               'contains opaque references only, never message content.'),
                'delivery': ['webhook'],
                'inputSchema': {'type': 'object', 'properties': {'queue': {'const': 'verified_internal', 'type': 'string'}},
                                'required': ['queue'], 'additionalProperties': False},
                'payloadSchema': {'type': 'object', 'properties': {
                    'queue': {'const': 'verified_internal', 'type': 'string'},
                    'conversationId': {'type': 'string', 'pattern': '^TEST-TEAMS-CONVERSATION-'},
                    'messageId': {'type': 'string', 'pattern': '^TEST-TEAMS-MESSAGE-'}},
                    'required': ['queue', 'conversationId', 'messageId'], 'additionalProperties': False}}]}
        if method == 'events/subscribe':
            return self.subscribe(params)
        if method == 'events/unsubscribe':
            with self.lock:
                sid, _ = self.identity(params)
                self.db.execute('DELETE FROM subscriptions WHERE id=?', (sid,))
                self.db.commit()
                return {}
        raise Rejected('Unsupported method in protocol prototype')

    def ingest(self, payload):
        if (not isinstance(payload, dict) or set(payload) != {'conversationId', 'messageId'}
            or any(not isinstance(x, str) or not x.startswith('TEST-') or not 6 <= len(x) <= 120
                   or any(ord(c) < 32 for c in x) for x in payload.values())):
            raise Rejected('Only TEST- identifiers are accepted; message text is forbidden')
        with self.lock:
            now = self.clock()
            subscriptions = self.db.execute('SELECT id,url,secret FROM subscriptions WHERE expires>?', (now,)).fetchall()
            if not subscriptions:
                return 409, {'state': 'NO_ACTIVE_SUBSCRIPTION', 'chatgptWakeVerified': False}
            eid = 'evt_' + hashlib.sha256(encode(payload)).hexdigest()
            body = encode({'eventId': eid, 'name': EVENT,
                           'timestamp': datetime.fromtimestamp(now, timezone.utc).isoformat(),
                           'data': dict(payload, queue='verified_internal'), 'cursor': None})
            outcomes = []
            for sid, url, encrypted in subscriptions:
                self.db.execute('INSERT OR IGNORE INTO deliveries VALUES (?,?,?,?,0)', (sid, eid, body, 'pending'))
                record = self.db.execute('SELECT payload,status,attempts FROM deliveries WHERE subscription=? AND event=?', (sid, eid)).fetchone()
                if record[1] in ('accepted', 'permanent_failure') or record[2] >= 3:
                    outcomes.append(record[1] if record[2] < 3 or record[1] == 'accepted' else 'attempt_limit')
                    continue
                # Persist attempt before IO: crash may require reconciliation, never unbounded resend.
                self.db.execute('UPDATE deliveries SET attempts=attempts+1 WHERE subscription=? AND event=?', (sid, eid))
                self.db.commit()
                keys = self.vault.open(encrypted)
                signing = [keys['current']]
                if keys.get('previous') and keys['rotateUntil'] > now:
                    signing.append(keys['previous'])
                headers = signed_headers(signing, eid, record[0], sid, now)
                try:
                    code, _ = self.transport(url, headers, record[0])
                    state = ('accepted' if 200 <= code < 300 else
                             'retryable' if code in (408, 429) or code >= 500 else 'permanent_failure')
                except (OSError, Rejected, http.client.HTTPException):
                    state = 'retryable'
                self.db.execute('UPDATE deliveries SET status=? WHERE subscription=? AND event=?', (state, sid, eid))
                self.db.commit()
                outcomes.append(state)
            result = {'eventId': eid, 'deliveries': outcomes, 'chatgptWakeVerified': False}
            return (200 if all(s == 'accepted' for s in outcomes) else 503), result


def handler_for(bridge, mcp_token, ingress_token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Never log bearer tokens, callback URLs, secrets or payloads.

        def reply(self, code, value):
            body = encode(value)
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            # This prototype deliberately has no OAuth/PRMD metadata. Returning
            # a JSON 404 lets tunnel-client distinguish that from a malformed
            # metadata endpoint (BaseHTTPRequestHandler otherwise emits HTML).
            self.reply(404, {'error': 'not_found'})

        def do_POST(self):
            expected = {'/mcp': mcp_token, '/ingress/test': ingress_token}.get(self.path)
            if not expected:
                return self.reply(404, {'error': 'not_found'})
            if self.headers.get('Origin'):
                return self.reply(403, {'error': 'browser_origin_not_allowed'})
            if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + expected):
                return self.reply(401, {'error': 'unauthorized'})
            rid = None
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= LIMIT:
                    return self.reply(413, {'error': 'invalid_size'})
                self.connection.settimeout(10)
                payload = json.loads(self.rfile.read(length))
                if self.path == '/ingress/test':
                    code, result = bridge.ingest(payload)
                    return self.reply(code, result)
                if not isinstance(payload, dict) or payload.get('jsonrpc') != '2.0':
                    raise Rejected('JSON-RPC object required')
                rid = payload.get('id')
                result = bridge.rpc(payload.get('method'), payload.get('params', {}))
                self.reply(200, {'jsonrpc': '2.0', 'id': rid, 'result': result})
            except (Rejected, ValueError, TypeError, KeyError, AttributeError) as error:
                try:
                    params = payload.get('params', {}) if isinstance(payload, dict) else {}
                    arguments = params.get('arguments', {}) if isinstance(params, dict) else {}
                    summary = {
                        'time': datetime.now(timezone.utc).isoformat(),
                        'method': payload.get('method') if isinstance(payload, dict) else None,
                        'name': params.get('name') if isinstance(params, dict) else None,
                        'argumentKeys': sorted(arguments) if isinstance(arguments, dict) else [],
                        'argumentLengths': ({key: len(value) if isinstance(value, str) else None
                                             for key, value in arguments.items()}
                                            if isinstance(arguments, dict) else {}),
                        'reason': str(error),
                    }
                    audit = Path(os.environ['LOCALAPPDATA']) / 'MyAvatarMcpEvents' / 'rejections.jsonl'
                    with audit.open('a', encoding='utf-8') as handle:
                        handle.write(json.dumps(summary, separators=(',', ':')) + '\n')
                except Exception:
                    pass
                self.reply(400, {'jsonrpc': '2.0', 'id': rid,
                                 'error': {'code': -32602, 'message': 'Request rejected; check synthetic identifiers, callback and parameters'}})
            except Exception:
                self.reply(503, {'error': 'bridge_unavailable'})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve', action='store_true')
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    if not args.serve:
        parser.print_help()
        return
    mcp = os.environ.get('MYAVATAR_MCP_TOKEN', '')
    ingress = os.environ.get('MYAVATAR_INGRESS_TOKEN', '')
    if len(mcp) < 32 or len(ingress) < 32 or mcp == ingress:
        parser.error('Two distinct tokens of at least 32 characters are required in environment')
    directory = Path(os.environ['LOCALAPPDATA']) / 'MyAvatarMcpEvents'
    directory.mkdir(exist_ok=True)
    hosts = {h.strip().lower() for h in os.environ.get('MYAVATAR_CALLBACK_HOSTS', '').split(',') if h.strip()}
    bridge = Bridge(directory / 'test-state.sqlite3', hosts)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(bridge, mcp, ingress))
    print(f'Synthetic-only bridge on 127.0.0.1:{args.port}; no ChatGPT subscription verified.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        bridge.db.close()


if __name__ == '__main__':
    main()
