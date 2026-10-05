"""One read-only app-server probe; prints no invoice or authentication content."""
import json
import sys
from pathlib import Path
from erp_teams import worker_config
from payables import ROOT

MARKETING = ROOT.parent / 'Marketing EFS'
sys.path.insert(0, str(MARKETING / 'scripts/operations'))
from appserver import AppServer

EXECUTABLE = sys.argv[1] if len(sys.argv)>1 else 'C:/Users/Operations/AppData/Local/OpenAI/Codex/bin/f544b3844e0f14e9/codex.exe'
client = AppServer(EXECUTABLE, MARKETING, worker_config(MARKETING))
try:
    # Reading the public project instructions must work; financial files must not.
    for label, path in [('instructions', ROOT/'README.md'),
                        ('financial_snapshot', ROOT/'.local/erp/payables-latest.json'),
                        ('original_export', ROOT/'input/esolver/erp20261005.xlsx'),
                        ('financial_report', ROOT/'output/payables/scadenzario-fornitori-2026-10-05.txt'),
                        ('transport_state',MARKETING/'.local/operations-teams/config.json')]:
        command = "try { $erpProbeLength = Get-Content -LiteralPath '" + str(path) + "' -ErrorAction Stop | Measure-Object; Write-Output 'readable'; exit 0 } catch { Write-Output $_.Exception.Message; exit 1 }"
        result = client.request('command/exec', {'command': ['powershell.exe', '-NoProfile', '-Command', command],
                                                'cwd': str(MARKETING), 'timeoutMs': 10000})
        print(json.dumps({'probe': label, 'result': result}, ensure_ascii=False))
        expected=0 if label=='instructions' else 1
        if result['exitCode']!=expected:raise RuntimeError('permission_probe_failed:'+label)
finally:
    client.close()
