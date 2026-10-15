"""Windows logon launcher; stdlib only. One watchdog per workspace."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from runtime_paths import resolve_codex
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/'.local/operations-teams'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex',type=Path)
    args=parser.parse_args()
    if not (STATE/'service.enabled').exists():
        return
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
                # Resolve again on every restart after desktop updates.
                try:codex=resolve_codex(args.codex)
                except FileNotFoundError:
                    # A desktop updater may briefly remove the old distribution.
                    (STATE/'watchdog-runtime.json').write_text(json.dumps({'status':'waiting_for_installed_runtime','at':time.time()}),encoding='utf-8')
                    time.sleep(5)
                    continue
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
