"""Notion payload parsing and key loading, using a real page shape."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import notion_tasks  # noqa: E402

PAGE = {
    "properties": {
        "Name": {"title": [{"plain_text": "Debug failed Stockbit token collection"}]},
        "Status": {"select": {"name": "In Progress"}},
        "Owner": {"multi_select": [{"name": "Jimmy"}, {"name": "Wahyu"}]},
        "Timeline": {"date": {"start": "2026-10-03"}},
        "Last Update": {"date": {"start": "2026-11-02T09:14:00.000+07:00"}},
    }
}


class ParseTaskTest(unittest.TestCase):
    def test_reads_every_field(self):
        task = notion_tasks.parse_task(PAGE)
        self.assertEqual(task.name, "Debug failed Stockbit token collection")
        self.assertEqual(task.status, "In Progress")
        self.assertEqual(task.owners, ("Jimmy", "Wahyu"))
        self.assertEqual(task.timeline, date(2026, 10, 3))
        self.assertEqual(task.last_update, date(2026, 11, 2))

    def test_empty_values_do_not_crash(self):
        task = notion_tasks.parse_task(
            {"properties": {"Name": {"title": []}, "Status": {"select": None}, "Owner": {"multi_select": []}, "Timeline": {"date": None}}}
        )
        self.assertEqual(task.name, "")
        self.assertEqual(task.status, "")
        self.assertEqual(task.owners, ())
        self.assertIsNone(task.timeline)
        self.assertIsNone(task.last_update)


class LoadApiKeyTest(unittest.TestCase):
    def test_reads_value_from_environment(self):
        with mock.patch.dict("os.environ", {"NOTION_API_KEY": "secret_123"}):
            self.assertEqual(notion_tasks.load_api_key(), "secret_123")

    def test_missing_key_names_the_variable(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "NOTION_API_KEY"):
                notion_tasks.load_api_key()


if __name__ == "__main__":
    unittest.main()
