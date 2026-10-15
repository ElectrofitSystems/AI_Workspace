import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from marketing_runtime import authorized,worker_config,instructions,POLICY
from teams_service import Service,ROOT
import test_service_routing

class MarketingAccessTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads(POLICY.read_text(encoding='utf-8'))
        self.transport={'tenant_id':self.policy['tenant_id'],
                        'owner_id':self.policy['operations']['user_id'],
                        'owner_email':self.policy['operations']['email']}
    def test_verified_internal_peers_share_capabilities_without_name_allowlist(self):
        for email in ('francesco.lucherini@efitsys.com','collega@efitsys.com','ALTRO@EFITSYS.COM'):
            self.assertTrue(authorized({'peer_id':'verified-user','peer_email':email},self.transport))
    def test_external_missing_and_lookalike_domains_fail_closed(self):
        for email in ('guest@external.com','user@sub.efitsys.com','user@efitsys.com.evil',
                      'user@@efitsys.com','display <user@efitsys.com>',None,''):
            self.assertFalse(authorized({'peer_id':'id','peer_email':email},self.transport))
        self.assertFalse(authorized({'peer_email':'user@efitsys.com'},self.transport))
        self.assertFalse(authorized({'peer_id':'id','peer_email':'user@efitsys.com'},{}))
        self.assertFalse(authorized({'peer_id':'id','peer_email':'user@efitsys.com'},
                                   {**self.transport,'tenant_id':'other-tenant'}))
    def test_missing_or_disabled_policy_never_enables(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'policy.json'
            b={'peer_id':'id','peer_email':'user@efitsys.com'}
            self.assertFalse(authorized(b,self.transport,p))
            p.write_text(json.dumps({**self.policy,'enabled':False}),encoding='utf-8')
            self.assertFalse(authorized(b,self.transport,p))
    def test_profile_enables_artifacts_and_inherits_plugins_but_denies_private_data(self):
        c=worker_config(ROOT);name=c['default_permissions']
        self.assertTrue(c['features.apps']);self.assertTrue(c['features.plugins'])
        self.assertTrue(c['features.shell_tool']);self.assertTrue(c['skills.include_instructions'])
        self.assertNotIn('plugins',c);self.assertNotIn('mcp_servers',c)
        fs=c[f'permissions.{name}.filesystem']
        for folder in ('input','output','.local/maintenance/temporary'):
            self.assertEqual(fs[(ROOT/folder).as_posix()],'write')
        self.assertEqual(fs[(ROOT/'.local').as_posix()],'read')
        self.assertEqual(fs[(ROOT/'.local/operations-teams').as_posix()],'deny')
        self.assertEqual(fs[(ROOT.parent/'ERP EFS/output').as_posix()],'deny')
        self.assertNotIn((ROOT/'scripts').as_posix(),fs)
        self.assertIn('stesso ruolo',instructions(ROOT))

class MarketingRoutingTests(unittest.TestCase):
    def setup_service(self):
        s,r,restricted,store=test_service_routing.ResponseTests().service('Marketing, crea una presentazione',[])
        s.marketing_sessions={};s.worker_servers=[];s.executable='codex.exe'
        return s,r,restricted,store
    def test_authorized_uses_dedicated_session_and_reuses_within_chat(self):
        s,r,restricted,store=self.setup_service()
        capable=Mock();capable.start_thread.return_value='marketing-thread'
        capable.answer.return_value=restricted.answer.return_value
        with patch('teams_service.erp_context',return_value=({'financial_access':False},False)), \
             patch('teams_service.marketing_authorized',return_value=True), \
             patch('teams_service.AppServer',return_value=capable) as factory:
            s.respond(r,restricted,'restricted-thread',store)
            s.respond(r,restricted,'restricted-thread',store)
        factory.assert_called_once();capable.start_thread.assert_called_once()
        self.assertEqual(capable.answer.call_count,2);restricted.answer.assert_not_called()
        self.assertEqual(s.marketing_sessions['chat'],(capable,'marketing-thread'))
    def test_erp_never_routes_into_capable_marketing_session(self):
        s,r,restricted,store=self.setup_service();r['content']='Mostrami le fatture fornitori'
        with patch('teams_service.erp_context',return_value=({'financial_access':False},False)), \
             patch('teams_service.marketing_authorized',return_value=True), \
             patch('teams_service.AppServer') as factory:
            s.respond(r,restricted,'restricted-thread',store)
        factory.assert_not_called();self.assertEqual(s.marketing_sessions,{})
    def test_unprivileged_peer_keeps_existing_readonly_session(self):
        s,r,restricted,store=self.setup_service()
        with patch('teams_service.erp_context',return_value=({'financial_access':False},False)), \
             patch('teams_service.marketing_authorized',return_value=False), \
             patch('teams_service.AppServer') as factory:
            s.respond(r,restricted,'restricted-thread',store)
        factory.assert_not_called();restricted.answer.assert_called_once()
    def test_failed_start_closes_process_and_does_not_cache(self):
        s,r,restricted,store=self.setup_service();capable=Mock()
        capable.start_thread.side_effect=RuntimeError('startup failed')
        with patch('teams_service.erp_context',return_value=({'financial_access':False},False)), \
             patch('teams_service.marketing_authorized',return_value=True), \
             patch('teams_service.AppServer',return_value=capable),self.assertRaises(RuntimeError):
            s.respond(r,restricted,'restricted-thread',store)
        capable.close.assert_called_once();self.assertEqual(s.marketing_sessions,{})

if __name__=='__main__':unittest.main()
