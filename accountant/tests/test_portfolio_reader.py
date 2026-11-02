"""Integration tests for portfolio snapshot reading and fallback handling."""

import unittest
from unittest.mock import patch

from scripts.portfolio import get_current_unrealized_pnl, get_initial_risk_pool


class TestPortfolioReader(unittest.TestCase):
    def test_get_initial_risk_pool(self) -> None:
        pool = get_initial_risk_pool()
        self.assertEqual(pool["Faiz"], 10_000_000)
        self.assertEqual(pool["Jimmy"], 1_140_313)
        self.assertEqual(pool["Oscar"], 2_000_000)
        self.assertEqual(pool["Wahyu"], 1_500_000)
        self.assertEqual(sum(pool.values()), 14_640_313)

    @patch("scripts.portfolio.read_kotrade_live_snapshot")
    def test_get_unrealized_pnl_live_success(self, mock_live) -> None:
        mock_live.return_value = {
            "summary": {
                "unrealized_pnl": 947563,
            }
        }
        pnl = get_current_unrealized_pnl()
        self.assertEqual(pnl, 947563)

    @patch("scripts.portfolio.read_kotrade_live_snapshot")
    def test_get_unrealized_pnl_fallback_on_error(self, mock_live) -> None:
        mock_live.side_effect = RuntimeError("Broker connection timeout")
        pnl = get_current_unrealized_pnl()
        # Fallback should return the verified baseline or cached figure
        self.assertEqual(pnl, 947563)


if __name__ == "__main__":
    unittest.main()
