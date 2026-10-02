import base64
import json
import os
import tempfile
import unittest
import http.client
import threading
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from bridge import (Bridge, Dpapi, PENDING_TOOL, Rejected, RESOLVE_TOOL, STATUS_TOOL,
                    callback_target, public_addresses, handler_for)


SECRET = 'whsec_' + base64.b64encode(b'a' * 32).decode()


class TestVault:
    # Only injected by tests. Production storage exclusively uses Windows DPAPI.
    def seal(self, value):
        return json.dumps(value).encode()

    def open(self, value):
        return json.loads(value)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.directory.name, 'state.db')
        self.now = 1000
        self.deliveries = []
        self.status = 202
        self.bad_challenge = False
        self.bridge = self.open_bridge()
        self.params = {'name': 'myavatar.test.ready', 'arguments': {'queue': 'synthetic'},
                       'delivery': {'mode': 'webhook', 'url': 'https://callback.example/test', 'secret': SECRET}}
        self.payload = {'conversationId': 'TEST-chat', 'messageId': 'TEST-message'}

    def open_bridge(self):
        switch = os.path.join(self.directory.name, 'auto-reply.enabled')
        with open(switch, 'w', encoding='utf-8') as handle:
            handle.write('enabled\n')
        return Bridge(self.path, ['callback.example'], self.transport, TestVault(), lambda: self.now,
                      switch)

    def transport(self, url, headers, body):
        data = json.loads(body)
        if data.get('type') == 'verification':
            return 200, json.dumps({'challenge': 'wrong' if self.bad_challenge else data['challenge']}).encode()
        self.deliveries.append((headers, body))
        return self.status, b'{}'

    def tearDown(self):
        self.bridge.db.close()
        self.directory.cleanup()

    def test_no_subscription_never_delivers(self):
        self.assertEqual(self.bridge.ingest(self.payload)[0], 409)
        self.assertEqual(self.deliveries, [])

    def test_dedup_survives_restart(self):
        self.bridge.subscribe(self.params)
        self.assertEqual(self.bridge.ingest(self.payload)[0], 200)
        self.bridge.db.close()
        self.bridge = self.open_bridge()
        self.assertEqual(self.bridge.ingest(self.payload)[0], 200)
        self.assertEqual(len(self.deliveries), 1)

    def test_failed_verification_creates_no_subscription(self):
        self.bad_challenge = True
        with self.assertRaises(Rejected):
            self.bridge.subscribe(self.params)
        self.assertEqual(self.bridge.ingest(self.payload)[0], 409)
        attempt = self.bridge.db.execute(
            'SELECT callback_host,outcome FROM subscription_attempts ORDER BY requested DESC LIMIT 1'
        ).fetchone()
        self.assertEqual(attempt, ('callback.example', 'received'))

    def test_expiry_stops_delivery(self):
        self.params['ttlMs'] = 1000
        self.bridge.subscribe(self.params)
        self.now += 2
        self.assertEqual(self.bridge.ingest(self.payload)[0], 409)

    def test_unsubscribe_idempotent(self):
        self.bridge.subscribe(self.params)
        params = dict(self.params, delivery={'mode': 'webhook', 'url': self.params['delivery']['url']})
        self.bridge.rpc('events/unsubscribe', params)
        self.bridge.rpc('events/unsubscribe', params)
        self.assertEqual(self.bridge.ingest(self.payload)[0], 409)

    def test_no_real_identifiers_or_message_text(self):
        for payload in ({'conversationId': '19:real', 'messageId': '123'},
                        dict(self.payload, text='a message'), {}, []):
            with self.assertRaises(Rejected):
                self.bridge.ingest(payload)

    def test_retry_keeps_event_and_body_changes_signing_time(self):
        self.bridge.subscribe(self.params)
        self.status = 503
        self.bridge.ingest(self.payload)
        self.now += 60
        self.status = 202
        self.bridge.ingest(self.payload)
        first, second = self.deliveries
        self.assertEqual(first[1], second[1])
        self.assertEqual(first[0]['webhook-id'], second[0]['webhook-id'])
        self.assertNotEqual(first[0]['webhook-signature'], second[0]['webhook-signature'])

    def test_no_retry_after_410_or_413(self):
        self.bridge.subscribe(self.params)
        for code in (410, 413):
            self.status = code
            payload = dict(self.payload, messageId=f'TEST-{code}')
            self.bridge.ingest(payload)
            count = len(self.deliveries)
            self.bridge.ingest(payload)
            self.assertEqual(len(self.deliveries), count)

    def test_rotation_and_idempotent_subscription(self):
        original = self.bridge.subscribe(self.params)['id']
        self.params['delivery']['secret'] = 'whsec_' + base64.b64encode(b'b' * 32).decode()
        self.assertEqual(self.bridge.subscribe(self.params)['id'], original)
        self.bridge.ingest(self.payload)
        self.assertEqual(len(self.deliveries[-1][0]['webhook-signature'].split()), 2)

    def test_bad_callback_and_private_dns_blocked(self):
        for url in ('http://callback.example/x', 'https://evil.example/x',
                    'https://user:pass@callback.example/x', 'https://callback.example:8443/x'):
            with self.assertRaises(Rejected):
                callback_target(url, {'callback.example'})
        with patch('bridge.socket.getaddrinfo', return_value=[(2, 1, 6, '', ('127.0.0.1', 443))]):
            with self.assertRaises(Rejected):
                public_addresses('callback.example')

    def test_http_auth_isolation_discovery_and_ingress(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(self.bridge, 'm' * 32, 'i' * 32))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        def request(path, token, body):
            connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
            try:
                connection.request('POST', path, json.dumps(body), {'Authorization': 'Bearer ' + token})
                response = connection.getresponse()
                return response.status, json.loads(response.read())
            finally:
                connection.close()
        try:
            connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
            try:
                connection.request('GET', '/.well-known/oauth-protected-resource/mcp')
                response = connection.getresponse()
                self.assertEqual(response.status, 404)
                self.assertEqual(json.loads(response.read()), {'error': 'not_found'})
            finally:
                connection.close()
            rpc = {'jsonrpc': '2.0', 'id': 1, 'method': 'server/discover'}
            self.assertEqual(request('/mcp', 'i' * 32, rpc)[0], 401)
            code, result = request('/mcp', 'm' * 32, rpc)
            self.assertEqual(code, 200)
            self.assertIn('events', result['result']['capabilities'])
            tools = {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'}
            code, result = request('/mcp', 'm' * 32, tools)
            self.assertEqual(code, 200)
            self.assertEqual(result['result']['tools'][0]['name'], STATUS_TOOL)
            call = {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
                    'params': {'name': STATUS_TOOL, 'arguments': {}}}
            code, result = request('/mcp', 'm' * 32, call)
            self.assertEqual(code, 200)
            self.assertTrue(result['result']['structuredContent']['teamsEnabled'])
            self.assertEqual(request('/ingress/test', 'm' * 32, self.payload)[0], 401)
            self.assertEqual(request('/ingress/test', 'i' * 32, self.payload)[0], 409)
            self.assertEqual(request('/ingress/test', 'i' * 32, dict(self.payload, text='no'))[0], 400)
        finally:
            server.shutdown()
            worker.join()
            server.server_close()

    def test_resolve_verified_internal_event(self):
        conversation_key = 'TEST-TEAMS-CONVERSATION-' + 'a' * 64
        message_key = 'TEST-TEAMS-MESSAGE-' + 'b' * 64
        self.bridge.db.execute(
            'INSERT INTO teams_events VALUES (?,?,?,?,?)',
            (conversation_key, message_key, '19:internal@thread.v2', '12345', self.now),
        )
        self.bridge.db.commit()
        result = self.bridge.rpc('tools/call', {'name': RESOLVE_TOOL, 'arguments': {
            'conversationId': conversation_key, 'messageId': message_key}})
        self.assertEqual(result['structuredContent'], {
            'path': '/chats/19:internal@thread.v2/messages/12345',
            'verifiedInternal': True,
        })
        with self.assertRaises(Rejected):
            self.bridge.rpc('tools/call', {'name': RESOLVE_TOOL, 'arguments': {
                'conversationId': conversation_key, 'messageId': 'TEST-TEAMS-MESSAGE-' + 'c' * 64}})

    def test_pending_event_checks_switch_and_claims_once(self):
        self.now += 1
        self.bridge.db.execute(
            'INSERT INTO teams_events VALUES (?,?,?,?,?)',
            ('TEST-TEAMS-CONVERSATION-' + 'a' * 64,
             'TEST-TEAMS-MESSAGE-' + 'b' * 64,
             '19:internal@thread.v2', '12345', self.now),
        )
        self.bridge.db.commit()
        result = self.bridge.rpc('tools/call', {'name': PENDING_TOOL, 'arguments': {}})
        payload = json.loads(result['content'][0]['text'])
        self.assertTrue(payload['autoReplyEnabled'])
        self.assertFalse(payload['killSwitchEngaged'])
        self.assertFalse(payload['duplicate'])
        self.assertEqual(payload['claimState'], 'claimed')
        with self.assertRaises(Rejected):
            self.bridge.rpc('tools/call', {'name': PENDING_TOOL, 'arguments': {}})

    def test_pending_event_is_blocked_when_switch_is_off(self):
        os.remove(self.bridge.auto_reply_switch)
        with self.assertRaises(Rejected):
            self.bridge.rpc('tools/call', {'name': PENDING_TOOL, 'arguments': {}})

    def test_skill_catalog_and_resources(self):
        catalog = self.bridge.rpc('skills/list', {})
        self.assertEqual(catalog['nextCursor'], None)
        skill = catalog['skills'][0]
        self.assertEqual(skill['frontmatter']['name'], 'teams-auto-responder')
        self.assertEqual(self.bridge.rpc('skills/get', {'uri': skill['uri']})['skill'], skill)
        for resource in skill['resources']:
            result = self.bridge.rpc('resources/read', {'uri': resource['uri']})
            content = result['contents'][0]['text'].encode()
            self.assertEqual(resource['digest'], 'sha256:' + __import__('hashlib').sha256(content).hexdigest())

    def test_skill_digest_preserves_windows_line_endings(self):
        from pathlib import Path
        import bridge

        with tempfile.TemporaryDirectory() as directory:
            resource_path = Path(directory) / 'SKILL.md'
            original = '# Policy\r\nRisposta gi\u00e0 verificata.\r\n'.encode('utf-8')
            resource_path.write_bytes(original)
            uri = 'skill://my-avatar/teams-auto-responder/SKILL.md'
            with patch.dict(bridge.SKILL_URIS, {uri: resource_path}, clear=True):
                resource = self.bridge.rpc('skills/list', {})['skills'][0]['resources'][0]
                text = self.bridge.rpc('resources/read', {'uri': uri})['contents'][0]['text']
            self.assertEqual(text.encode('utf-8'), original)
            self.assertEqual(resource['digest'], 'sha256:' + __import__('hashlib').sha256(original).hexdigest())

    @unittest.skipUnless(os.name == 'nt', 'Windows-only secret protection')
    def test_dpapi_roundtrip(self):
        vault = Dpapi()
        encrypted = vault.seal({'current': SECRET})
        self.assertNotIn(SECRET.encode(), encrypted)
        self.assertEqual(vault.open(encrypted), {'current': SECRET})


if __name__ == '__main__':
    unittest.main()
