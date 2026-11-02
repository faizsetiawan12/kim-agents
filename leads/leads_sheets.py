"""Read-only Google Sheets client for PM leads sheet. No writes, no RDN access."""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, "/home/faiz/.hermes/profiles/kim-accountant/workspace")

from scripts.google_sheets import get_access_token  # noqa: E402

LEADS_SHEET_ENV = "KIM_LEADS_SHEET_ID"
RDN_BOOK_ID = "1xSPJfRAfR0xj5FNeLGd_-kDXJoPunZa8Gu5bnMF6W-U"


def _leads_id() -> str:
    val = os.environ.get(LEADS_SHEET_ENV)
    assert val, f"{LEADS_SHEET_ENV} is not set"  # fail fast, no silent default
    assert val != RDN_BOOK_ID, "refusing RDN money book; use leads sheet only"
    return val


def read_range(tab: str, cell_range: str) -> list[list[str]]:
    """Read tab!range from leads sheet. Returns rows of cell strings."""
    token = get_access_token()
    encoded = urllib.parse.quote(f"{tab}!{cell_range}", safe="!:")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{_leads_id()}/values/{encoded}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8")).get("values", [])


def funnel_counts() -> dict[str, int]:
    """Count Tracker rows per Stage (col H)."""
    rows = read_range("Tracker", "H2:H1000")
    counts: dict[str, int] = {}
    for r in rows:
        stage = (r[0] if r else "").strip() or "Backlog"
        counts[stage] = counts.get(stage, 0) + 1
    return counts


if __name__ == "__main__":
    print(json.dumps(funnel_counts(), indent=1))
