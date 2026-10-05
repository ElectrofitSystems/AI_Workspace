import sys
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'Marketing EFS/scripts/operations'))
from teams_service import Service
from erp_teams import AccessDenied
from teams_state import GuardError


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.service=Service.__new__(Service)
        self.service.config={'owner_id':'owner','activated_at':'2026-10-05T00:00:00Z'}
        self.service.chats={'chat':{'id':'chat'}}
        self.service.token='test'
        self.service.transport='test-transport'
        self.service.live=False
        self.service.log=Mock()
        self.binding={'peer_id':'reader','peer_email':'reader@example.test'}
        self.service.identity=Mock(return_value={'binding':self.binding})
        self.request={'chat_id':'chat','message_id':'message','peer_id':'reader',
                      'peer_email':'reader@example.test','content':'ERP fatture da pagare',
                      'created_at':'2026-10-05T11:00:00Z','has_attachments':False}
        historical={'chat_id':'chat','author_user_id':'owner','message_type':'message',
                    'created_at':'2026-10-05T10:00:00Z','content':'Fatture: vecchio importo privato'}
        self.service.server=Mock()
        self.service.server.tool.side_effect=[{'messages':[historical]},
                                             {'messages':[{'message_id':'message'}]}]
        self.agent=Mock()
        self.agent.start_thread.return_value='new-financial-session'
        self.agent.answer.return_value={'agent':'Agente ERP EFS','response':'valid response',
                                         'delegated_roles':['Agente ERP EFS'],'elapsed_seconds':1}
        self.store=Mock()
        self.available={'financial_access':True,'status':'available_snapshot',
                        'data':{'acquired_at':'time','source':{'sha256':'hash'}}}

    def test_denial_is_deterministic_and_never_calls_model(self):
        with patch('teams_service.erp_context',return_value=({'financial_access':False,'status':'access_denied'},False)):
            self.service.respond(self.request,self.agent,'old-session',self.store)
        self.agent.answer.assert_not_called()
        self.store.prepare.assert_not_called()

    def test_financial_session_is_fresh_and_omits_previous_amounts(self):
        with patch('teams_service.erp_context',return_value=(self.available,True)), patch('teams_service.assert_delivery'):
            self.service.respond(self.request,self.agent,'old-session',self.store)
        thread,prompt=self.agent.answer.call_args.args
        self.assertEqual(thread,'new-financial-session')
        self.assertNotIn('vecchio importo privato',prompt)
        self.store.prepare.assert_not_called()

    def test_revocation_after_model_blocks_delivery(self):
        self.service.live=True
        with patch('teams_service.erp_context',return_value=(self.available,True)), \
             patch('teams_service.assert_delivery',side_effect=AccessDenied('revoked')):
            with self.assertRaises(AccessDenied):
                self.service.respond(self.request,self.agent,'old-session',self.store)
        self.store.prepare.assert_not_called()
        self.assertEqual(self.service.server.tool.call_count,1)

    def test_snapshot_expiring_during_model_blocks_delivery(self):
        self.service.live=True
        with patch('teams_service.erp_context',side_effect=[(self.available,True),
                    ({'financial_access':True,'status':'snapshot_stale'},False)]), patch('teams_service.assert_delivery'):
            with self.assertRaises(GuardError):
                self.service.respond(self.request,self.agent,'old-session',self.store)
        self.store.prepare.assert_not_called()

    def test_changed_peer_blocks_history_and_dataset_acquisition(self):
        self.service.identity.return_value={'binding':{'peer_id':'other','peer_email':'reader@example.test'}}
        with patch('teams_service.erp_context') as acquire:
            with self.assertRaises(GuardError):
                self.service.respond(self.request,self.agent,'old-session',self.store)
        self.service.server.tool.assert_not_called()
        acquire.assert_not_called()


if __name__=='__main__':unittest.main()
