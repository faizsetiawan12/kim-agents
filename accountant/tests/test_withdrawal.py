"""Tests for RDN withdrawal calculations, dilution handling, and journal entries."""

import unittest

from scripts.book import (
    calculate_withdrawal,
    format_withdrawal_alert,
    build_withdrawal_journal_entries,
    parse_withdraw_command,
    apply_entry,
)


class TestWithdrawalMath(unittest.TestCase):
    def setUp(self) -> None:
        # Initial pool deposits before Faiz's 110M idle cash
        self.old_pool_deposits = {
            "Faiz": 10_000_000,
            "Jimmy": 1_140_313,
            "Oscar": 2_000_000,
            "Wahyu": 1_500_000,
        }
        self.total_old_pool = sum(self.old_pool_deposits.values())  # 14,640,313
        self.unrealized_pnl = 947_563  # Kotrade current unrealized P&L

    def test_jimmy_full_equity_calculation(self) -> None:
        calc = calculate_withdrawal(
            owner="Jimmy",
            requested_net_rp=1_000_000,
            old_pool_deposits=self.old_pool_deposits,
            unrealized_pnl=self.unrealized_pnl,
            idle_cash_provider="Faiz",
        )
        # Verify share ratio is exactly 1,140,313 / 14,640,313 ~ 0.0778885
        self.assertAlmostEqual(calc["owner_share_ratio"], 1_140_313 / 14_640_313, places=5)

        # Gross profit attributable = share_ratio * 947,563 ~ 73,804
        self.assertEqual(calc["total_owner_gross_profit"], 73_804)
        self.assertEqual(calc["total_owner_fee"], 3_690)  # 5% of 73,804
        self.assertEqual(calc["total_owner_net_equity"], 1_210_427)  # 1,140,313 + 73,804 - 3,690

        # Payout breakdown: net requested is 1,000,000
        self.assertEqual(calc["net_payout_rp"], 1_000_000)
        self.assertEqual(calc["principal_withdrawn_rp"], 942_075)
        self.assertEqual(calc["profit_withdrawn_net_rp"], 57_925)
        self.assertEqual(calc["profit_withdrawn_gross_rp"], 60_973)
        self.assertEqual(calc["fee_withdrawn_rp"], 3_048)  # 5% of 60,973 is 3,048 (60,973 - 3,048 = 57,925)

        # Verify net payout equals principal + profit_net
        self.assertEqual(
            calc["principal_withdrawn_rp"] + calc["profit_withdrawn_net_rp"],
            calc["net_payout_rp"],
        )
        # Sisa equity Jimmy
        self.assertEqual(calc["remaining_equity_rp"], 210_427)
        # Buyout by Faiz
        self.assertEqual(calc["idle_cash_provider"], "Faiz")
        self.assertEqual(calc["buyout_principal_rp"], 942_075)

    def test_insufficient_equity_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            calculate_withdrawal(
                owner="Jimmy",
                requested_net_rp=2_000_000,  # exceeds 1,210,427
                old_pool_deposits=self.old_pool_deposits,
                unrealized_pnl=self.unrealized_pnl,
            )
        self.assertIn("exceeds available equity", str(ctx.exception))

    def test_unknown_owner_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            calculate_withdrawal(
                owner="UnknownUser",
                requested_net_rp=100_000,
                old_pool_deposits=self.old_pool_deposits,
                unrealized_pnl=self.unrealized_pnl,
            )
        self.assertIn("not found in old pool", str(ctx.exception))


class TestWithdrawalJournalEntries(unittest.TestCase):
    def test_journal_entries_structure(self) -> None:
        calc = {
            "owner": "Jimmy",
            "net_payout_rp": 1_000_000,
            "principal_withdrawn_rp": 942_083,
            "profit_withdrawn_gross_rp": 60_965,
            "fee_withdrawn_rp": 3_048,
            "profit_withdrawn_net_rp": 57_917,
            "remaining_equity_rp": 210_427,
            "idle_cash_provider": "Faiz",
            "buyout_principal_rp": 942_083,
        }
        date_wib = "2026-10-08 10:00 WIB"
        entries = build_withdrawal_journal_entries(calc, date_wib=date_wib)

        # Must produce 4 journal entries:
        # 1. Jimmy withdraw (principal)
        # 2. Jimmy realized-profit (gross)
        # 3. Jimmy fee-5pct
        # 4. Wahyu deposit (reinvested fee)
        self.assertEqual(len(entries), 4)

        e1, e2, e3, e4 = entries
        self.assertEqual(e1["type"], "withdraw")
        self.assertEqual(e1["owner"], "Jimmy")
        self.assertEqual(e1["amount"], 942_083)
        self.assertIn("principal withdrawn", e1["note"])

        self.assertEqual(e2["type"], "realized-profit")
        self.assertEqual(e2["owner"], "Jimmy")
        self.assertEqual(e2["amount"], 60_965)

        self.assertEqual(e3["type"], "fee-5pct")
        self.assertEqual(e3["owner"], "Jimmy")
        self.assertEqual(e3["amount"], 3_048)

        self.assertEqual(e4["type"], "deposit")
        self.assertEqual(e4["owner"], "Wahyu")
        self.assertEqual(e4["amount"], 3_048)
        self.assertIn("reinvest", e4["note"])

        # Test balance impact on Jimmy
        balances = {"Jimmy": 1_140_313, "Wahyu": 1_500_000, "Wahyu-fee": 0}
        for entry in entries:
            balances = apply_entry(balances, entry)

        # Net Jimmy change: -942_083 + 60_965 - 3_048 = -884_166
        # Expected new Jimmy balance = 1_140_313 - 884_166 = 256_147
        self.assertEqual(balances["Jimmy"], 1_140_313 - 884_166)
        # Wahyu got +3,048 deposit
        self.assertEqual(balances["Wahyu"], 1_503_048)


class TestParseAndFormat(unittest.TestCase):
    def test_parse_withdraw_command(self) -> None:
        self.assertEqual(parse_withdraw_command("/withdraw 1000000"), 1_000_000)
        self.assertEqual(parse_withdraw_command("/withdraw 1jt"), 1_000_000)
        self.assertEqual(parse_withdraw_command("/withdraw 1.000.000"), 1_000_000)
        self.assertEqual(parse_withdraw_command("/withdraw 500rb"), 500_000)
        self.assertEqual(parse_withdraw_command("tarik 1 juta"), 1_000_000)
        self.assertEqual(parse_withdraw_command("tarik saldo 1jt"), 1_000_000)
        self.assertEqual(parse_withdraw_command("tarik dana 2.5 juta"), 2_500_000)
        self.assertEqual(parse_withdraw_command("withdraw 2.5jt"), 2_500_000)
        self.assertIsNone(parse_withdraw_command("halo apa kabar"))

    def test_format_withdrawal_alert(self) -> None:
        calc = {
            "owner": "Jimmy",
            "net_payout_rp": 1_000_000,
            "principal_withdrawn_rp": 942_083,
            "profit_withdrawn_gross_rp": 60_965,
            "fee_withdrawn_rp": 3_048,
            "profit_withdrawn_net_rp": 57_917,
            "remaining_equity_rp": 210_427,
            "idle_cash_provider": "Faiz",
            "buyout_principal_rp": 942_083,
        }
        msg = format_withdrawal_alert(calc)
        self.assertIn("💸 *Withdrawal Request: Jimmy*", msg)
        self.assertIn("Kas Ditarik: Rp1.000.000", msg)
        self.assertIn("Modal Rp942.083", msg)
        self.assertIn("Profit Bersih Rp57.917", msg)
        self.assertIn("Fee Wahyu (5%): Rp3.048 (Reinvested)", msg)
        self.assertIn("Sisa Saldo Jimmy: Rp210.427", msg)
        self.assertIn("Buyout Kas: Faiz", msg)
        self.assertIn("@Wahyu tolong transfer Rp1.000.000 ke Jimmy.", msg)


if __name__ == "__main__":
    unittest.main()
