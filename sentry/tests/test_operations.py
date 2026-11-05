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
        self.assertIn('check passed again', self.store.pending()[1][1])

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
        self.store.confirm_recovery('gateway')
        self.assertIsNone(self.store.claim_repair('gateway'))
        self.store.observe('gateway', False, 'Unavailable.')
        self.assertEqual(self.store.claim_repair('gateway'), 1)

class ConcurrentOperationsTest(unittest.TestCase):
    def test_competing_checks_emit_one_alert(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as temp:
            db = pathlib.Path(temp) / 'state.sqlite'
            store = ops.Store(db)
            store.close()
            code = 'import sys;sys.path.insert(0,sys.argv[1]);from operations import Store;s=Store(sys.argv[2]);s.observe("gateway",False,"Unavailable.");s.close()'
            workers = [subprocess.Popen([sys.executable, '-c', code, str(pathlib.Path(__file__).parents[1]), str(db)]) for _ in range(4)]
            for worker in workers:
                self.assertEqual(worker.wait(timeout=10), 0)
            store = ops.Store(db)
            self.addCleanup(store.close)
            self.assertEqual(len(store.pending()), 1)

    def test_competing_delivery_sends_one_message(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as temp:
            db = pathlib.Path(temp) / 'state.sqlite'
            delivered = pathlib.Path(temp) / 'delivered.txt'
            store = ops.Store(db)
            store.observe('gateway', False, 'Unavailable.')
            store.close()
            code = '''import sys,time
sys.path.insert(0,sys.argv[1])
from operations import Store
s=Store(sys.argv[2])
def send(body):
    with open(sys.argv[3],'a') as output:output.write('sent\\n')
    time.sleep(.1)
s.deliver(send)
s.close()
'''
            workers = [subprocess.Popen([sys.executable, '-c', code, str(pathlib.Path(__file__).parents[1]), str(db), str(delivered)]) for _ in range(3)]
            for worker in workers:
                self.assertEqual(worker.wait(timeout=10), 0)
            self.assertEqual(delivered.read_text().splitlines(), ['sent'])

class IncidentEvidenceTest(unittest.TestCase):
    def test_liveness_does_not_reset_budget_and_links_survive_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            store=ops.Store(pathlib.Path(temp)/'state.sqlite');self.addCleanup(store.close)
            store.observe('gateway',False,'Unavailable.')
            incident=store.status()[0]['incident_id']
            store.claim_repair('gateway')
            store.outcome('gateway', {'status':'unresolved','issue_url':'https://example.test/issues/1'})
            store.observe('gateway',True,'')
            store.observe('gateway',False,'Unavailable.')
            self.assertEqual(store.status()[0]['incident_id'],incident)
            self.assertEqual(store.claim_repair('gateway'),2)
            store.outcome('gateway', {'status':'blocked','summary':'Access approval required.','issue_url':''})
            self.assertIn('https://example.test/issues/1',store.status()[0]['evidence'])
            self.assertIsNone(store.claim_repair('gateway'))
