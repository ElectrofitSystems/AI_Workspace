import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from watchdog import resolve_codex


class RuntimePathTests(unittest.TestCase):
    def test_explicit_path_with_spaces_overrides_environment(self):
        with tempfile.TemporaryDirectory(prefix='operations runtime ') as directory:
            executable = Path(directory) / 'codex.exe'
            executable.touch()
            with patch.dict(os.environ, {'OPERATIONS_CODEX': 'missing-codex.exe'}):
                self.assertEqual(resolve_codex(executable), executable.resolve())

    def test_environment_path(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'codex.exe'
            executable.touch()
            with patch.dict(os.environ, {'OPERATIONS_CODEX': str(executable)}):
                self.assertEqual(resolve_codex(), executable.resolve())

    def test_path_lookup(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'codex.exe'
            executable.touch()
            with patch.dict(os.environ, {'OPERATIONS_CODEX': ''}), patch('watchdog.shutil.which', return_value=str(executable)):
                self.assertEqual(resolve_codex(), executable.resolve())

    def test_missing_explicit_executable_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('watchdog.shutil.which') as lookup:
                with self.assertRaises(FileNotFoundError):
                    resolve_codex(Path(directory) / 'missing.exe')
                lookup.assert_not_called()


if __name__ == '__main__':
    unittest.main()
