"""Artifact-capable Marketing sessions for verified internal efitsys.com colleagues."""
from __future__ import annotations
import json
import os
import re
from pathlib import Path

POLICY=Path(__file__).with_name('marketing-access.json')

def restricted_config(base_config,marketing_root):
    """Keep private service data denied without a machine-wide deny on scratch parents."""
    root=Path(marketing_root).resolve()
    name=base_config['default_permissions']
    files=base_config[f'permissions.{name}.filesystem']
    files[(root/'.local').as_posix()]='read'
    files[(root/'.local/operations-teams').as_posix()]='deny'
    files[(root/'.local/myavatar').as_posix()]='deny'
    return base_config

def authorized(binding, transport, policy_path=POLICY):
    try:
        policy=json.loads(Path(policy_path).read_text(encoding='utf-8'))
        owner=policy['operations']
        return bool(policy.get('enabled') and
            transport.get('tenant_id')==policy['tenant_id'] and
            transport.get('owner_id')==owner['user_id'] and
            transport.get('owner_email','').lower()==owner['email'] and
            binding.get('peer_id') and
            isinstance(binding.get('peer_email'),str) and
            re.fullmatch(r'[^@\s]+@efitsys\.com',binding['peer_email'].strip(),re.I) and
            binding['peer_email'].strip().lower().rsplit('@',1)[-1] in policy['allowed_domains'])
    except (OSError,ValueError,KeyError,TypeError):
        return False

def worker_config(marketing_root):
    """Inherit installed skills/plugins, allow only Marketing artifact writes.

    The default Operations/ERP worker is unchanged. The service invokes this
    profile only after verify_chat and exact identity binding, never on message text.
    """
    root=Path(marketing_root).resolve()
    home=Path.home()
    files={':root':'read',':minimal':'read'}
    # Windows helpers must traverse .local/maintenance to enter the writable
    # scratch directory. A deny on .local itself also blocked that traversal.
    for path in (root/'.local/operations-teams',root/'.local/myavatar',
                 root.parent/'ERP EFS/input',root.parent/'ERP EFS/output',
                 root.parent/'ERP EFS/.local',home/'.codex/auth.json',
                 home/'.codex/sessions',home/'.codex/archived_sessions',
                 home/'.codex/log',home/'.codex/history.jsonl',home/'.codex/state_5.sqlite',
                 home/'Desktop',home/'Downloads'):
        files[path.as_posix()]='deny'
    files[(root/'.local').as_posix()]='read'
    files[(root/'.local/maintenance').as_posix()]='read'
    for path in (root/'input',root/'output',root/'.local/maintenance/temporary'):
        files[path.as_posix()]='write'
    if os.environ.get('TEMP'):
        files[Path(os.environ['TEMP']).as_posix()]='write'
    return {'default_permissions':'operations_marketing_internal',
            'permissions.operations_marketing_internal.filesystem':files,
            'permissions.operations_marketing_internal.network.enabled':True,
            'features.apps':True,'features.plugins':True,
            'features.shell_tool':True,'skills.include_instructions':True,
            'skills.bundled.enabled':True,'agents.enabled':True,
            'web_search':'live'}

def instructions(marketing_root):
    return (Path(marketing_root)/'scripts/operations/marketing-coordinator.md').read_text(encoding='utf-8')
