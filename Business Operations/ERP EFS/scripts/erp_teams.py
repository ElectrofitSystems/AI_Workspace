"""Financial data gate for the existing verified Operations Teams transport."""
from __future__ import annotations
import json
import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from payables import ROOT, SNAPSHOT, validate_snapshot

class AccessDenied(PermissionError):
    pass

def authorize(binding, transport_config, access_path=None):
    policy = json.loads((access_path or ROOT / 'config/access.json').read_text(encoding='utf-8-sig'))
    owner = policy['operations']
    if (transport_config.get('tenant_id') != policy['tenant_id'] or
        transport_config.get('owner_id') != owner['user_id'] or
        transport_config.get('owner_email', '').lower() != owner['email']):
        raise AccessDenied('wrong_transport_identity')
    matched = [u for u in policy['financial_readers']
               if u.get('scope') == 'supplier_payables_read'
               and u.get('user_id') == binding.get('peer_id')
               and u.get('email', '').lower() == binding.get('peer_email', '').strip().lower()]
    if len(matched) != 1:
        raise AccessDenied('financial_reader_not_authorized')
    return matched[0]

def erp_intent(text):
    # Intent is routing only; it never grants access.
    return bool(re.search(r'\b(erp|esolver|scadenz\w*|fattur\w*|pagament\w*|pagare|bonific\w*|debiti|crediti|fornitor\w*)\b', text or '', re.I))

def context(binding, transport_config, text, prior_erp=False, *, access_path=None,
            snapshot_path=None, clock=None):
    try:
        authorize(binding, transport_config, access_path)
    except (AccessDenied, OSError, ValueError, KeyError):
        return {'financial_access': False, 'status': 'access_denied'}, False
    if not (prior_erp or erp_intent(text)):
        return {'financial_access': True, 'status': 'not_requested'}, False
    try:
        snapshot = json.loads((snapshot_path or SNAPSHOT).read_text(encoding='utf-8'))
        summary = validate_snapshot(snapshot)
        instant = clock or datetime.now(timezone.utc)
        acquired = datetime.fromisoformat(snapshot['acquired_at']).astimezone(timezone.utc)
        age = (instant - acquired).total_seconds()
        if age < -60 or age > 86400 or snapshot['as_of'] != instant.astimezone(ZoneInfo('Europe/Rome')).date().isoformat():
            return {'financial_access': True, 'status': 'snapshot_stale',
                    'as_of': snapshot['as_of'], 'acquired_at': snapshot['acquired_at'],
                    'automatic_refresh': False}, False
        return {'financial_access': True, 'status': 'available_snapshot',
                'data': snapshot, 'summary': summary,
                'limitations': ['Dati da esportazione datata; aggiornamento automatico non configurato.',
                                'Valuta di conto non verificata: importi in UdC, non dichiarare EUR.',
                                'Stati e blocchi non validati; nessuna proposta automatica di bonifico.',
                                'Distinte non contabilizzate escluse dalla vista iniziale.',
                                'Partite aperte storiche da riconciliare con amministrazione.']}, True
    except (OSError, ValueError, KeyError, TypeError):
        return {'financial_access': True, 'status': 'snapshot_unavailable'}, False

def assert_delivery(binding, transport_config, access_path=None):
    authorize(binding, transport_config, access_path)

def safe_read_roots(marketing_root):
    marketing_root = Path(marketing_root)
    # Neither ERP financial folders nor any user's authentication/history is readable.
    return [str(p) for p in (marketing_root / 'README.md', marketing_root / 'AGENTS.md',
                            marketing_root / 'docs', marketing_root / 'scripts/operations',
                            marketing_root / '.codex/agents', ROOT / 'README.md', ROOT / 'AGENTS.md',
                            ROOT / 'docs', ROOT / 'config', ROOT / '.codex/agents',
                            Path.home() / '.codex/agents')]


def worker_config(marketing_root):
    # Native Windows requires root read; explicit deny rules protect data.
    filesystem={':root':'read', ':minimal':'read'}
    private=[ROOT/'input', ROOT/'output', ROOT/'.local',
             Path(marketing_root)/'.local', Path.home()/'.codex/auth.json',
             Path.home()/'.codex/sessions', Path.home()/'.codex/archived_sessions',
             Path.home()/'.codex/log', Path.home()/'.codex/history.jsonl',
             Path.home()/'.codex/state_5.sqlite', Path.home()/'Desktop',
             Path.home()/'Downloads']
    filesystem.update({p.as_posix():'deny' for p in private})
    filesystem.update({Path(p).as_posix():'read' for p in safe_read_roots(marketing_root)})
    user_config=tomllib.loads((Path.home()/'.codex/config.toml').read_text(encoding='utf-8-sig'))
    return {'default_permissions':'operations_teams',
            'permissions.operations_teams.filesystem':filesystem,
            'permissions.operations_teams.network.enabled':False,
            'features.apps':False, 'mcp_servers.node_repl.enabled':False,
            'mcp_servers':{name:{'enabled':False} for name in user_config.get('mcp_servers',{})},
            'plugins':{name:{'enabled':False} for name in user_config.get('plugins',{})},
            'allow_browser_and_computer_use':False, 'web_search':'disabled'}
