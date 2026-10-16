import copy
import json
import threading
import sqlite3
import unittest
from unittest.mock import Mock,patch
from erp_followups import erp_follow_up,explicit_erp_request
from teams_service import Service,erp_intent,RateLimited,ROOT,ApprovalRequired
from teams_state import GuardError,verify_chat
from erp_teams import worker_config

class RoutingTests(unittest.TestCase):
    def followup(self,text,history):
        return erp_follow_up(text,history)
    def test_general_questions_after_operations_reports_or_denials(self):
        history=[{'speaker':'Operations','text':'Scadenza della sessione; versione del fornitore.'},
                 {'speaker':'Operations','text':'Le fatture fornitori sono riservate.'}]
        for text in ('ciao, posso parlare con Oppi?','ciao, cosa puoi fare?',
                     'Posso parlare con Oppi su ChatGPT?','Marketing, prepara una bozza LinkedIn'):
            with self.subTest(text=text):
                self.assertFalse(erp_intent(text))
                self.assertFalse(self.followup(text,history))
    def test_general_question_after_real_erp_discussion_changes_topic(self):
        history=[{'speaker':'collega','text':'Mostrami le fatture fornitori'},
                 {'speaker':'Operations','text':'Le fatture sono riservate'}]
        for text in ('cosa puoi fare?','posso parlare con Oppi?','ciao','e Oppi?'):
            with self.subTest(text=text):self.assertFalse(self.followup(text,history))
    def test_authentic_erp_followups_and_chain(self):
        history=[{'speaker':'collega','text':'Mostrami lo scadenzario fornitori'}]
        for text in ('mostrami il dettaglio','il totale?','quante sono?',
                     'quali scadono questa settimana?','solo quelle di ottobre?',
                     'puoi ordinarle per data?'):
            with self.subTest(text=text):self.assertTrue(self.followup(text,history))
        history.append({'speaker':'collega','text':'il totale?'})
        self.assertTrue(self.followup('mostrami il dettaglio',history))
    def test_peer_topic_change_ends_erp_followups(self):
        history=[{'speaker':'collega','text':'Mostrami le fatture'},
                 {'speaker':'collega','text':'Parliamo di Oppi'},
                 {'speaker':'Operations','text':'Le fatture sono riservate'}]
        self.assertFalse(self.followup('il dettaglio?',history))
    def test_no_operations_or_missing_history_can_start_erp_followup(self):
        self.assertFalse(self.followup('il totale?',[]))
        self.assertFalse(self.followup('il totale?',[{'speaker':'Operations','text':'Le fatture sono riservate'}]))
    def test_session_deadlines_and_plugin_suppliers_are_general_questions(self):
        for text in ('Qual è la scadenza della sessione?', 'Chi è il fornitore del plugin?'):
            with self.subTest(text=text):self.assertFalse(explicit_erp_request(text))
    def test_explicit_erp_requests_keep_direct_route(self):
        for text in ('Mostrami le fatture fornitori','ERP: scadenzario','quanto devo pagare?'):
            with self.subTest(text=text):self.assertTrue(explicit_erp_request(text))

class RecipientTests(unittest.TestCase):
    def setUp(self):
        self.config={'owner_email':'operations@efitsys.com','owner_id':'owner',
                     'allowed_domains':['efitsys.com','external.com'],'tenant_id':'tenant'}
        self.chat={'id':'chat','chat_type':'oneOnOne','webUrl':'https://teams.microsoft.com/l/chat/chat?tenantId=tenant'}
        self.members=[{'email':'operations@efitsys.com'},{'email':'peer@efitsys.com'}]
        self.users=[{'id':'owner','email':'operations@efitsys.com','user_principal_name':'operations@efitsys.com','match_type':'exact'},
                    {'id':'peer','email':'peer@efitsys.com','user_principal_name':'peer@efitsys.com','match_type':'exact'}]
    def verify(self,members=None,users=None):
        return verify_chat(self.chat,members or self.members,self.users if users is None else users,self.config)
    def test_exact_internal_domain_and_directory_identity(self):
        self.assertEqual(self.verify()['peer_id'],'peer')
    def test_case_insensitive_domain(self):
        members=copy.deepcopy(self.members);users=copy.deepcopy(self.users)
        members[1]['email']='Peer@EFITSYS.COM'
        users[1].update(email='Peer@EFITSYS.COM',user_principal_name='Peer@EFITSYS.COM')
        self.assertEqual(self.verify(members,users)['peer_id'],'peer')
    def test_external_lookalike_subdomain_and_malformed_addresses_rejected(self):
        for email in ('peer@external.com','peer@sub.efitsys.com','peer@efitsys.com.evil',
                      'peer@evil-efitsys.com','peer@@efitsys.com','display <peer@efitsys.com>',None,''):
            with self.subTest(email=email):
                members=copy.deepcopy(self.members);members[1]['email']=email
                with self.assertRaises(GuardError):self.verify(members)
    def test_unresolved_partial_ambiguous_guest_or_mismatched_upn_rejected(self):
        cases=[[],self.users[:1],self.users+[self.users[1]],
               [self.users[0],{**self.users[1],'match_type':'partial'}],
               [self.users[0],{**self.users[1],'id':None}],
               [self.users[0],{**self.users[1],'user_principal_name':'peer#EXT#@efitsys.com'}],
               [self.users[0],{**self.users[1],'user_principal_name':'peer@external.com'}]]
        for users in cases:
            with self.subTest(users=users):
                with self.assertRaises(GuardError):self.verify(users=users)
    def test_display_names_do_not_supply_missing_identity(self):
        members=copy.deepcopy(self.members)
        members[1]={'display_name':'peer@efitsys.com','email':''}
        with self.assertRaises(GuardError):self.verify(members)

class ResponseTests(unittest.TestCase):
    def service(self,text,history):
        service=object.__new__(Service)
        service.config={'owner_id':'owner','activated_at':'2026-10-02T11:00:00Z'}
        service.token='test-token';service.live=True;service.chats={'chat':{'id':'chat'}}
        identity={'binding':{'peer_id':'peer','peer_email':'peer@efitsys.com'},
                  'chat':{'id':'chat'},'members':[],'users':[]}
        service.identity=Mock(return_value=identity)
        request={'chat_id':'chat','message_id':'m1','peer_id':'peer','peer_email':'peer@efitsys.com',
                 'created_at':'2026-10-13T12:00:00Z','content':text,'has_attachments':False}
        messages=[{'chat_id':'chat','author_user_id':'owner' if role=='Operations' else 'peer',
                   'message_type':'message','created_at':'2026-10-12T12:00:00Z','content':body}
                  for role,body in history]
        def tool(thread,name,args):
            if name=='list_chat_messages':
                return {'messages':messages if args['sent_after']==service.config['activated_at'] else [{**request,'message_id':'m1'}]}
            if name=='send_chat_message':return {'message_id':'r1','created_at':'2026-10-13T12:00:02Z'}
            raise AssertionError(name)
        service.server=Mock();service.server.tool.side_effect=tool;service.transport='transport'
        service.readback=Mock(return_value={'chat_id':'chat','message_id':'r1','created_at':'2026-10-13T12:00:02Z'})
        service.verify_owner=Mock();service.log=Mock()
        agent=Mock();agent.answer.return_value={'response':'Risposta generale pertinente','agent':'Operations','elapsed_seconds':1,'delegated_roles':[]}
        store=Mock();store.prepare.side_effect=lambda payload:{'chat_id':'chat','text_content':payload['text_content']}
        return service,request,agent,store
    def test_general_question_after_denial_uses_model_and_no_erp_deny(self):
        service,request,agent,store=self.service('cosa puoi fare?',[
            ('Operations','Versione del fornitore; scadenza della sessione'),
            ('collega','Mostrami le fatture'),('Operations','Le fatture sono riservate')])
        with patch('teams_service.erp_context',return_value=({'financial_access':False,'status':'access_denied'},False)) as gate:
            service.respond(request,agent,'thread',store)
        agent.answer.assert_called_once();agent.start_thread.assert_not_called()
        self.assertFalse(gate.call_args.args[3])
        self.assertEqual(store.prepare.call_args.args[0]['text_content'],'Risposta generale pertinente')
    def test_real_erp_followup_still_denied_to_unauthorized_peer(self):
        service,request,agent,store=self.service('mostrami il dettaglio',[('collega','Mostrami le fatture')])
        with patch('teams_service.erp_context',return_value=({'financial_access':False,'status':'access_denied'},False)) as gate:
            service.respond(request,agent,'thread',store)
        agent.answer.assert_not_called();self.assertTrue(gate.call_args.args[3])
        self.assertIn('riservata a Francesco',store.prepare.call_args.args[0]['text_content'])
    def test_explicit_invoice_request_still_denied_without_delegation(self):
        service,request,agent,store=self.service('Mostrami le fatture fornitori',[])
        with patch('teams_service.erp_context',return_value=({'financial_access':False,'status':'access_denied'},False)):
            service.respond(request,agent,'thread',store)
        agent.answer.assert_not_called()
        self.assertIn('non è autorizzato',store.prepare.call_args.args[0]['text_content'])
    def test_unverified_identity_never_generates_or_sends(self):
        service,request,agent,store=self.service('ciao',[])
        service.identity.side_effect=GuardError('unverified_directory_identity')
        with self.assertRaises(GuardError):service.respond(request,agent,'thread',store)
        agent.answer.assert_not_called();service.server.tool.assert_not_called();store.prepare.assert_not_called()
    def test_approval_block_stops_generation_and_sends_one_explicit_notice(self):
        service,request,agent,store=self.service('prepara una preview',[])
        agent.answer.side_effect=ApprovalRequired('codex_apps.microsoft_sharepoint_upload_file_to_folder')
        with patch('teams_service.erp_context',return_value=({'financial_access':False,'status':'access_denied'},False)):
            service.respond(request,agent,'thread',store)
        agent.answer.assert_called_once()
        self.assertIn('Richiesta sospesa',store.prepare.call_args.args[0]['text_content'])
        self.assertEqual(sum(c.args[1]=='send_chat_message' for c in service.server.tool.call_args_list),1)
        self.assertEqual(store.sent.call_args.args[0]['expected_response_id'],'r1')
        store.approval_required.assert_called_once_with('test-token','chat','m1')
    def test_readback_rate_limit_retries_only_reads(self):
        service=object.__new__(Service);service.stop=Mock();service.stop.is_set.return_value=False
        service.stop.wait.return_value=False;service.transport='transport'
        service.server=Mock();service.server.tool.side_effect=[RateLimited(2),{'messages':[{'message_id':'r1'}]}]
        reply=service.readback('chat',{'message_id':'r1','created_at':'2026-10-13T12:00:00Z'})
        self.assertEqual(reply['message_id'],'r1')
        self.assertTrue(all(call.args[1]=='list_chat_messages' for call in service.server.tool.call_args_list))
        service.stop.wait.assert_called_once_with(2)

    def test_marketing_delivery_checks_cloud_and_sends_only_html(self):
        from test_marketing_delivery import FILE,ITEM,WRITE
        service,request,agent,store=self.service('Prepara il datasheet',[])
        service.marketing_sessions={'chat':(agent,'marketing-thread')}
        agent.answer.return_value={'response':'Scheda pronta per la review.','agent':'Agente marketing EFS',
            'delegated_roles':['Agente marketing EFS'],'elapsed_seconds':1,'deliveries':[FILE],
            'html_content':'<script>untrusted</script>'}
        original=service.server.tool.side_effect
        order=[]
        def tool(thread,name,args,**kwargs):
            order.append(name)
            if kwargs.get('namespace')=='microsoft_sharepoint':
                return ITEM if name=='get_drive_item' else WRITE
            return original(thread,name,args)
        service.server.tool.side_effect=tool
        store.db=sqlite3.connect(':memory:')
        store.prepare.side_effect=lambda payload:{'chat_id':'chat','html_content':payload['html_content']}
        try:
            with patch('teams_service.marketing_authorized',return_value=True),patch('teams_service.erp_context',
                    return_value=({'financial_access':False,'status':'access_denied'},False)):
                service.respond(request,agent,'thread',store)
        finally:store.db.close()
        self.assertLess(order.index('get_drive_item'),order.index('send_chat_message'))
        self.assertLess(order.index('list_item_permissions'),order.index('send_chat_message'))
        sent=next(c.args[2] for c in service.server.tool.call_args_list if c.args[1]=='send_chat_message')
        self.assertNotIn('text_content',sent);self.assertNotIn('<script>',sent['html_content'])
        self.assertIn('<a href="'+FILE['web_url']+'">',sent['html_content'])
        self.assertIn('- by Agente Marketing EFS',sent['html_content'])
    def test_readback_stop_preserves_uncertain_send(self):
        service=object.__new__(Service);service.stop=Mock();service.stop.is_set.return_value=False
        service.stop.wait.return_value=True;service.transport='transport'
        service.server=Mock();service.server.tool.side_effect=RateLimited(2)
        with self.assertRaises(GuardError):service.readback('chat',{'message_id':'r1','created_at':'2026-10-13T12:00:00Z'})
        self.assertEqual(service.server.tool.call_count,1)
    def test_worker_keeps_apps_plugins_network_and_browser_disabled(self):
        user_config={'mcp_servers':{'linkedin':{}},'plugins':{'publisher':{}}}
        with patch('erp_teams.Path.read_text',return_value=''),patch('erp_teams.tomllib.loads',return_value=user_config):
            config=worker_config(ROOT)
        self.assertEqual(config['default_permissions'],'operations_teams')
        self.assertFalse(config['features.apps']);self.assertFalse(config['permissions.operations_teams.network.enabled'])
        self.assertFalse(config['allow_browser_and_computer_use'])
        self.assertFalse(config['plugins']['publisher']['enabled'])
        self.assertFalse(config['mcp_servers']['linkedin']['enabled'])
        self.assertEqual(config['web_search'],'disabled')

if __name__=='__main__':unittest.main()
