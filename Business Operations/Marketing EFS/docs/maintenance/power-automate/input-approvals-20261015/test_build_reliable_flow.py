import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

import build_reliable_flow as builder


def walk_actions(actions):
    for name, action in actions.items():
        yield name, action
        for child in (action.get('actions'), action.get('else', {}).get('actions')):
            if child:
                yield from walk_actions(child)


def siblings_valid(actions, ancestors):
    names = set(actions)
    for name, action in actions.items():
        if not set(action.get('runAfter', {})).issubset(names - {name}):
            raise AssertionError(f'Invalid runAfter: {name}')
        for child in (action.get('actions'), action.get('else', {}).get('actions')):
            if child:
                siblings_valid(child, ancestors | names)


def expression_strings(value):
    if isinstance(value, str):
        if value.startswith('@') and not value.startswith('@{'):
            yield value[1:]
    elif isinstance(value, dict):
        for child in value.values():
            yield from expression_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from expression_strings(child)


class ReliableFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(builder.ORIGINAL) as source:
            cls.workflow_name = next(n for n in source.namelist() if n.endswith('.json'))
            cls.original_workflow_bytes = source.read(cls.workflow_name)
            cls.original = json.loads(cls.original_workflow_bytes)
            cls.original_sha = hashlib.sha256(builder.ORIGINAL.read_bytes()).hexdigest()
        cls.definition = builder.make_definition(cls.original['properties']['definition'], '2026-10-15T14:01:21Z')

    def test_bootstrap_has_no_enabled_dispatch_or_acquisition(self):
        cfg = self.definition['actions']['Configuration']['inputs']
        self.assertFalse(cfg['EnableDispatch'])
        self.assertFalse(cfg['EnableAcquisition'])
        self.assertFalse(cfg['NativeStatusContractVerified'])
        self.assertEqual('Recurrence', self.definition['triggers']['Every_five_minutes']['type'])
        self.assertEqual(1, self.definition['triggers']['Every_five_minutes']['runtimeConfiguration']['concurrency']['runs'])

    def test_action_graph_dependencies_and_references(self):
        actions = self.definition['actions']
        siblings_valid(actions, set())
        flattened = list(walk_actions(actions))
        names = [name for name, _ in flattened]
        self.assertEqual(len(names), len(set(names)), 'Global action names must be unique')
        refs = re.findall(r"(?:body|outputs|result|items)\('([^']+)'\)", json.dumps(actions))
        self.assertFalse(set(refs) - set(names), set(refs)-set(names))
        for name, action in flattened:
            if action['type'] == 'Foreach':
                self.assertEqual(1, action['runtimeConfiguration']['concurrency']['repetitions'])

    def test_expression_delimiters(self):
        for expression in expression_strings(self.definition):
            stack=[]
            quoted=False
            index=0
            while index < len(expression):
                character=expression[index]
                if character == "'":
                    if quoted and index+1 < len(expression) and expression[index+1] == "'":
                        index+=2
                        continue
                    quoted=not quoted
                elif not quoted:
                    if character in '([':
                        stack.append(character)
                    elif character in ')]':
                        self.assertTrue(stack,expression)
                        self.assertEqual('(' if character==')' else '[',stack.pop(),expression)
                index+=1
            self.assertFalse(quoted,expression)
            self.assertFalse(stack,expression)

    def test_create_preserves_review_configuration_and_no_retry(self):
        original_create = next(iter(self.original['properties']['definition']['actions'].values()))
        create = dict(walk_actions(self.definition['actions']))['Create_native_approval']
        for key in ('dataset', 'table', 'approvalType', 'approvalSchema/approvers', 'approvalSchema/awaitAll'):
            self.assertEqual(original_create['inputs']['parameters'][key], create['inputs']['parameters'][key])
        self.assertEqual({'type':'none'}, create['inputs']['retryPolicy'])
        self.assertNotIn('triggerOutputs', json.dumps(self.definition))

    def test_cursor_only_commits_successful_page_and_server_scope(self):
        acquisition = self.definition['actions']['Acquisition_enabled']['actions']
        uri = acquisition['Poll_source']['inputs']['parameters']['parameters/uri']
        self.assertIn('startswith(FileRef', uri)
        self.assertIn('FSObjType%20eq%200', uri)
        self.assertIn('Created%20ge', uri)
        self.assertEqual({'Acquire_page':['Succeeded']}, acquisition['Commit_nonempty_page']['runAfter'])
        self.assertEqual({'type':'none'}, dict(walk_actions(acquisition))['Enqueue']['inputs']['retryPolicy'])

    def test_lease_and_final_updates_are_conditional(self):
        flat = dict(walk_actions(self.definition['actions']))
        lease = flat['Lease_row']['inputs']['parameters']['parameters/headers']['IF-MATCH']
        self.assertNotEqual('*',lease)
        for name, action in flat.items():
            inputs = action.get('inputs', {})
            params = inputs.get('parameters', {}) if isinstance(inputs,dict) else {}
            if name.endswith('_write') or name == 'Commit_cursor':
                self.assertNotEqual('*',params.get('parameters/headers',{}).get('IF-MATCH'))
        self.assertEqual(['Failed','TimedOut'],flat['Unknown_read']['runAfter']['Create_scope'])
        self.assertIn("DispatchState%20eq%20'queued'",flat['Queued_rows']['inputs']['parameters']['parameters/uri'])

    def test_packages_preserve_original_identity_and_allow_rollback(self):
        with tempfile.TemporaryDirectory(dir=builder.HERE) as temporary:
            destination=Path(temporary)/'bootstrap.zip'
            builder.build(output=destination)
            with zipfile.ZipFile(destination) as generated, zipfile.ZipFile(builder.ORIGINAL) as source:
                self.assertIsNone(generated.testzip())
                self.assertEqual(source.read('customizations.xml'),generated.read('customizations.xml'))
                out=json.loads(generated.read(self.workflow_name))
                self.assertEqual(self.original['properties']['connectionReferences'],out['properties']['connectionReferences'])
                self.assertEqual('1.0.1.0',ET.fromstring(generated.read('solution.xml')).find('.//Version').text)
            rollback=Path(temporary)/'rollback.zip'
            builder.build(output=rollback,rollback=True)
            with zipfile.ZipFile(rollback) as archive:
                self.assertEqual(self.original_workflow_bytes,archive.read(self.workflow_name))
                self.assertEqual('1.0.1.9',ET.fromstring(archive.read('solution.xml')).find('.//Version').text)
        self.assertEqual(self.original_sha,hashlib.sha256(builder.ORIGINAL.read_bytes()).hexdigest())

    def test_nested_payload_json_is_expression_serialized(self):
        value={'Payload':"@string(outputs('Snapshot'))",'__metadata':{'type':"@body('Metadata')?['type']"}}
        action=builder.http('POST','_api/test',value)
        body=action['inputs']['parameters']['parameters/body']
        self.assertTrue(body.startswith('@string(setProperty('))
        self.assertIn("string(outputs('Snapshot'))",body)
        self.assertNotIn('"@body(',body)

    def test_result_and_restart_quarantine_guards(self):
        flat=dict(walk_actions(self.definition['actions']))
        verify=flat['Verify_created_result']
        self.assertEqual({'Create_scope':['Succeeded']},verify['runAfter'])
        self.assertIn("['approvalId']",verify['expression'])
        self.assertIn("['ApprovalId']",verify['expression'])
        self.assertIn('Empty_result_write',verify['else']['actions'])
        expired=flat['Expired_to_unknown']['inputs']['parameters']['parameters/body']
        self.assertIn("json('"+'"unknown"'+"')",expired)
        self.assertIn("'reconcileRequired',true",expired)
        self.assertIn("DispatchState%20eq%20'queued'",flat['Queued_rows']['inputs']['parameters']['parameters/uri'])
        self.assertIn("addMinutes(utcNow(),-15)",flat['Expired_processing']['inputs']['parameters']['parameters/uri'])

    def test_live_diagnostics_and_schema_mutations_are_guarded(self):
        live=builder.make_definition(self.original['properties']['definition'],'2026-10-15T14:01:21Z',True,True)
        actions=live['actions']
        self.assertFalse(actions['Configuration']['inputs']['BootstrapDiagnostics'])
        self.assertIn('Source_item_diagnostics',actions['Bootstrap_diagnostics']['actions'])
        self.assertIn('Index_title',actions['Ensure_title_index']['actions'])
        self.assertIn('Unique_title',actions['Ensure_title_unique']['actions'])
        self.assertEqual({},actions['Ensure_title_unique']['else']['actions'])


if __name__ == '__main__':
    unittest.main()
