"""Save a dated, readable local report from the reconciled ERP snapshot."""
import json
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo
from payables import ROOT, SNAPSHOT, validate_snapshot

def italian(value):
    return f'{Decimal(value):,.2f}'.replace(',','X').replace('.',',').replace('X','.')

data=json.loads(SNAPSHOT.read_text(encoding='utf-8'))
summary=validate_snapshot(data)
all_totals=summary['all']
acquired=datetime.fromisoformat(data['acquired_at']).astimezone(ZoneInfo('Europe/Rome'))
lines=['ELECTROFIT SYSTEMS - SCADENZARIO FORNITORI',
       'Situazione eSolver: '+data['as_of'],
       'Acquisito: '+acquired.strftime('%d/%m/%Y %H:%M:%S %Z'),
       'Fonte: eSolver EC742, ditta EL; '+data['source']['file']+' / '+data['source']['sheet']+' / '+data['source']['range'],
       '',str(all_totals['installments'])+' scadenze aperte; '+str(len(summary['by_supplier']))+' fornitori.',
       'Residui positivi: '+italian(all_totals['positive_udc'])+' UdC',
       'Note di credito/residui negativi: '+italian(all_totals['negative_udc'])+' UdC',
       'Saldo aritmetico netto: '+italian(all_totals['net_udc'])+' UdC',
       'Tutte le scadenze della vista risultano precedenti alla data di situazione.',
       '', 'LIMITI',
       'UdC = unita di conto; valuta della ditta non ancora verificata.',
       'Stati e blocchi non validati. Il saldo non e un totale di bonifici da eseguire.',
       'Distinte da contabilizzare, registrazioni provvisorie e avvisi parcella esclusi.',
       'Compensazioni con note di credito e partite storiche da riconciliare con amministrazione.',
       'Questo file non si aggiorna automaticamente.',
       '', 'RIEPILOGO PER FORNITORE (positivi | negativi | netto, tutti in UdC)']
for supplier in sorted(summary['by_supplier'],key=lambda s:Decimal(s['positive_udc']),reverse=True):
    lines.append(supplier['supplier']+' | '+italian(supplier['positive_udc'])+' | '
                 +italian(supplier['negative_udc'])+' | '+italian(supplier['net_udc']))
lines.extend(['','DETTAGLIO ORIGINALE DELLE SCADENZE',
              'Scadenza | Fornitore | Tipo / numero documento | Data documento | Residuo UdC | Pagamento | Riga fonte'])
for row in sorted(data['rows'],key=lambda r:(r['due_date'],r['supplier'],r['document_number'])):
    lines.append(' | '.join([row['due_date'],row['supplier'],row['document_type']+' / '+row['document_number'],
                             row['document_date'],italian(row['residual_udc']),row['payment_method'],str(row['source_row'])]))
lines.extend(['','Hash SHA256 originale: '+data['source']['sha256'],
              'Conteggio e netto verificati rispetto alla griglia eSolver.'])
destination=ROOT/'output/payables'/('scadenzario-fornitori-'+data['as_of']+'.txt')
destination.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(destination)
