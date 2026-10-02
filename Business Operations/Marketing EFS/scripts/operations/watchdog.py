"""Windows logon launcher; stdlib only. One watchdog per workspace."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/'.local/operations-teams'

def resolve_codex(explicit=None):
    value=explicit or os.environ.get('OPERATIONS_CODEX') or shutil.which('codex.exe')
    if not value or not Path(value).is_file():
        raise FileNotFoundError('Specify an existing Codex executable with --codex or OPERATIONS_CODEX.')
    return Path(value).resolve()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex',type=Path)
    args=parser.parse_args()
    if not (STATE/'service.enabled').exists():
        return
    codex=resolve_codex(args.codex)
    import msvcrt
    STATE.mkdir(parents=True,exist_ok=True)
    with (STATE/'watchdog.lock').open('a+b') as lock:
        lock.seek(0)
        lock.write(b'0')
        lock.flush()
        lock.seek(0)
        try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:return
        (STATE/'watchdog.json').write_text(json.dumps({'pid':os.getpid()}),encoding='utf-8')
        python=Path(sys.executable).with_name('python.exe')
        service=ROOT/'scripts/operations/teams_service.py'
        try:
            while (STATE/'service.enabled').exists():
                with (STATE/'errors.log').open('a',encoding='utf-8') as errors:
                    subprocess.run([str(python),str(service),'--codex',str(codex),'--live'],
                        cwd=ROOT,stdout=subprocess.DEVNULL,stderr=errors,
                        creationflags=subprocess.CREATE_NO_WINDOW)
                for _ in range(30):
                    if not (STATE/'service.enabled').exists():return
                    time.sleep(1)
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

if __name__=='__main__':main()
