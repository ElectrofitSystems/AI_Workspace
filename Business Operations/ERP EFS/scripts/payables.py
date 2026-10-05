"""Read an eSolver export; preserve originals and reconcile Decimal amounts."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / '.local/erp/payables-latest.json'
HEADERS = ['S', 'Scadenza bloccata', 'Annotazione scadenza', 'Scadenza',
           'Fornitore - Codice', 'Fornitore - Ragione sociale', 'Documento - Sigla',
           'Documento - Numero', 'Documento - Data', 'R.A.',
           'Importi in UdC - Residuo', 'Valuta origine',
           'Tipo pagamento - Codice', 'Tipo pagamento - Descrizione']

class DataError(ValueError):
    pass

def money(value):
    if value is None or isinstance(value, bool):
        raise DataError('missing_amount')
    try:
        amount = Decimal(str(value))
    except InvalidOperation as error:
        raise DataError('invalid_amount') from error
    if not amount.is_finite() or amount != amount.quantize(Decimal('.01')):
        raise DataError('invalid_amount_precision')
    return amount.quantize(Decimal('.01'))

def source_date(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    raise DataError('missing_or_invalid_date')

def read_export(path, as_of, expected_rows, expected_net):
    import openpyxl
    path = Path(path).resolve()
    # Only the explicitly selected original is opened. No formulas are evaluated.
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        if len(workbook.worksheets) != 1:
            raise DataError('unexpected_sheet_count')
        sheet = workbook.active
        values = list(sheet.values)
        headers = values[0]
        if len(set(headers)) != len(headers) or set(HEADERS) - set(headers):
            raise DataError('unexpected_export_columns')
        aging = 'Giorni scaduto al ' + date.fromisoformat(as_of).strftime('%d/%m/%Y')
        if aging not in headers or len(headers) != 15:
            raise DataError('as_of_date_or_columns_mismatch')
        rows, identities = [], set()
        for source_row, cells in enumerate(values[1:], 2):
            if any(isinstance(v, str) and v.startswith('=') for v in cells):
                raise DataError('unexpected_formula')
            row = dict(zip(headers, cells))
            if not row.get('Fornitore - Codice') or not row.get('Fornitore - Ragione sociale'):
                raise DataError('missing_supplier')
            due = source_date(row['Scadenza'])
            if row[aging] != (date.fromisoformat(as_of) - date.fromisoformat(due)).days:
                raise DataError('aging_mismatch')
            amount = money(row['Importi in UdC - Residuo'])
            document = str(row['Documento - Numero'] or '').strip()
            kind = str(row['Documento - Sigla'] or '').strip()
            if not document or kind not in ('FT', 'NC'):
                raise DataError('unknown_document_type_or_number')
            identity = (str(row['Fornitore - Codice']), kind, document,
                        source_date(row['Documento - Data']), due)
            if identity in identities:
                raise DataError('ambiguous_duplicate_installment')
            identities.add(identity)
            rows.append({
                'source_row': source_row, 'supplier_id': identity[0],
                'supplier': str(row['Fornitore - Ragione sociale']),
                'document_type': kind, 'document_number': document,
                'document_date': identity[3], 'due_date': due,
                'residual_udc': str(amount), 'state_raw': row['S'],
                'blocked_raw': row['Scadenza bloccata'],
                'annotation': row['Annotazione scadenza'],
                'original_currency': row['Valuta origine'],
                'withholding_raw': row['R.A.'],
                'payment_code': str(row['Tipo pagamento - Codice'] or ''),
                'payment_method': row['Tipo pagamento - Descrizione'],
            })
        if len(rows) != expected_rows:
            raise DataError('row_count_does_not_match_grid')
        net = sum((money(r['residual_udc']) for r in rows), Decimal('0.00'))
        if net != money(expected_net):
            raise DataError('net_does_not_match_grid')
        return {'schema_version': 1, 'company': 'EL - ELECTROFIT SYSTEMS S.R.L.',
                'as_of': as_of, 'acquired_at': datetime.now(timezone.utc).isoformat(),
                'account_currency': None, 'amount_basis': 'Importi in UdC - Residuo',
                'source': {'file': str(path.relative_to(ROOT)),
                           'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'sheet': sheet.title, 'range': 'A1:O' + str(len(values)),
                           'row_count': len(rows), 'grid_net_udc': str(net)},
                'filters': {'open': True, 'closed': False, 'supplier': 'all',
                            'due_from': None, 'due_to': '2099-12-31',
                            'blocked': 'all', 'unposted_payment_batches': False,
                            'provisional_entries': False, 'proforma_notices': False,
                            'original_currency_amounts': False},
                'validation': {'grid_reconciled': True, 'accounting_reconciled': False,
                               'state_codes_verified': False,
                               'currency_verified': False,
                               'automatic_refresh': False},
                'rows': rows}
    finally:
        workbook.close()

def totals(rows):
    positive = sum((money(r['residual_udc']) for r in rows if money(r['residual_udc']) > 0), Decimal('0.00'))
    negative = sum((money(r['residual_udc']) for r in rows if money(r['residual_udc']) < 0), Decimal('0.00'))
    return {'installments': len(rows), 'positive_udc': str(positive),
            'negative_udc': str(negative), 'net_udc': str(positive + negative)}

def summarize(snapshot):
    rows = snapshot['rows']
    today = date.fromisoformat(snapshot['as_of'])
    groups = {'overdue': [], 'due_today': [], 'next_7_days': [],
              'days_8_to_30': [], 'after_30_days': []}
    for row in rows:
        days = (date.fromisoformat(row['due_date']) - today).days
        key = ('overdue' if days < 0 else 'due_today' if days == 0 else
               'next_7_days' if days <= 7 else 'days_8_to_30' if days <= 30 else 'after_30_days')
        groups[key].append(row)
    suppliers = {}
    for row in rows:
        suppliers.setdefault((row['supplier_id'], row['supplier']), []).append(row)
    return {'all': totals(rows), 'by_period': {k: totals(v) for k, v in groups.items()},
            'by_supplier': [{'supplier_id': key[0], 'supplier': key[1], **totals(value)}
                            for key, value in sorted(suppliers.items(), key=lambda p:p[0][1])],
            'oldest_due': min((r['due_date'] for r in rows), default=None),
            'newest_due': max((r['due_date'] for r in rows), default=None)}

def validate_snapshot(snapshot):
    if snapshot.get('schema_version') != 1 or snapshot.get('amount_basis') != 'Importi in UdC - Residuo':
        raise DataError('unsupported_snapshot')
    if snapshot.get('company') != 'EL - ELECTROFIT SYSTEMS S.R.L.':
        raise DataError('wrong_company')
    if not snapshot.get('validation', {}).get('grid_reconciled'):
        raise DataError('unreconciled_snapshot')
    rows = snapshot['rows']
    for row in rows:
        date.fromisoformat(row['due_date'])
        money(row['residual_udc'])
    result = summarize(snapshot)
    if result['all']['installments'] != snapshot['source']['row_count']:
        raise DataError('snapshot_count_mismatch')
    if result['all']['net_udc'] != snapshot['source']['grid_net_udc']:
        raise DataError('snapshot_net_mismatch')
    return result

def write_snapshot(snapshot):
    result = validate_snapshot(snapshot)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    temporary = SNAPSHOT.with_suffix('.tmp')
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(SNAPSHOT)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--expected-rows', type=int, required=True)
    parser.add_argument('--expected-net', required=True)
    args = parser.parse_args()
    snapshot = read_export(args.source, args.as_of, args.expected_rows, args.expected_net)
    print(json.dumps(write_snapshot(snapshot), ensure_ascii=False, indent=2))
