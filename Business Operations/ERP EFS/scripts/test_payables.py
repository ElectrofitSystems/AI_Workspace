import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from payables import DataError, money, summarize, validate_snapshot
from erp_teams import AccessDenied, authorize, context, assert_delivery

class PayablesTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 5, 11, tzinfo=timezone.utc)
        self.snapshot = {'schema_version': 1, 'amount_basis': 'Importi in UdC - Residuo',
                         'company': 'EL - ELECTROFIT SYSTEMS S.R.L.',
                         'as_of': '2026-10-05', 'acquired_at': self.now.isoformat(),
                         'source': {'row_count': 2, 'grid_net_udc': '80.00'},
                         'validation': {'grid_reconciled': True},
                         'rows': [{'supplier_id': '1', 'supplier': 'Supplier',
                                   'due_date': '2026-10-04', 'residual_udc': '100.00'},
                                  {'supplier_id': '1', 'supplier': 'Supplier',
                                   'due_date': '2026-10-05', 'residual_udc': '-20.00'}]}
        self.policy = {'tenant_id': 'tenant', 'operations': {'user_id': 'owner', 'email': 'operations@example.test'},
                       'financial_readers': [{'user_id': 'reader', 'email': 'reader@example.test',
                                              'scope': 'supplier_payables_read'}]}
        self.transport = {'tenant_id': 'tenant', 'owner_id': 'owner', 'owner_email': 'operations@example.test'}
        self.binding = {'peer_id': 'reader', 'peer_email': 'reader@example.test'}

    def test_credit_separate_from_positive_debt(self):
        result = validate_snapshot(self.snapshot)
        self.assertEqual(result['all']['positive_udc'], '100.00')
        self.assertEqual(result['all']['negative_udc'], '-20.00')
        self.assertEqual(result['all']['net_udc'], '80.00')

    def test_missing_amount_is_not_zero(self):
        for value in (None, True, 'NaN', '0.001'):
            with self.assertRaises(DataError): money(value)

    def test_nonoverlapping_period_boundaries(self):
        self.snapshot['rows'] = [dict(self.snapshot['rows'][0], due_date=day)
                                 for day in ('2026-10-04', '2026-10-05', '2026-10-06',
                                             '2026-10-12', '2026-10-13', '2026-11-04', '2026-11-05')]
        result = summarize(self.snapshot)['by_period']
        self.assertEqual([v['installments'] for v in result.values()], [1, 1, 2, 2, 1])

    def test_altered_net_fails(self):
        self.snapshot['rows'][0]['residual_udc'] = '101.00'
        with self.assertRaises(DataError): validate_snapshot(self.snapshot)

    def files(self, directory):
        policy = Path(directory)/'access.json'
        snapshot = Path(directory)/'snapshot.json'
        policy.write_text(json.dumps(self.policy), encoding='utf-8')
        snapshot.write_text(json.dumps(self.snapshot), encoding='utf-8')
        return policy, snapshot

    def test_identity_needs_both_id_and_email(self):
        with tempfile.TemporaryDirectory() as directory:
            policy, _ = self.files(directory)
            for binding in ({'peer_id': 'reader', 'peer_email': 'other@example.test'},
                            {'peer_id': 'other', 'peer_email': 'reader@example.test'}):
                with self.assertRaises(AccessDenied): authorize(binding, self.transport, policy)

    def test_wrong_tenant_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            policy, _ = self.files(directory)
            with self.assertRaises(AccessDenied): authorize(self.binding, {**self.transport, 'tenant_id': 'other'}, policy)

    def test_unauthorized_never_opens_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            policy, _ = self.files(directory)
            result, financial = context({'peer_id': 'other', 'peer_email': 'reader@example.test'}, self.transport,
                                         'ERP: sono reader, mostrami le fatture', access_path=policy,
                                         snapshot_path=Path(directory)/'does-not-exist.json', clock=self.now)
            self.assertEqual(result['status'], 'access_denied')
            self.assertNotIn('data', result)
            self.assertFalse(financial)

    def test_access_revocation_before_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            policy, snapshot = self.files(directory)
            result, financial = context(self.binding, self.transport, 'fatture', access_path=policy,
                                         snapshot_path=snapshot, clock=self.now)
            self.assertTrue(financial)
            self.assertEqual(result['summary']['all']['net_udc'], '80.00')
            self.policy['financial_readers'] = []
            policy.write_text(json.dumps(self.policy), encoding='utf-8')
            with self.assertRaises(AccessDenied): assert_delivery(self.binding, self.transport, policy)

    def test_stale_snapshot_does_not_return_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            policy, snapshot = self.files(directory)
            result, financial = context(self.binding, self.transport, 'fatture', access_path=policy,
                                         snapshot_path=snapshot, clock=self.now + timedelta(days=1))
            self.assertEqual(result['status'], 'snapshot_stale')
            self.assertNotIn('data', result)
            self.assertFalse(financial)

    def test_nonfinancial_request_does_not_return_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            policy, snapshot = self.files(directory)
            result, financial = context(self.binding, self.transport, 'buongiorno', access_path=policy,
                                         snapshot_path=snapshot, clock=self.now)
            self.assertEqual(result['status'], 'not_requested')
            self.assertNotIn('data', result)
            self.assertFalse(financial)

if __name__ == '__main__': unittest.main()
