"""Chat paragraph: log reading and model-failure behaviour."""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import chat_note  # noqa: E402

TODAY = date(2026, 11, 2)


class ReadLogTest(unittest.TestCase):
    def test_missing_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(chat_note.read_log(TODAY, Path(tmp)))

    def test_reads_today_file_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "group-chat-2026-11-01.md").write_text("- kemarin\n")
            self.assertIsNone(chat_note.read_log(TODAY, Path(tmp)))
            (Path(tmp) / "group-chat-2026-11-02.md").write_text("- hari ini\n")
            self.assertIn("hari ini", chat_note.read_log(TODAY, Path(tmp)))

    def test_keeps_only_the_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = [f"- baris {i}" for i in range(chat_note.MAX_LOG_LINES + 40)]
            (Path(tmp) / "group-chat-2026-11-02.md").write_text("\n".join(lines))
            log = chat_note.read_log(TODAY, Path(tmp))
            self.assertEqual(len(log.splitlines()), chat_note.MAX_LOG_LINES)
            self.assertIn(f"baris {chat_note.MAX_LOG_LINES + 39}", log)


class BuildNoteTest(unittest.TestCase):
    def test_no_log_means_no_note_and_no_model_call(self):
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            note = chat_note.build_note(TODAY, Path(tmp), run=lambda prompt: calls.append(prompt) or "x")
        self.assertIsNone(note)
        self.assertEqual(calls, [])

    def test_model_failure_still_renders_without_note(self):
        def boom(prompt):
            raise RuntimeError("model down")

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "group-chat-2026-11-02.md").write_text("- halo\n")
            self.assertIsNone(chat_note.build_note(TODAY, Path(tmp), run=boom))

    def test_dash_means_nothing_to_say(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "group-chat-2026-11-02.md").write_text("- halo\n")
            self.assertIsNone(chat_note.build_note(TODAY, Path(tmp), run=lambda prompt: " - "))

    def test_returns_paragraph_and_includes_log(self):
        seen = {}

        def fake(prompt):
            seen["prompt"] = prompt
            return "  Oscar follow up Dylan Senin.  "

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "group-chat-2026-11-02.md").write_text("- Oscar: follow up Dylan\n")
            note = chat_note.build_note(TODAY, Path(tmp), run=fake)
        self.assertEqual(note, "Oscar follow up Dylan Senin.")
        self.assertIn("follow up Dylan", seen["prompt"])


if __name__ == "__main__":
    unittest.main()
