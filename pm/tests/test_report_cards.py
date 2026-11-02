"""Card rendering: grouping, overdue flagging, silence, and section layout."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pm_config  # noqa: E402
import report_cards  # noqa: E402
from notion_tasks import Task  # noqa: E402

TODAY = date(2026, 11, 2)


def task(name, status="In Progress", owners=("Faiz",), timeline=None, last_update=None):
    return Task(name=name, status=status, owners=owners, timeline=timeline, last_update=last_update)


class MorningCardTest(unittest.TestCase):
    def test_silent_when_nothing_is_active(self):
        tasks = [task("Backlog", "Todo"), task("Selesai", "Done", timeline=date(2026, 10, 1))]
        self.assertIsNone(report_cards.morning_card(tasks, TODAY))

    def test_groups_by_owner_with_whatsapp_tags(self):
        card = report_cards.morning_card(
            [task("A", owners=("Faiz",)), task("B", owners=("Oscar",))], TODAY
        )
        self.assertIn("@+628113112054", card)
        self.assertIn("@+628111929008", card)
        self.assertLess(card.index("@+628113112054"), card.index("@+628111929008"))

    def test_kim_owner_tags_every_principal(self):
        card = report_cards.morning_card([task("A", owners=("KIM",))], TODAY)
        for tag in pm_config.KIM_TAGS:
            self.assertIn(f"@{tag}", card)

    def test_overdue_is_flagged_and_sorted_first(self):
        card = report_cards.morning_card(
            [
                task("Nanti", timeline=date(2026, 11, 9)),
                task("Telat", timeline=date(2026, 10, 30)),
            ],
            TODAY,
        )
        self.assertIn("• 🔴 Telat (tenggat 30 Okt 2026)", card)
        self.assertLess(card.index("Telat"), card.index("Nanti"))

    def test_overdue_non_done_is_included_even_when_not_in_progress(self):
        card = report_cards.morning_card(
            [task("Blocked telat", "Blocked", timeline=date(2026, 10, 1))], TODAY
        )
        self.assertIn("🔴 Blocked telat", card)

    def test_missing_owner_gets_its_own_block(self):
        card = report_cards.morning_card([task("Tanpa", owners=())], TODAY)
        self.assertIn("Tanpa owner", card)
        self.assertIn("• Tanpa", card)

    def test_multi_owner_task_appears_under_each_owner(self):
        card = report_cards.morning_card([task("Bersama", owners=("Faiz", "Wahyu"))], TODAY)
        self.assertEqual(card.count("• Bersama"), 2)

    def test_footer_is_last_line(self):
        card = report_cards.morning_card([task("A")], TODAY)
        self.assertEqual(card.splitlines()[-1], "🕐 08:00 WIB · Progress hari ini pukul 18:00")


class EveningCardTest(unittest.TestCase):
    def test_sends_even_with_no_tasks(self):
        card = report_cards.evening_card([], TODAY)
        self.assertIn("📊 *Progress Hari Ini — 2 Nov 2026*", card)
        self.assertEqual(card.splitlines()[-1], "🕐 18:00 WIB · Fokus berikutnya besok 08:00")

    def test_done_today_section_lists_owner(self):
        card = report_cards.evening_card(
            [task("Selesai", "Done", last_update=TODAY)], TODAY
        )
        self.assertIn("Selesai hari ini\n• Selesai — Faiz", card)

    def test_done_on_another_day_is_not_listed(self):
        card = report_cards.evening_card(
            [task("Kemarin", "Done", last_update=date(2026, 11, 1))], TODAY
        )
        self.assertNotIn("Kemarin", card)

    def test_note_is_included_when_present(self):
        card = report_cards.evening_card([], TODAY, note="Oscar follow up Dylan Senin.")
        self.assertIn("Catatan hari ini\nOscar follow up Dylan Senin.", card)

    def test_note_section_absent_when_missing(self):
        card = report_cards.evening_card([], TODAY, note=None)
        self.assertNotIn("Catatan hari ini", card)

    def test_task_appears_once_when_both_in_progress_and_overdue(self):
        card = report_cards.evening_card(
            [task("Telat", timeline=date(2026, 10, 30))], TODAY
        )
        self.assertEqual(card.count("Telat"), 1)
        self.assertIn("• 🔴 Telat (tenggat 30 Okt 2026)", card)


class DateFormatTest(unittest.TestCase):
    def test_indonesian_month_names(self):
        self.assertEqual(report_cards.format_date(date(2026, 8, 1)), "1 Agu 2026")
        self.assertEqual(report_cards.format_date(date(2026, 12, 30)), "30 Des 2026")


if __name__ == "__main__":
    unittest.main()
