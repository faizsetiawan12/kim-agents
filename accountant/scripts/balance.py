"""Balance and sheet-link helpers for KIM Accountant. No Sheet formula writes."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from scripts.google_sheets import get_access_token

SHEET_ID_ENV = "KIM_RDN_SHEET_ID"


def sheet_id() -> str:
    """Return the live RDN Sheet ID. Fail fast when env var is missing."""
    val = os.environ.get(SHEET_ID_ENV)
    assert val, f"{SHEET_ID_ENV} is not set"  # fail fast, no silent default
    return val


def sheet_link(sid: str | None = None) -> str:
    """Return the shareable Sheet URL for the live RDN book."""
    return f"https://docs.google.com/spreadsheets/d/{sid or sheet_id()}/edit"


def _read_range(sid: str, tab_range: str, token: str) -> list[list[str]]:
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/"
        f"{tab_range}"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8")).get("values", [])


def read_balances(sid: str | None = None, token: str | None = None) -> dict[str, Any]:
    """Read computed Ledger balances (formula-driven, read-only)."""
    target = sid or sheet_id()
    auth = token or get_access_token()
    rows = _read_range(target, "Ledger!A2:B6", auth)
    balances = {r[0]: r[1] if len(r) > 1 else "Rp0" for r in rows if r}
    return {"balances": balances, "sheet_link": sheet_link(target)}


def format_sheet_reply(sid: str | None = None) -> str:
    """Reply for /sheet: link only, no xlsx export."""
    return f"📄 *RDN Book*\n{sheet_link(sid)}"


def format_balance_reply(data: dict[str, Any]) -> str:
    """Reply for /balance: one bullet per owner, structured lines."""
    b = data.get("balances", {})
    owners = ("Faiz", "Jimmy", "Oscar", "Wahyu", "Wahyu-fee")
    lines = ["💰 *RDN Balance*"]
    lines.extend(f"• {o}: {b[o]}" for o in owners if o in b)
    lines.append(f"📄 {data.get('sheet_link', '')}")
    return "\n".join(lines)
