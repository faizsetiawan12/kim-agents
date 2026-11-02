"""Portfolio reader for KIM Ledger. Pure functions with graceful fallback."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from typing import Any

# Verified initial risk pool before Faiz's 110M idle cash
INITIAL_RISK_POOL_DEPOSITS = {
    "Faiz": 10_000_000,
    "Jimmy": 1_140_313,
    "Oscar": 2_000_000,
    "Wahyu": 1_500_000,
}

# Baseline verified unrealized P&L (2026-10-07 16:05 WIB)
FALLBACK_UNREALIZED_PNL = 947_563
KOTRADE_PYTHON = "/home/faiz/miniconda3/envs/kotrade/bin/python"


def get_initial_risk_pool() -> dict[str, int]:
    """Return immutable copy of the initial risk pool deposits."""
    return dict(INITIAL_RISK_POOL_DEPOSITS)


def read_kotrade_live_snapshot() -> dict[str, Any] | None:
    """Attempt to read live portfolio snapshot using Kotrade environment if available."""
    # First attempt: run via Kotrade's dedicated conda python environment to ensure dependencies exist
    try:
        cmd = [
            KOTRADE_PYTHON,
            "-c",
            (
                "import sys, json; "
                "sys.path.insert(0, '/home/faiz/KIM/repos/kotrade'); "
                "from modules.live_execution.scripts import portfolio; "
                "snap = portfolio.fetch_portfolio_snapshot(validate_session=False); "
                "print(json.dumps(snap))"
            ),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout.strip())
    except Exception as exc:
        logging.getLogger("ledger.portfolio").debug(
            "Subprocess Kotrade fetch failed or timed out: %s", exc
        )

    # In-process fallback attempt
    try:
        kotrade_path = "/home/faiz/KIM/repos/kotrade"
        if kotrade_path not in sys.path:
            sys.path.insert(0, kotrade_path)
        from modules.live_execution.scripts import portfolio as live_portfolio  # type: ignore

        return live_portfolio.fetch_portfolio_snapshot(validate_session=False)
    except Exception as exc:
        logging.getLogger("ledger.portfolio").debug(
            "In-process Kotrade fetch unavailable: %s", exc
        )

    return None


def get_current_unrealized_pnl() -> int:
    """Return live unrealized P&L from Kotrade, or fallback to the verified baseline."""
    try:
        snapshot = read_kotrade_live_snapshot()
        if snapshot and "summary" in snapshot:
            summary = snapshot["summary"]
            val = summary.get("unrealized_pnl")
            if val is not None:
                return int(round(float(val)))
    except Exception as exc:
        logging.getLogger("ledger.portfolio").error(
            "Error retrieving unrealized pnl: %s", exc
        )

    return FALLBACK_UNREALIZED_PNL
