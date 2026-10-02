"""Windows logon launcher; stdlib only. One watchdog per workspace."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/'.local/operations-teams'

def main():
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
        codex=Path('C:/Users/Operations/AppData/Local/OpenAI/Codex/bin/a51e250fa15c740a/codex.exe')
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
