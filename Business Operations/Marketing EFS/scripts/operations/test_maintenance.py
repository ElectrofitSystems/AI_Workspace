import tempfile,unittest,hashlib
import json
from pathlib import Path
from unittest.mock import patch
from maintenance import REQUIRED,guarded_digests,current_brand,sandbox_probe,service_issues
from marketing_runtime import restricted_config
from runtime_paths import refresh_node_reference

class MaintenanceTests(unittest.TestCase):
    def test_service_health_error_is_an_issue_even_when_process_is_running(self):
        self.assertEqual(service_issues({'Enabled':True,'Running':True,
            'Health':{'status':'error','error_type':'RpcError'}}),
            ['service_health_error:RpcError'])
        self.assertEqual(service_issues({'Enabled':True,'Running':True,
            'Health':{'status':'error'}}),['service_health_error'])

    def test_service_diagnostic_preserves_explicit_stop_and_existing_states(self):
        for service,expected in [
            ({'Enabled':False,'Running':False,'Health':{'status':'error'}},[]),
            ({'Enabled':False,'Running':True,'Health':{'status':'error'}},[]),
            ({'Enabled':True,'Running':False,'Health':{'status':'error'}},['service_not_running']),
            ({'Enabled':True,'Running':True,'Health':{'status':'running'}},[])]:
            with self.subTest(service=service):
                self.assertEqual(service_issues(service),expected)

    def test_maintenance_reports_running_heartbeat_error_without_restarting_service(self):
        import maintenance
        from datetime import datetime,timezone
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'state';state.mkdir()
            service={'Enabled':True,'Running':True,'Health':{
                'at':datetime.now(timezone.utc).isoformat(),'status':'error',
                'error_type':'RpcError','runtime_executable':'codex.exe'}}
            with patch.object(maintenance,'STATE',state), \
                 patch.object(maintenance,'WORK',root/'work'), \
                 patch.object(maintenance,'snapshot',return_value=str(root/'backup')), \
                 patch.object(maintenance,'refresh_node_reference',return_value=False), \
                 patch.object(maintenance,'resolve_codex',return_value='codex.exe'), \
                 patch.object(maintenance,'check',return_value={'issues':[]}), \
                 patch.object(maintenance,'control',return_value=service) as control, \
                 patch.object(maintenance.sys,'argv',['maintenance.py']), \
                 patch('builtins.print'):
                self.assertEqual(maintenance.main(),1)
            control.assert_called_once_with('Status')
            report=json.loads((state/'maintenance-status.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'],'attention_required')
            self.assertIn('service_health_error:RpcError',report['issues'])
            self.assertEqual(report['repairs'],[])

    def test_probe_checks_real_input_and_output_and_does_not_accept_stale_token(self):
        from types import SimpleNamespace
        with patch('maintenance.uuid.uuid4',return_value=SimpleNamespace(hex='fresh')), \
             patch('maintenance.run',return_value=SimpleNamespace(returncode=0,stdout='MARKETING_HEALTH_fresh\n')) as run:
            self.assertTrue(sandbox_probe('codex.exe'))
            args=run.call_args.args[0];script=args[-1]
            self.assertIn("$ErrorActionPreference='Stop'",script)
            self.assertIn('ReadAllBytes',script)
            self.assertIn('runtime-checks',script)
            self.assertIn('--',args)
        with patch('maintenance.run',return_value=SimpleNamespace(returncode=1,stdout='MARKETING_HEALTH_OK\n')):
            self.assertFalse(sandbox_probe('codex.exe'))
    def test_brand_rejects_changed_logo_without_historical_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'docs/company').mkdir(parents=True);(root/'input/kit').mkdir(parents=True)
            archive=root/'input/kit.zip';archive.write_bytes(b'archive')
            logo=root/'input/kit/logo.svg';logo.write_bytes(b'official')
            digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
            manifest={'version':'selected','archive':'input/kit.zip','source':{'sha256':digest(archive)},
                'asset_root':'input/kit','assets':{'logo':'logo.svg'},'asset_sha256':{'logo':digest(logo)}}
            (root/'docs/company/brand-kit.json').write_text(json.dumps(manifest),encoding='utf-8')
            self.assertTrue(current_brand(root)['logo_verified'])
            logo.write_bytes(b'outdated')
            with self.assertRaisesRegex(ValueError,'brand_asset_hash_mismatch'):current_brand(root)
    def test_required_skills_cover_marketing_and_production(self):
        for name in ('presentations','documents','pdf','spreadsheets','imagegen','efs-linkedin-content','efs-linkedin-performance'):
            self.assertIn(name,REQUIRED)
    def test_restricted_lane_keeps_private_state_denied_without_parent_acl_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            r=Path(directory).resolve()
            cfg={'default_permissions':'ops','permissions.ops.filesystem':{(r/'.local').as_posix():'deny','ERP-private':'deny'},'features.apps':False}
            out=restricted_config(cfg,r)
            self.assertEqual(out['permissions.ops.filesystem'][(r/'.local').as_posix()],'read')
            self.assertEqual(out['permissions.ops.filesystem'][(r/'.local/operations-teams').as_posix()],'deny')
            self.assertEqual(out['permissions.ops.filesystem']['ERP-private'],'deny')
            self.assertFalse(out['features.apps'])
    def test_guarded_configuration_has_policy_and_financial_routing(self):
        d=guarded_digests()
        self.assertIn('marketing-access.json',d);self.assertIn('erp_followups.py',d)
        self.assertTrue(all(len(x)==64 for x in d.values()))
    def test_stale_node_reference_updates_only_node_configuration_and_keeps_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory).resolve();(home/'.codex').mkdir()
            base=home/'AppData/Local/OpenAI/Codex/runtimes/cua_node'
            old=base/'old/bin/node_repl.exe';new=base/'new/bin/node_repl.exe'
            new.parent.mkdir(parents=True);new.touch();(new.parent/'node.exe').touch();(new.parent/'node_modules').mkdir()
            root=home/'Marketing';(root/'.local/operations-teams').mkdir(parents=True)
            cfg=home/'.codex/config.toml'
            cfg.write_text('model = "unchanged"\n[mcp_servers.node_repl]\ncommand = '+json.dumps(str(old))+'\n',encoding='utf-8')
            with patch('runtime_paths.Path.home',return_value=home):
                self.assertTrue(refresh_node_reference(root))
                self.assertFalse(refresh_node_reference(root))
            self.assertIn('model = "unchanged"',cfg.read_text(encoding='utf-8'))
            self.assertTrue(list((root/'.local/operations-teams').glob('runtime-config-before-*.toml')))

if __name__=='__main__':unittest.main()
