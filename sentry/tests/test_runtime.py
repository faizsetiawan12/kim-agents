"""Exercise the real supervisor with fake external processes and Telegram transport."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
import runtime
from operations import Store


class SupervisorTest(unittest.TestCase):
    def test_failed_external_worker_exhausts_budget_and_notifies(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            (home/'runtime').mkdir()
            binaries = home/'bin'; binaries.mkdir()
            # Test doubles replace actual systemd/model processes, not incident logic.
            for name, text in [('systemctl', '#!/bin/sh\nexit 3\n'), ('hermes', '#!/bin/sh\nkill -KILL $$\n')]:
                path = binaries/name; path.write_text(text);path.chmod(0o700)
            store = Store(home/'runtime/state.sqlite'); self.addCleanup(store.close)
            runtime.initialize(store)
            store.observe('AI gateway', False, 'Unavailable.')
            sent=[]
            with patch.dict(os.environ, {'PATH':str(binaries)+':'+os.environ['PATH']}), patch.object(runtime, 'send_telegram', sent.append):
                runtime.repair(store,home)
                runtime.repair(store,home)
                runtime.repair(store,home)
            self.assertEqual(store.status()[0]['repair_attempts'],2)
            self.assertTrue(any('Your help is needed' in body for body in sent))
            self.assertFalse(any('restored' in body for body in sent))

    def test_pause_survives_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'state.sqlite'
            store=Store(path);runtime.control(store,'pause');store.close()
            store=Store(path);self.addCleanup(store.close)
            self.assertTrue(runtime.paused(store))
            runtime.control(store,'resume')
            self.assertFalse(runtime.paused(store))

    def test_incident_approval_preserves_budget(self):
        with tempfile.TemporaryDirectory() as temp:
            store=Store(Path(temp)/'state.sqlite');self.addCleanup(store.close)
            store.observe('AI gateway',False,'Unavailable.')
            incident=store.status()[0]['incident_id']
            self.assertEqual(store.claim_repair('AI gateway'),1)
            store.outcome('AI gateway',{'status':'blocked','summary':'Approve a specific configuration change.'})
            self.assertIsNone(store.claim_repair('AI gateway'))
            self.assertIn('Blocked:',runtime.status(store))
            runtime.approve_repair(store,incident,'Apply the proposed configuration change.')
            self.assertEqual(store.claim_repair('AI gateway'),2)
            self.assertIsNone(store.claim_repair('AI gateway'))
            self.assertIn('Two attempts',runtime.approve_repair(store,incident,'Retry the investigation.'))
