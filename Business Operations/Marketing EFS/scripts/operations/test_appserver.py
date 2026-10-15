import json
import tempfile
import time
import unittest
import queue
from pathlib import Path
from unittest.mock import Mock
from appserver import AppServer, RateLimited, ApprovalRequired, approval_failure

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

class ApprovalTests(unittest.TestCase):
    def test_tool_approval_is_explicit_and_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            client=AppServer.__new__(AppServer)
            client.cooldown=Path(directory)/'cooldown.json'
            client.request=Mock(return_value={'isError':True,'content':[{'type':'text',
                'text':'MCP tool call requires approval, but approval policy is never'}]})
            with self.assertRaises(ApprovalRequired) as raised:
                client.tool('t','send_chat_message',{'text_content':'private'})
            self.assertEqual(raised.exception.action,'microsoft_teams.send_chat_message')
            client.request.assert_called_once()
            self.assertNotIn('private',str(raised.exception))

    def test_first_child_approval_interrupts_parent_before_another_action(self):
        client=AppServer.__new__(AppServer)
        client.events=queue.Queue()
        client.events.put({'method':'item/completed','params':{'threadId':'specialist',
            'item':{'type':'mcpToolCall','status':'failed','server':'codex_apps',
                'tool':'microsoft_sharepoint_upload_file_to_folder',
                'error':{'message':'MCP tool call requires approval, but approval policy is never'}}}})
        client.request=Mock(side_effect=[{'turn':{'id':'turn'}},{}])
        with self.assertRaises(ApprovalRequired) as raised:
            client.answer('parent','create file',timeout=1)
        self.assertIn('microsoft_sharepoint_upload_file_to_folder',raised.exception.action)
        self.assertEqual([c.args[0] for c in client.request.call_args_list],['turn/start','turn/interrupt'])

    def test_successful_document_mentioning_approval_is_not_a_block(self):
        self.assertIsNone(approval_failure({'type':'mcpToolCall','status':'completed',
            'result':{'content':[{'type':'text','text':'A previous tool requires approval.'}]}}))
        self.assertIsNone(approval_failure({'type':'agentMessage',
            'error':{'message':'approval required'}}))

    def test_server_approval_event_is_a_block_not_an_automatic_acceptance(self):
        client=AppServer.__new__(AppServer);client.events=queue.Queue()
        client.events.put({'method':'operations/approvalRequired','params':{
            'requestMethod':'item/permissions/requestApproval'}})
        client.request=Mock(side_effect=[{'turn':{'id':'turn'}},{}])
        with self.assertRaises(ApprovalRequired):client.answer('parent','work',timeout=1)
        self.assertEqual(client.request.call_args_list[-1].args[0],'turn/interrupt')

if __name__=='__main__':unittest.main()
