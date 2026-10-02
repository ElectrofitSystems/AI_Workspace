import copy
import hashlib
import json
from pathlib import Path
import secrets
import tempfile
import unittest
from unittest.mock import patch
from publisher import Publisher, GuardError, digest, protect
from mcp_server import handle

class MemoryVault:
    def __init__(self): self.value={}
    def read(self): return copy.deepcopy(self.value)
    def save(self,value): self.value=copy.deepcopy(value)

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name); self.v=MemoryVault(); self.p=Publisher(self.root,self.v)
        self.image=self.root/'test.png'; self.image.write_bytes(b'\x89PNG\r\n\x1a\nfixture')
        self.password='reviewer testing passphrase'; salt=secrets.token_bytes(32)
        self.v.save({'reviewer':{'name':'Test reviewer','salt':salt.hex(),'hash':hashlib.pbkdf2_hmac('sha256',self.password.encode(),salt,600000).hex()},'approval_key':secrets.token_hex(32)})
    def tearDown(self): self.p.db.close(); self.temp.cleanup()
    def configured(self,live=False):
        c=self.p.config(); c.update(organization='urn:li:organization:123',live_enabled=live,api_access='approved'); self.p.config_path.write_text(json.dumps(c))
    def draft(self): return self.p.save_draft('EFS-TEST','EN\nExample\nIT\nEsempio',str(self.image), 'Test image')
    def approve(self): return self.p.approve('EFS-TEST',self.password,digest(self.p.envelope(self.p.get('EFS-TEST'))))
    def test_default_no_network(self):
        self.draft()
        with patch('publisher.LinkedIn.send',side_effect=AssertionError('network forbidden')):
            self.assertEqual(self.p.dry_run('EFS-TEST')['network_calls'],0)
            with self.assertRaises(GuardError): self.p.publish('EFS-TEST')
            with self.assertRaises(GuardError): self.p.oauth_start()
    def test_edit_invalidates_approval(self):
        self.configured(); self.draft(); self.approve()
        self.p.save_draft('EFS-TEST','Changed',str(self.image),expected_revision=1)
        self.assertEqual(self.p.get('EFS-TEST')['status'],'needs_review'); self.assertIsNone(self.p.get('EFS-TEST')['approval'])
    def test_revision_race(self):
        self.draft()
        with self.assertRaises(GuardError): self.p.save_draft('EFS-TEST','Stale',expected_revision=0)
    def test_password_and_hash_required(self):
        self.configured(); self.draft()
        with self.assertRaises(GuardError): self.p.approve('EFS-TEST','wrong','anything')
        with self.assertRaises(GuardError): self.p.approve('EFS-TEST',self.password,'outdated')
    def test_missing_image_blocks(self):
        self.configured(); self.p.save_draft('EFS-TEST','Draft')
        self.assertFalse(self.p.dry_run('EFS-TEST')['ready_for_review'])
        with self.assertRaises(GuardError): self.approve()
    def test_media_mutation_blocks(self):
        self.configured(); d=self.draft(); self.approve()
        (self.root/'media'/d['body']['media']['file']).write_bytes(b'changed')
        self.assertFalse(self.p.dry_run('EFS-TEST')['ready_for_review'])
    def test_dry_approval_not_live(self):
        self.configured(); self.draft(); self.approve(); self.configured(True)
        with patch.object(self.p,'client',return_value=object()):
            with self.assertRaises(GuardError): self.p.publish('EFS-TEST')
    def test_post_timeout_never_retries(self):
        self.configured(True); self.draft(); self.approve()
        class Client:
            calls=0
            def organizations(self): return [{'urn':'urn:li:organization:123'}]
            def upload(self,*args): return 'urn:li:image:fake'
            def request(self,*args): self.calls+=1; raise TimeoutError()
        c=Client()
        with patch.object(self.p,'client',return_value=c):
            with self.assertRaises(GuardError): self.p.publish('EFS-TEST')
            with self.assertRaises(GuardError): self.p.publish('EFS-TEST')
        self.assertEqual(c.calls,1); self.assertEqual(self.p.get('EFS-TEST')['status'],'outcome_unknown')
    def test_success_duplicate_guard(self):
        self.configured(True); self.draft(); self.approve()
        class Client:
            calls=0
            def organizations(self): return [{'urn':'urn:li:organization:123'}]
            def upload(self,*args): return 'urn:li:image:fake'
            def request(self,*args): self.calls+=1; return {},{'x-restli-id':'urn:li:share:42'}
        c=Client()
        with patch.object(self.p,'client',return_value=c):
            self.assertEqual(self.p.publish('EFS-TEST')['status'],'published')
            self.assertTrue(self.p.publish('EFS-TEST')['duplicate_prevented'])
        self.assertEqual(c.calls,1)
    def test_oauth_state_consumed(self):
        self.v.save({'oauth':{'state':'correct','expires_at':9999999999,'redirect_uri':'https://example.com/callback'}})
        with patch('publisher.LinkedIn.send',side_effect=AssertionError('network forbidden')):
            with self.assertRaises(GuardError): self.p.oauth_complete('https://example.com/callback?state=wrong&code=abc')
        self.assertNotIn('oauth',self.v.read())
    def test_mcp_has_no_approval_or_secret_tool(self):
        result=handle({'method':'tools/list'},self.p)
        self.assertEqual(len(result['tools']),6)
        self.assertNotIn('approve',[x['name'] for x in result['tools']])
        self.assertEqual(handle({'method':'initialize','params':{'protocolVersion':'2024-11-05'}},self.p)['protocolVersion'],'2024-11-05')
    def test_dpapi_roundtrip(self):
        import os
        if os.name!='nt': self.skipTest('Windows only')
        ciphertext=protect(b'test credential')
        self.assertNotIn(b'test credential',ciphertext)
        self.assertEqual(protect(ciphertext,True),b'test credential')

if __name__=='__main__': unittest.main()
