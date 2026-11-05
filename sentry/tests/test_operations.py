import importlib.util
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('operations', pathlib.Path(__file__).parents[1] / 'operations.py')
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)


class OperationsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = ops.Store(pathlib.Path(self.tmp.name) / 'state.sqlite')
        self.addCleanup(self.store.close)

    def test_failure_deduplicates_and_recovery_reports_once(self):
        self.store.observe('gateway', False, 'Service did not respond.')
        self.store.observe('gateway', False, 'Service did not respond.')
        self.assertEqual(len(self.store.pending()), 1)
        self.store.observe('gateway', True, '')
        self.store.observe('gateway', True, '')
        self.assertEqual(len(self.store.pending()), 2)
        self.assertIn('restored', self.store.pending()[1][1])

    def test_two_attempts_survive_restart_and_block_third(self):
        self.store.observe('gateway', False, 'Service did not respond.')
        self.assertEqual(self.store.claim_repair('gateway'), 1)
        self.assertEqual(self.store.claim_repair('gateway'), 2)
        self.assertIsNone(self.store.claim_repair('gateway'))
        second = ops.Store(pathlib.Path(self.tmp.name) / 'state.sqlite')
        self.addCleanup(second.close)
        self.assertIsNone(second.claim_repair('gateway'))

    def test_failed_delivery_remains_pending(self):
        self.store.observe('gateway', False, 'Service did not respond.')
        def fail(text):
            raise OSError('offline')
        with self.assertRaises(OSError):
            self.store.deliver(fail)
        self.assertEqual(len(self.store.pending()), 1)
        sent = []
        self.store.deliver(sent.append)
        self.assertEqual(len(sent), 1)
        self.assertEqual(self.store.pending(), [])

    def test_recovery_closes_incident_and_next_failure_has_new_budget(self):
        self.store.observe('gateway', False, 'Unavailable.')
        self.store.claim_repair('gateway')
        self.store.observe('gateway', True, '')
        self.assertIsNone(self.store.claim_repair('gateway'))
        self.store.observe('gateway', False, 'Unavailable.')
        self.assertEqual(self.store.claim_repair('gateway'), 1)
