"""Local ERP response test. Never calls Teams or sends a message."""
import json
import sys
from payables import ROOT
from erp_teams import context, worker_config

MARKETING=ROOT.parent/'Marketing EFS'
sys.path.insert(0,str(MARKETING/'scripts/operations'))
from appserver import AppServer

policy=json.loads((ROOT/'config/access.json').read_text(encoding='utf-8'))
transport={'tenant_id':policy['tenant_id'],'owner_id':policy['operations']['user_id'],
           'owner_email':policy['operations']['email']}
reader=policy['financial_readers'][0]
binding={'peer_id':reader['user_id'],'peer_email':reader['email']}
payload,financial=context(binding,transport,'ERP, quali fatture risultano da pagare?')
if not financial:raise RuntimeError('test_snapshot_not_current')
client=AppServer('C:/Users/Operations/AppData/Local/OpenAI/Codex/bin/f544b3844e0f14e9/codex.exe',
                 MARKETING,worker_config(MARKETING))
try:
    instructions=(MARKETING/'scripts/operations/coordinator.md').read_text(encoding='utf-8')
    thread=client.start_thread(instructions,{'model_reasoning_effort':'low'})
    answer=client.answer(thread,'Richiesta Teams verificata: ERP, quali fatture risultano da pagare?\n'
                         +'Risultato ERP del trasporto verificato:\n'+json.dumps(payload,ensure_ascii=False))
    if 'Agente ERP EFS' not in answer['delegated_roles'] or answer['agent']!='Agente ERP EFS':
        raise RuntimeError('exact_erp_specialist_not_verified')
    output=ROOT/'.local/maintenance/temporary/erp-agent-probe.json'
    output.write_text(json.dumps(answer,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'agent':answer['agent'],'delegated_roles':answer['delegated_roles'],
                      'elapsed_seconds':answer['elapsed_seconds'],'result_path':str(output)},ensure_ascii=False))
finally:
    client.close()
