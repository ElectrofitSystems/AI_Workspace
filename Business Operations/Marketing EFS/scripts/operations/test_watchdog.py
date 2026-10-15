import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,Mock
from runtime_paths import resolve_codex,codex_candidates

class RuntimePathTests(unittest.TestCase):
    def test_healthy_installed_runtime_selected(self):
        with tempfile.TemporaryDirectory(prefix='operations runtime ') as directory:
            executable = Path(directory) / 'codex.exe'
            executable.touch()
            with patch('runtime_paths.codex_candidates',return_value=[executable]),patch('runtime_paths.subprocess.run',return_value=Mock(returncode=0,stdout='codex-cli 0.160.0')):
                self.assertEqual(resolve_codex(),executable)

    def test_removed_runtime_falls_back(self):
        with patch('runtime_paths.codex_candidates',return_value=[Path('old.exe'),Path('new.exe')]),patch('runtime_paths.subprocess.run',side_effect=[OSError('removed'),Mock(returncode=0,stdout='codex-cli 1.0')]):
            self.assertEqual(resolve_codex(),Path('new.exe'))

    def test_incomplete_distribution_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);folder=root/'AppData/Local/OpenAI/Codex/bin/hash'
            folder.mkdir(parents=True);exe=folder/'codex.exe';exe.touch()
            with patch('runtime_paths.Path.home',return_value=root),patch('runtime_paths.shutil.which',return_value=None),patch.dict('os.environ',{'OPERATIONS_CODEX':'','CODEX_CLI_PATH':''}):
                self.assertEqual(codex_candidates(),[])
                (folder/'codex-windows-sandbox-setup.exe').touch()
                self.assertEqual(codex_candidates(),[exe.resolve()])

    def test_no_valid_runtime_fails_explicitly(self):
        with patch('runtime_paths.codex_candidates',return_value=[]):
            with self.assertRaises(FileNotFoundError):resolve_codex()


if __name__ == '__main__':
    unittest.main()
