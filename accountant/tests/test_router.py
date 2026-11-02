"""Tests for the strict 4-command router."""

import unittest
from unittest.mock import patch

from scripts.command_router import dispatch
from scripts.router import COMMANDS, parse_command, parse_nominal


class TestParseCommand(unittest.TestCase):
    def test_commands_constant(self) -> None:
        self.assertEqual(COMMANDS, ("/withdraw", "/deposit", "/sheet", "/balance"))

    def test_strict_forms_accepted(self) -> None:
        self.assertEqual(
            parse_command("/withdraw 1jt"), {"command": "/withdraw", "arg": "1jt"}
        )
        self.assertEqual(
            parse_command("/deposit 5jt"), {"command": "/deposit", "arg": "5jt"}
        )
        self.assertEqual(parse_command("/sheet"), {"command": "/sheet", "arg": ""})
        self.assertEqual(parse_command("/balance"), {"command": "/balance", "arg": ""})

    def test_natural_language_rejected(self) -> None:
        self.assertIsNone(parse_command("gw mau withdraw 1 juta"))
        self.assertIsNone(parse_command("tarik 1 juta"))
        self.assertIsNone(parse_command("halo apa kabar"))
        self.assertIsNone(parse_command("/profit 500rb"))


class TestParseNominal(unittest.TestCase):
    def test_formats(self) -> None:
        self.assertEqual(parse_nominal("1000000"), 1_000_000)
        self.assertEqual(parse_nominal("1.000.000"), 1_000_000)
        self.assertEqual(parse_nominal("1jt"), 1_000_000)
        self.assertEqual(parse_nominal("2.5jt"), 2_500_000)
        self.assertEqual(parse_nominal("500rb"), 500_000)
        self.assertIsNone(parse_nominal("abc"))


class TestDispatch(unittest.TestCase):
    def test_unknown_gets_help(self) -> None:
        res = dispatch("gw mau withdraw 1 juta", "Jimmy", write_sheet=False)
        self.assertFalse(res["success"])
        self.assertIn("/withdraw <nominal>", res["message"])
        self.assertIn("/deposit <nominal>", res["message"])
        self.assertIn("/sheet", res["message"])
        self.assertIn("/balance", res["message"])

    def test_deposit_dry_run(self) -> None:
        res = dispatch("/deposit 5jt", "Faiz", write_sheet=False)
        self.assertTrue(res["success"])
        self.assertIn("deposit Faiz Rp5.000.000", res["message"])
        self.assertEqual(res["entries"][0]["type"], "deposit")
        self.assertEqual(res["entries"][0]["owner"], "Faiz")
        self.assertEqual(res["entries"][0]["amount"], 5_000_000)

    def test_withdraw_bad_nominal(self) -> None:
        res = dispatch("/withdraw abc", "Jimmy", write_sheet=False)
        self.assertFalse(res["success"])
        self.assertIn("/withdraw <nominal>", res["message"])

    @patch("scripts.command_router.read_balances")
    def test_balance(self, mock_bal) -> None:
        mock_bal.return_value = {
            "balances": {"Faiz": "Rp120.000.000", "Jimmy": "Rp1.140.313"},
            "sheet_link": "https://example/sheet",
        }
        res = dispatch("/balance", "Jimmy", write_sheet=False)
        self.assertTrue(res["success"])
        self.assertIn("Faiz: Rp120.000.000", res["message"])

    def test_sheet(self) -> None:
        res = dispatch("/sheet", "Jimmy", sheet_id="abc123", write_sheet=False)
        self.assertTrue(res["success"])
        self.assertIn("abc123", res["message"])


if __name__ == "__main__":
    unittest.main()
