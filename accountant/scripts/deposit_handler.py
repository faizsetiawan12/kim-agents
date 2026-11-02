"""Handler for the /deposit command. Appends one Journal deposit row."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from scripts.router import parse_command, parse_nominal
from scripts.sheet_ops import append_journal_rows

_WIB = ZoneInfo("Asia/Jakarta")
SHEET_ID_ENV = "KIM_RDN_SHEET_ID"


def execute_deposit_workflow(
    text: str,
    sender_name: str,
    sheet_id: str | None = None,
    write_sheet: bool = True,
) -> dict[str, Any]:
    """Process `/deposit <nominal>`. Owner is always the sender."""
    parsed = parse_command(text)
    if not parsed or parsed["command"] != "/deposit":
        return {
            "success": False,
            "message": "⚠️ Format tidak dikenali. Gunakan: `/deposit <nominal>` (contoh: `/deposit 5jt`).",
        }
    amount = parse_nominal(parsed["arg"])
    if not amount:
        return {
            "success": False,
            "message": "⚠️ Nominal tidak dikenali. Gunakan: `/deposit <nominal>` (contoh: `/deposit 5jt`).",
        }

    owner = sender_name.capitalize()
    now_str = datetime.now(_WIB).strftime("%Y-%m-%d %H:%M WIB")
    entry = {
        "date_wib": now_str,
        "who_pasted": owner,
        "type": "deposit",
        "owner": owner,
        "amount": amount,
        "proof_text": "",
        "oscar_approved": "FALSE",
        "note": f"Deposit via /deposit command: Rp{amount:,}.",
    }

    target_sheet_id = sheet_id or os.environ.get(SHEET_ID_ENV)
    sheet_result = None
    if write_sheet:
        if not target_sheet_id:
            raise KeyError(f"{SHEET_ID_ENV} is not set. Cannot record deposit to Google Sheet.")
        try:
            sheet_result = append_journal_rows(sheet_id=target_sheet_id, rows=[entry])
        except Exception as exc:
            return {
                "success": False,
                "message": f"⚠️ Gagal mencatat ke Google Sheet: {exc}",
            }

    pretty = f"Rp{amount:,}".replace(",", ".")
    return {
        "success": True,
        "message": f"✅ *Tercatat*\ndeposit {owner} {pretty} ({now_str})",
        "entries": [entry],
        "sheet_result": sheet_result,
    }
