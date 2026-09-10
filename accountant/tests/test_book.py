"""Tracer bullet: fee is 5% of realized profit, zero on loss."""

import unittest

from scripts.book import (
    apply_entry,
    fee_for_profit,
    reversing_allowed,
    signed_amount,
    validate_paste,
)


class TestFee(unittest.TestCase):
    def test_fee_example(self) -> None:
        self.assertEqual(fee_for_profit(10_000_000), 500_000)

    def test_no_fee_on_loss_or_zero(self) -> None:
        self.assertEqual(fee_for_profit(0), 0)
        self.assertEqual(fee_for_profit(-5_000_000), 0)


class TestValidate(unittest.TestCase):
    def test_missing_amount_rejected_but_proof_optional(self) -> None:
        errors = validate_paste({"date": "2026-09-09", "type": "deposit", "owner": "Faiz"})
        self.assertEqual(errors, ["missing amount"])

    def test_good_paste_accepted(self) -> None:
        errors = validate_paste(
            {
                "date": "2026-09-09",
                "type": "deposit",
                "owner": "Faiz",
                "amount": 100_000_000,
                "proof": "stockbit-abc",
            }
        )
        self.assertEqual(errors, [])


class TestRules(unittest.TestCase):
    def test_signed_amounts(self) -> None:
        self.assertEqual(signed_amount("deposit", 10_000_000), 10_000_000)
        self.assertEqual(signed_amount("realized-profit", 5_000_000), 5_000_000)
        self.assertEqual(signed_amount("realized-loss", 890), -890)
        self.assertEqual(signed_amount("fee-5pct", 250_000), -250_000)
        self.assertEqual(signed_amount("withdraw", 2_000_000), -2_000_000)
        self.assertEqual(signed_amount("reversing-entry", -10_000_000), -10_000_000)

    def test_q14_math(self) -> None:
        balances = {"Faiz": 0, "Jimmy": 0, "Oscar": 0, "Wahyu-fee": 0}
        balances = apply_entry(balances, {"type": "deposit", "owner": "Faiz", "amount": 100_000_000})
        balances = apply_entry(
            balances, {"type": "realized-profit", "owner": "Faiz", "amount": 10_000_000}
        )
        balances = apply_entry(
            balances, {"type": "fee-5pct", "owner": "Faiz", "amount": 500_000}
        )
        self.assertEqual(balances["Faiz"], 109_500_000)
        self.assertEqual(balances["Wahyu-fee"], 500_000)


if __name__ == "__main__":
    unittest.main()
