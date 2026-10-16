import copy
import sqlite3
import unittest
from unittest.mock import Mock
from marketing_delivery import (verify_files,teams_html,html_fingerprint,destination,direct_write,SIGNATURE)
from teams_state import GuardError

URL='https://efitsys.sharepoint.com/sites/Documentation/Shared%20Documents/General/Marketing/Outputs/Documentation/Brochures/test.pdf'
PEER={'peer_id':'peer','peer_email':'peer@efitsys.com','chat_id':'chat','message_id':'request'}
FILE={'drive_id':'drive','item_id':'file','web_url':URL,'e_tag':'revision1','label':'Scheda <test>','kind':'datasheet'}
ITEM={'id':'file','file':{'mimeType':'application/pdf'},'folder':None,'size':30,
      'parent_reference':{'drive_id':'drive'},'web_url':URL,'e_tag':'revision1'}
WRITE={'value':[{'roles':['write'],'granted_to_v2':{'user':{'id':'peer','email':'peer@efitsys.com'}}}]}

class DeliveryTests(unittest.TestCase):
    def setUp(self):self.db=sqlite3.connect(':memory:')
    def tearDown(self):self.db.close()
    def call(self,permissions=None):
        def run(name,args):
            if name=='get_drive_item':return copy.deepcopy(ITEM)
            if name=='list_item_permissions':return copy.deepcopy(permissions or WRITE)
            self.fail(name)
        return Mock(side_effect=run)
    def test_uploaded_file_verified_before_acl_and_no_redundant_grant(self):
        call=self.call();files=verify_files(call,self.db,PEER,[FILE])
        self.assertEqual([c.args[0] for c in call.call_args_list],['get_drive_item','list_item_permissions'])
        self.assertIn('<a href="'+URL+'">',teams_html('Ecco la scheda.',files))
    def test_grant_exact_recipient_file_and_verify_after_mutation(self):
        call=Mock(side_effect=[ITEM,{'value':[]},{},WRITE])
        verify_files(call,self.db,PEER,[FILE])
        names=[c.args[0] for c in call.call_args_list]
        self.assertEqual(names,['get_drive_item','list_item_permissions','invite_item_recipients','list_item_permissions'])
        grant=call.call_args_list[2].args[1]
        self.assertEqual(grant['recipients'],['peer@efitsys.com'])
        self.assertEqual(grant['target'],{'type':'drive_item','drive_id':'drive','item_id':'file'})
        self.assertEqual(grant['role'],'write');self.assertTrue(grant['require_sign_in'])
        self.assertFalse(grant['send_invitation']);self.assertTrue(grant['retain_inherited_permissions'])
    def test_uncertain_grant_not_replayed_even_after_restart(self):
        call=Mock(side_effect=[ITEM,{'value':[]},TimeoutError('unknown')])
        with self.assertRaises(TimeoutError):verify_files(call,self.db,PEER,[FILE])
        again=self.call({'value':[]})
        with self.assertRaisesRegex(GuardError,'uncertain'):verify_files(again,self.db,PEER,[FILE])
        self.assertNotIn('invite_item_recipients',[c.args[0] for c in again.call_args_list])
        # A later authoritative observation can reconcile an uncertain grant.
        verify_files(self.call(),self.db,PEER,[FILE])
    def test_read_only_unknown_group_and_display_name_do_not_prove_access(self):
        for row in ({'roles':['read'],'granted_to_v2':{'user':{'id':'peer'}}},
                    {'roles':['write'],'granted_to_v2':{'siteGroup':{'id':'peer'}}},
                    {'roles':['write'],'granted_to':{'user':{'displayName':'peer@efitsys.com'}}}):
            self.assertFalse(direct_write({'value':[row]},PEER))
    def test_public_and_organization_links_block_even_after_valid_named_acl(self):
        for scope in ('anonymous','organization'):
            permissions=copy.deepcopy(WRITE)
            permissions['value'].append({'roles':['read'],'link':{'scope':scope}})
            with self.assertRaisesRegex(GuardError,'broad_sharing'):direct_write(permissions,PEER)
    def test_incomplete_permissions_block(self):
        with self.assertRaises(GuardError):direct_write({**WRITE,'next_link':'more'},PEER)
    def test_stale_revision_folder_empty_or_wrong_file_never_shared(self):
        for change in ({'e_tag':'other'},{'id':'different'},{'file':None},{'folder':{'childCount':2}},
                       {'size':0},{'web_url':URL.replace('test.pdf','other.pdf')}):
            call=Mock(return_value={**ITEM,**change})
            with self.assertRaises(GuardError):verify_files(call,self.db,PEER,[FILE])
            self.assertEqual(call.call_count,1)
    def test_external_subdomain_lookalike_recipient_rejected(self):
        for address in ('peer@evil.com','peer@efitsys.com.evil','peer@sub.efitsys.com'):
            call=self.call()
            with self.assertRaises(GuardError):verify_files(call,self.db,{**PEER,'peer_email':address},[FILE])
            call.assert_not_called()
    def test_only_authorized_output_destination_and_datasheet_brochures(self):
        for url in (URL.replace('/Outputs/','/Inputs/'),URL.replace('/Brochures/','/Other/'),
                    URL.replace('efitsys.sharepoint.com','evil.com'),URL+'?share=public',URL+'/../private.pdf'):
            with self.assertRaises(GuardError):destination(url,'datasheet')
    def test_fallback_declared_and_verified_operations_drive(self):
        url='https://efitsys-my.sharepoint.com/personal/operations_efitsys_com/Documents/Chat%20con%20efitsys/test.pdf'
        entry={**FILE,'web_url':url,'kind':'other'}
        item={**ITEM,'web_url':url}
        call=Mock(side_effect=[item,{'value':[{'id':'drive','web_url':
            'https://efitsys-my.sharepoint.com/personal/operations_efitsys_com/Documents'}]},WRITE])
        files=verify_files(call,self.db,PEER,[entry])
        self.assertIn('OneDrive di Operations / Chat con efitsys',teams_html('Documento pronto.',files))
        with self.assertRaises(GuardError):destination(url,'datasheet')
    def test_html_escape_anchor_and_signature_once(self):
        files=[{**FILE,'fallback_note':None}]
        result=teams_html('Pronto <script>bad</script> ['+FILE['label']+']('+URL+')\n'+SIGNATURE,files)
        self.assertNotIn('<script>',result);self.assertIn('&lt;script&gt;',result)
        self.assertIn('Scheda &lt;test&gt;</a>',result)
        self.assertEqual(result.count(SIGNATURE),1)
    def test_unverified_link_without_manifest_never_sent(self):
        with self.assertRaises(GuardError):teams_html('[File]('+URL+')',[])
    def test_public_research_sources_keep_safe_clickable_links(self):
        result=teams_html('[Fonte](https://www.efitsys.com/technical)',[])
        self.assertIn('<a href="https://www.efitsys.com/technical">Fonte</a>',result)
    def test_receipt_checks_actual_href_not_only_label(self):
        one='<p><a href="'+URL+'">Scheda</a></p><p>'+SIGNATURE+'</p>'
        self.assertEqual(html_fingerprint(one),html_fingerprint(one.replace('<p>','<div>').replace('</p>','</div>')))
        self.assertNotEqual(html_fingerprint(one),html_fingerprint(one.replace('test.pdf','wrong.pdf')))
    def test_connector_markdown_readback_matches_html_with_wrapped_url(self):
        one='<p>Ecco <a href="'+URL+'">Scheda PDF</a>.</p><p>'+SIGNATURE+'</p>'
        markdown='Ecco [Scheda\nPDF]('+URL.replace('/test.pdf','/te\nst.pdf')+').\n\\- by Agente Marketing EFS'
        self.assertEqual(html_fingerprint(one),html_fingerprint(markdown))
        self.assertNotEqual(html_fingerprint(one),html_fingerprint(markdown.replace('st.pdf','xx.pdf')))
    def test_duplicate_manifest_rejected(self):
        with self.assertRaisesRegex(GuardError,'duplicate'):verify_files(self.call(),self.db,PEER,[FILE,FILE])

if __name__=='__main__':unittest.main()
