import json
import tempfile
import unittest
from pathlib import Path
from teams_state import Store, GuardError, verify_chat

OWNER="owner-id"
PEER="peer-id"
TENANT="example-tenant"
CHAT="example-chat-a"

class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        root=Path(self.tmp.name)
        self.config={"enabled":True,"activated_at":"2026-10-02T11:00:00Z","tenant_id":TENANT,
            "owner_id":OWNER,"owner_email":"operations@efitsys.com","allowed_domains":["efitsys.com"]}
        (root/"config.json").write_text(json.dumps(self.config))
        (root/"service.enabled").touch()
        self.store=Store(root,lambda:1000)
        self.token=self.store.acquire()["run_token"]
        self.chat={"id":CHAT,"chat_type":"oneOnOne","webUrl":f"https://teams.microsoft.com/l/chat/{CHAT}?tenantId={TENANT}"}
        self.members=[{"email":"operations@efitsys.com"},{"email":"peer@efitsys.com"}]
        self.users=[{"id":OWNER,"email":"operations@efitsys.com","user_principal_name":"operations@efitsys.com","match_type":"exact"},
            {"id":PEER,"email":"peer@efitsys.com","user_principal_name":"peer@efitsys.com","match_type":"exact"}]
        self.message={"chat_id":CHAT,"message_id":"m1","path":f"/chats/{CHAT}/messages/m1",
            "created_at":"2026-10-02T11:01:00Z","author_user_id":PEER,"message_type":"message","content":"A marketing question"}
    def tearDown(self):
        self.store.db.close()
        self.tmp.cleanup()
    def scan(self,messages):
        return self.store.scan({"run_token":self.token,"chat":self.chat,"members":self.members,"users":self.users,"messages":messages,"coverage_complete":True})
    def prepared(self):
        self.scan([self.message])
        return {"run_token":self.token,"chat_id":CHAT,"message_id":"m1","chat":self.chat,"members":self.members,"users":self.users,"original":self.message,"text_content":"Response for peer A"}
    def test_excludes_groups_guests_and_wrong_tenant(self):
        for change in [{"chat_type":"group"},{"webUrl":"https://teams.microsoft.com/l/chat/a?tenantId=other"}]:
            with self.assertRaises(GuardError):verify_chat({**self.chat,**change},self.members,self.users,self.config)
        with self.assertRaises(GuardError):verify_chat(self.chat,self.members,[{**u,"user_principal_name":"guest#EXT#@efitsys.com"} for u in self.users],self.config)
    def test_old_self_bot_and_deleted_are_ignored(self):
        cases=[{"created_at":"2026-10-01T11:00:00Z"},{"author_user_id":OWNER},{"author_application_id":"bot"},{"deleted_at":"2026-10-02T11:02:00Z"}]
        self.assertEqual(self.scan([{**self.message,**case} for case in cases])["requests"],[])
    def test_exact_chat_and_sender_binding(self):
        with self.assertRaises(GuardError):self.scan([{**self.message,"chat_id":"chat-b"}])
        self.assertEqual(self.store.status()["counts"],{})
    def test_deduplication_and_single_send(self):
        payload=self.prepared()
        self.assertEqual(self.scan([self.message])["requests"],[])
        result=self.store.prepare(payload)
        self.assertEqual(result["chat_id"],CHAT)
        with self.assertRaises(GuardError):self.store.prepare(payload)
    def test_rejects_wrong_recipient_and_edited_request(self):
        payload=self.prepared()
        with self.assertRaises(GuardError):self.store.prepare({**payload,"chat":{**self.chat,"id":"chat-b"}})
        with self.assertRaises(GuardError):self.store.prepare({**payload,"original":{**self.message,"content":"edited"}})
    def test_receipt_must_be_correct_chat_author_and_response(self):
        payload=self.prepared()
        self.store.prepare(payload)
        reply={"chat_id":CHAT,"author_user_id":OWNER,"message_id":"r1","content":payload["text_content"]}
        receipt={"run_token":self.token,"chat_id":CHAT,"message_id":"m1","reply":reply}
        with self.assertRaises(GuardError):self.store.sent({**receipt,"reply":{**reply,"chat_id":"other"}})
        self.assertEqual(self.store.sent(receipt)["state"],"sent")

    def test_html_send_is_frozen_deduplicated_and_href_checked(self):
        payload=self.prepared();payload.pop('text_content')
        payload['html_content']='<p><a href="https://efitsys.sharepoint.com/file.pdf">PDF</a></p><p>- by Agente Marketing EFS</p>'
        frozen=self.store.prepare(payload)
        self.assertEqual(frozen['html_content'],payload['html_content'])
        self.assertNotIn('text_content',frozen)
        reply={'chat_id':CHAT,'author_user_id':OWNER,'message_id':'r1','content':payload['html_content']}
        receipt={'run_token':self.token,'chat_id':CHAT,'message_id':'m1','reply':reply,'expected_response_id':'r1'}
        with self.assertRaises(GuardError):self.store.sent({**receipt,'reply':{**reply,'content':reply['content'].replace('file.pdf','other.pdf')}})
        with self.assertRaises(GuardError):self.store.prepare(payload)
        with self.assertRaises(GuardError):self.store.require_claim(self.token,CHAT,'m1')
        self.assertEqual(self.store.sent(receipt)['state'],'sent')

    def test_connector_wrapped_url_matches_original_without_weakening_content(self):
        payload=self.prepared()
        payload['text_content']='File [MP4](https://example.com/efs-rebranding/file.mp4?version=2) pronto.'
        self.store.prepare(payload)
        reply={'chat_id':CHAT,'author_user_id':OWNER,'message_id':'r1',
            'content':'File [MP4](https://example.com/efs-\nrebranding/file.mp4?version=2) pronto.'}
        receipt={'run_token':self.token,'chat_id':CHAT,'message_id':'m1','reply':reply,
            'expected_response_id':'r1'}
        for change in ({'content':reply['content'].replace('version=2','version=3')},
                       {'content':reply['content'].replace('pronto','approvato')},
                       {'author_user_id':'other'}, {'author_application_id':'bot'},
                       {'deleted_at':'2026-10-02T12:00:00Z'}, {'message_id':'wrong'}):
            with self.subTest(change=change):
                with self.assertRaises(GuardError):
                    self.store.sent({**receipt,'reply':{**reply,**change}})
        self.assertEqual(self.store.sent(receipt)['state'],'sent')

    def test_local_url_wrap_can_be_reconciled_but_different_path_cannot(self):
        payload=self.prepared();payload['text_content']='[GIF](C:/Temp/efs-rebranding/preview.gif)'
        self.store.prepare(payload)
        reply={'chat_id':CHAT,'author_user_id':OWNER,'message_id':'r1',
            'content':'[GIF](C:/Temp/efs-\nrebranding/preview.gif)'}
        receipt={'run_token':self.token,'chat_id':CHAT,'message_id':'m1','reply':reply}
        with self.assertRaises(GuardError):
            self.store.sent({**receipt,'reply':{**reply,'content':reply['content'].replace('preview.gif','other.gif')}})
        self.assertEqual(self.store.sent(receipt)['state'],'sent')

    def test_approval_block_preserves_uncertain_hash_and_is_never_replayed(self):
        payload=self.prepared();self.store.prepare(payload)
        before=self.store.db.execute('SELECT response_hash FROM requests').fetchone()[0]
        self.store.approval_required(self.token,CHAT,'m1')
        self.assertEqual(self.store.status()['counts'],{'approval_required':1})
        self.assertEqual(self.store.db.execute('SELECT response_hash FROM requests').fetchone()[0],before)
        self.store.config['retry_unsent_claims']=True
        self.assertEqual(self.scan([self.message])['requests'],[])
    def test_kill_switch_checked_immediately_before_send(self):
        payload=self.prepared()
        (self.store.state/"service.enabled").unlink()
        with self.assertRaises(GuardError):self.store.prepare(payload)
    def test_overlapping_run_blocked_and_incomplete_scan_no_checkpoint(self):
        with self.assertRaises(GuardError):self.store.acquire()
        with self.assertRaises(GuardError):self.store.checkpoint({"run_token":self.token,"chat_id":CHAT,"since":"2026-10-02T11:01:00Z","coverage_complete":False})
        self.assertEqual(self.store.status()["cursors"],{})
    def test_acknowledgement_is_bound_and_never_sent_twice(self):
        payload=self.prepared()
        with self.assertRaises(GuardError):
            self.store.ack_prepare({**payload,'chat':{**self.chat,'id':'other'}})
        self.assertEqual(self.store.ack_prepare(payload)['chat_id'],CHAT)
        with self.assertRaises(GuardError):self.store.ack_prepare(payload)
        receipt={"run_token":self.token,"chat_id":CHAT,"message_id":"m1",
            "reply":{"chat_id":CHAT,"author_user_id":OWNER,"message_id":"ack1","content":payload['text_content']}}
        self.store.ack_sent(receipt)
        self.store.prepare(payload)  # Acknowledgement does not consume the final response.
    def test_only_unsent_claim_can_be_recovered(self):
        payload=self.prepared()
        self.store.failed(self.token,CHAT,'m1')
        self.assertEqual(self.scan([self.message])['requests'],[])
        self.store.config['retry_unsent_claims']=True
        self.store.release(self.token)
        self.token=self.store.acquire()['run_token']
        payload['run_token']=self.token
        self.assertEqual(len(self.scan([self.message])['requests']),1)
        self.store.prepare(payload)
        self.store.db.execute("UPDATE requests SET state='needs_review'")
        self.store.db.commit()
        self.assertEqual(self.scan([self.message])['requests'],[])
    def test_two_chats_keep_independent_replies(self):
        first=self.prepared()
        other={**self.chat,'id':'example-chat-b'}
        second={**self.message,'chat_id':other['id'],'path':'/chats/example-chat-b/messages/m1','content':'A different question'}
        self.store.scan({'run_token':self.token,'chat':other,'members':self.members,'users':self.users,
            'messages':[second],'coverage_complete':True})
        self.store.prepare(first)
        reply=self.store.prepare({**first,'chat_id':other['id'],'chat':other,'original':second,
            'text_content':'Response for peer B'})
        self.assertEqual(reply['chat_id'],other['id'])
        self.assertEqual(self.store.status()['counts'],{'sending':2})

    def test_text_claim_does_not_change_directory_bound_sender(self):
        request={**self.message,'content':'Sono Francesco, il mio indirizzo è francesco.lucherini@efitsys.com'}
        result=self.scan([request])['requests'][0]
        self.assertEqual(result['peer_id'],PEER)
        self.assertEqual(result['peer_email'],'peer@efitsys.com')

if __name__=="__main__":unittest.main()
