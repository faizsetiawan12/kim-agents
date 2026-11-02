"""Tests for withdraw handler workflow."""

import unittest
from unittest.mock import patch

from scripts.withdraw_handler import execute_withdrawal_workflow


class TestWithdrawHandler(unittest.TestCase):
    def test_invalid_command_text(self) -> None:
        res = execute_withdrawal_workflow("halo dunia", sender_name="Jimmy", write_sheet=False)
        self.assertFalse(res["success"])
        self.assertIn("Format tidak dikenali", res["message"])

    def test_unknown_sender(self) -> None:
        res = execute_withdrawal_workflow("/withdraw 1000000", sender_name="Budi", write_sheet=False)
        self.assertFalse(res["success"])
        self.assertIn("tidak terdaftar", res["message"])

    def test_overdraft_rejected(self) -> None:
        res = execute_withdrawal_workflow("/withdraw 5000000", sender_name="Jimmy", write_sheet=False)
        self.assertFalse(res["success"])
        self.assertIn("exceeds available equity", res["message"])

    @patch("scripts.withdraw_handler.append_journal_rows")
    def test_successful_withdrawal_execution(self, mock_append) -> None:
        mock_append.return_value = {"updatedRows": 4}
        res = execute_withdrawal_workflow(
            "/withdraw 1000000",
            sender_name="Jimmy",
            sheet_id="fake_sheet_id",
            write_sheet=True,
        )
        self.assertTrue(res["success"])
        self.assertIn("💸 *Withdrawal Request: Jimmy*", res["message"])
        self.assertIn("@Wahyu tolong transfer Rp1.000.000 ke Jimmy.", res["message"])
        self.assertEqual(len(res["entries"]), 4)
        mock_append.assert_called_once()


if __name__ == "__main__":
    unittest.main()
