import json
import tempfile
import time
import unittest
from pathlib import Path
from appserver import AppServer, RateLimited

class RateLimitTests(unittest.TestCase):
    def test_shared_cooldown_blocks_request_until_retry_after(self):
        with tempfile.TemporaryDirectory() as directory:
            client=AppServer.__new__(AppServer)
            client.cooldown=Path(directory)/'cooldown.json'
            calls=[]
            def request(*args):
                calls.append(args)
                return {'isError':True,'structuredContent':{'error_code':'RATE_LIMITED',
                    'retry_after_seconds':62},'content':[]}
            client.request=request
            with self.assertRaises(RateLimited) as raised:client.tool('t','get_profile',{})
            self.assertGreaterEqual(raised.exception.retry_after,62)
            with self.assertRaises(RateLimited):client.tool('t','list_chats',{})
            self.assertEqual(len(calls),1)
            self.assertGreater(json.loads(client.cooldown.read_text())['until'],time.time()+60)
    def test_no_network_after_other_process_reports_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            client=AppServer.__new__(AppServer)
            client.cooldown=Path(directory)/'cooldown.json'
            client.cooldown.write_text(json.dumps({'until':time.time()+90}))
            def forbidden(*args):self.fail('No request may be sent during cooldown')
            client.request=forbidden
            with self.assertRaises(RateLimited):client.tool('t','get_profile',{})

if __name__=='__main__':unittest.main()
