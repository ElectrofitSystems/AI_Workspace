"""Discover installed desktop runtimes without pinning a disappearing update hash."""
from pathlib import Path
import os,shutil,subprocess,json,tomllib,copy,time

def codex_candidates(explicit=None):
    home=Path.home()
    candidates=[]
    for value in (explicit,os.environ.get('OPERATIONS_CODEX'),os.environ.get('CODEX_CLI_PATH'),shutil.which('codex.exe')):
        if value:candidates.append(Path(value))
    candidates.extend((home/'AppData/Local/OpenAI/Codex/bin').glob('*/codex.exe'))
    seen=set();valid=[]
    for p in candidates:
        p=p.resolve()
        if str(p).lower() in seen or not p.is_file():continue
        seen.add(str(p).lower())
        # Bundled Windows distributions need the matching helper next to the CLI.
        if 'AppData/Local/OpenAI/Codex/bin' in p.as_posix() and not (p.parent/'codex-windows-sandbox-setup.exe').is_file():continue
        valid.append(p)
    return sorted(valid,key=lambda p:p.stat().st_mtime_ns,reverse=True)

def resolve_codex(explicit=None):
    for p in codex_candidates(explicit):
        try:
            check=subprocess.run([str(p),'--version'],capture_output=True,text=True,timeout=10,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            if check.returncode==0 and 'codex' in check.stdout.lower():return p
        except (OSError,subprocess.TimeoutExpired):pass
    raise FileNotFoundError('No healthy installed Codex CLI with matching Windows helper found.')

def refresh_node_reference(marketing_root):
    """Repair only a disappeared bundled node runtime, keeping all other config intact."""
    config=Path.home()/'.codex/config.toml'
    raw=config.read_text(encoding='utf-8-sig');before=tomllib.loads(raw)
    node=before.get('mcp_servers',{}).get('node_repl',{})
    command=node.get('command')
    if not isinstance(command,str) or Path(command).is_file():return False
    base=Path.home()/'AppData/Local/OpenAI/Codex/runtimes/cua_node'
    if not Path(command).resolve().is_relative_to(base.resolve()):return False
    candidates=[p for p in base.glob('*/bin/node_repl.exe') if (p.parent/'node.exe').is_file() and (p.parent/'node_modules').is_dir()]
    if not candidates:return False
    current=max(candidates,key=lambda p:p.stat().st_mtime_ns)
    oldbase=Path(command).parent;newbase=current.parent
    updated=raw
    for old,new in ((str(oldbase),str(newbase)),(oldbase.as_posix(),newbase.as_posix()),
                    (json.dumps(str(oldbase))[1:-1],json.dumps(str(newbase))[1:-1])):
        updated=updated.replace(old,new)
    after=tomllib.loads(updated)
    a=copy.deepcopy(before);b=copy.deepcopy(after)
    a['mcp_servers'].pop('node_repl');b['mcp_servers'].pop('node_repl')
    if a!=b or Path(after['mcp_servers']['node_repl']['command']).resolve()!=current.resolve():
        raise RuntimeError('Refusing node reference repair affecting unrelated configuration')
    backup=Path(marketing_root)/'.local/operations-teams'/('runtime-config-before-'+str(time.time_ns())+'.toml')
    backup.write_text(raw,encoding='utf-8')
    tmp=config.with_suffix('.maintenance.tmp');tmp.write_text(updated,encoding='utf-8');tmp.replace(config)
    return True

if __name__=='__main__':print(resolve_codex())
