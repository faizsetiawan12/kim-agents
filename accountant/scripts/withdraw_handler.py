"""Handler for the /withdraw command and withdrawal workflow."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from scripts.book import (
    build_withdrawal_journal_entries,
    calculate_withdrawal,
    format_withdrawal_alert,
    parse_withdraw_command,
)
from scripts.portfolio import get_current_unrealized_pnl, get_initial_risk_pool
from scripts.sheet_ops import append_journal_rows

_WIB = ZoneInfo("Asia/Jakarta")
SHEET_ID_ENV = "KIM_RDN_SHEET_ID"


def execute_withdrawal_workflow(
    text: str,
    sender_name: str,
    sheet_id: str | None = None,
    write_sheet: bool = True,
) -> dict[str, Any]:
    """Process a withdrawal request from chat.

    1. Parse amount from text.
    2. Identify owner from sender.
    3. Calculate proportional equity and profit breakdown.
    4. Write journal rows to Google Sheet if write_sheet is True.
    5. Return formatted message and computation payload.
    """
    amount = parse_withdraw_command(text)
    if not amount:
        return {
            "success": False,
            "message": "⚠️ Format tidak dikenali. Gunakan contoh: `/withdraw 1000000` atau `tarik 1jt`.",
        }

    owner = sender_name.capitalize()
    risk_pool = get_initial_risk_pool()

    if owner not in risk_pool:
        return {
            "success": False,
            "message": f"⚠️ Akun {owner} tidak terdaftar dalam pool risiko RDN awal.",
        }

    unrealized_pnl = get_current_unrealized_pnl()

    try:
        calc = calculate_withdrawal(
            owner=owner,
            requested_net_rp=amount,
            old_pool_deposits=risk_pool,
            unrealized_pnl=unrealized_pnl,
            idle_cash_provider="Faiz",
        )
    except ValueError as exc:
        return {
            "success": False,
            "message": f"⚠️ Penarikan ditolak: {exc}",
        }

    now_str = datetime.now(_WIB).strftime("%Y-%m-%d %H:%M WIB")
    entries = build_withdrawal_journal_entries(calc, date_wib=now_str, who_pasted=owner)

    target_sheet_id = sheet_id or os.environ.get(SHEET_ID_ENV)
    sheet_result = None
    if write_sheet:
        if not target_sheet_id:
            raise KeyError(f"{SHEET_ID_ENV} is not set. Cannot record withdrawal to Google Sheet.")
        try:
            sheet_result = append_journal_rows(sheet_id=target_sheet_id, rows=entries)
        except Exception as exc:
            return {
                "success": False,
                "message": f"⚠️ Gagal mencatat ke Google Sheet: {exc}",
                "calc": calc,
            }

    alert_message = format_withdrawal_alert(calc)
    return {
        "success": True,
        "message": alert_message,
        "calc": calc,
        "entries": entries,
        "sheet_result": sheet_result,
    }
