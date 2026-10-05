"""Verify the existing Teams identity on the selected runtime; never send."""
import json
import sys
from payables import ROOT
MARKETING=ROOT.parent/'Marketing EFS'
sys.path.insert(0,str(MARKETING/'scripts/operations'))
from appserver import AppServer
policy=json.loads((ROOT/'config/access.json').read_text(encoding='utf-8'))
client=AppServer('C:/Users/Operations/AppData/Local/OpenAI/Codex/bin/f544b3844e0f14e9/codex.exe',MARKETING)
try:
    thread=client.start_thread()
    profile=client.tool(thread,'get_profile',{})
    if profile.get('id')!=policy['operations']['user_id'] or profile.get('email','').lower()!=policy['operations']['email']:
        raise RuntimeError('wrong_authenticated_operations_account')
    print('Teams Operations identity verified; no message sent.')
finally:
    client.close()
