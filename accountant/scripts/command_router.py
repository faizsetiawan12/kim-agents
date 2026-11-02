"""Top-level dispatcher for the 4 strict slash commands. No I/O except via handlers."""

from __future__ import annotations

from typing import Any

from scripts.balance import format_balance_reply, format_sheet_reply, read_balances
from scripts.deposit_handler import execute_deposit_workflow
from scripts.router import COMMANDS, parse_command
from scripts.withdraw_handler import execute_withdrawal_workflow

HELP = (
    "Perintah yang tersedia:\n"
    "`/withdraw <nominal>` — tarik kas (contoh: `/withdraw 1jt`)\n"
    "`/deposit <nominal>` — setor modal (contoh: `/deposit 5jt`)\n"
    "`/sheet` — link buku RDN\n"
    "`/balance` — saldo semua owner"
)


def dispatch(
    text: str,
    sender_name: str,
    sheet_id: str | None = None,
    write_sheet: bool = True,
) -> dict[str, Any]:
    """Route strict slash-command text to its handler. Anything else gets help."""
    parsed = parse_command(text)
    if not parsed:
        return {"success": False, "message": f"⚠️ Perintah tidak dikenali.\n\n{HELP}"}

    if parsed["command"] == "/withdraw":
        return execute_withdrawal_workflow(text, sender_name, sheet_id, write_sheet)
    if parsed["command"] == "/deposit":
        return execute_deposit_workflow(text, sender_name, sheet_id, write_sheet)
    if parsed["command"] == "/sheet":
        return {"success": True, "message": format_sheet_reply(sheet_id)}
    if parsed["command"] == "/balance":
        try:
            return {
                "success": True,
                "message": format_balance_reply(read_balances(sheet_id)),
            }
        except Exception as exc:
            return {"success": False, "message": f"⚠️ Gagal membaca saldo: {exc}"}
    return {"success": False, "message": f"⚠️ Perintah tidak dikenali.\n\n{HELP}"}
