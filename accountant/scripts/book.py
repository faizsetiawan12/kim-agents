"""RDN book rules: fee, validation, ledger, and withdrawal logic. Pure functions, no I/O."""

from __future__ import annotations

import re
from typing import Any

ALLOWED_TYPES = (
    "deposit",
    "realized-profit",
    "realized-loss",
    "fee-5pct",
    "withdraw",
    "reversing-entry",
)

ALLOWED_OWNERS = ("Faiz", "Jimmy", "Oscar", "Wahyu", "Wahyu-fee")


def fee_for_profit(profit_rp: int) -> int:
    """5% of realized profit. Zero when profit is zero or negative."""
    if profit_rp <= 0:
        return 0
    return profit_rp * 5 // 100


POSITIVE_TYPES = ("deposit", "realized-profit")


def signed_amount(kind: str, amount_rp: int) -> int:
    """Journal amount carries its effect sign; Ledger is a plain sum."""
    if kind in POSITIVE_TYPES:
        return abs(amount_rp)
    if kind == "reversing-entry":
        return amount_rp
    return -abs(amount_rp)


def validate_paste(entry: dict) -> list[str]:
    """Check inferred chat entry has required bookkeeping fields."""
    errors: list[str] = []
    for field in ("date", "type", "owner", "amount"):
        if not entry.get(field):
            errors.append(f"missing {field}")
    if entry.get("type") and entry["type"] not in ALLOWED_TYPES:
        errors.append("bad type")
    if entry.get("owner") and entry["owner"] not in ALLOWED_OWNERS:
        errors.append("bad owner")
    amount = entry.get("amount")
    if amount is not None and not isinstance(amount, int):
        errors.append("bad amount")
    return errors


def reversing_allowed(oscar_approved: bool) -> bool:
    """Reversing entries need Oscar's explicit approval."""
    return oscar_approved


def apply_entry(balances: dict, entry: dict) -> dict:
    """Apply one validated entry. Returns new balances, input untouched."""
    out = dict(balances)
    owner = entry["owner"]
    amount = entry["amount"]
    kind = entry["type"]
    if kind == "deposit" or kind == "realized-profit":
        out[owner] = out.get(owner, 0) + amount
    elif kind in ("withdraw", "realized-loss"):
        out[owner] = out.get(owner, 0) - amount
    elif kind == "fee-5pct":
        out[owner] = out.get(owner, 0) - amount
        out["Wahyu-fee"] = out.get("Wahyu-fee", 0) + amount
    elif kind == "reversing-entry":
        out[owner] = out.get(owner, 0) + amount
    return out


# ── WITHDRAWAL & DILUTION CALCULATIONS ──────────────────────────────────────────


def calculate_withdrawal(
    owner: str,
    requested_net_rp: int,
    old_pool_deposits: dict[str, int],
    unrealized_pnl: int,
    idle_cash_provider: str = "Faiz",
) -> dict[str, Any]:
    """Calculate proportional principal and profit withdrawal from the risk pool.

    Separates the old risk pool from idle cash to avoid dilution.
    Fee (5%) applies only to gross profit. Net payout = principal + net profit.
    """
    if owner not in old_pool_deposits:
        raise ValueError(f"Owner '{owner}' not found in old pool deposits.")

    total_old_pool = sum(old_pool_deposits.values())
    if total_old_pool <= 0:
        raise ValueError("Total old pool deposits must be positive.")

    owner_deposit = old_pool_deposits[owner]
    owner_share_ratio = owner_deposit / total_old_pool

    # Total gross profit attributable to this owner across open positions
    total_owner_gross_profit = round(owner_share_ratio * unrealized_pnl)
    total_owner_fee = fee_for_profit(total_owner_gross_profit)
    total_owner_net_profit = total_owner_gross_profit - total_owner_fee
    total_owner_net_equity = owner_deposit + total_owner_net_profit

    if requested_net_rp > total_owner_net_equity:
        raise ValueError(
            f"Requested withdrawal Rp{requested_net_rp:,} exceeds available equity "
            f"Rp{total_owner_net_equity:,} for {owner}."
        )

    # Proportional payout fraction
    payout_fraction = requested_net_rp / total_owner_net_equity if total_owner_net_equity > 0 else 0.0

    principal_withdrawn = round(owner_deposit * payout_fraction)
    # Net profit withdrawn is the remainder to guarantee exact requested net payout
    profit_withdrawn_net = requested_net_rp - principal_withdrawn

    # Gross profit and fee calculation:
    # profit_net = profit_gross * 0.95 => profit_gross = profit_net / 0.95
    if profit_withdrawn_net > 0:
        profit_withdrawn_gross = round(profit_withdrawn_net / 0.95)
        fee_withdrawn = fee_for_profit(profit_withdrawn_gross)
        # Adjust if rounding difference occurs
        if profit_withdrawn_gross - fee_withdrawn != profit_withdrawn_net:
            profit_withdrawn_gross = profit_withdrawn_net + fee_withdrawn
    else:
        profit_withdrawn_gross = 0
        fee_withdrawn = 0

    remaining_equity = total_owner_net_equity - requested_net_rp

    return {
        "owner": owner,
        "owner_share_ratio": owner_share_ratio,
        "total_owner_gross_profit": total_owner_gross_profit,
        "total_owner_fee": total_owner_fee,
        "total_owner_net_profit": total_owner_net_profit,
        "total_owner_net_equity": total_owner_net_equity,
        "net_payout_rp": requested_net_rp,
        "principal_withdrawn_rp": principal_withdrawn,
        "profit_withdrawn_net_rp": profit_withdrawn_net,
        "profit_withdrawn_gross_rp": profit_withdrawn_gross,
        "fee_withdrawn_rp": fee_withdrawn,
        "remaining_equity_rp": remaining_equity,
        "idle_cash_provider": idle_cash_provider,
        "buyout_principal_rp": principal_withdrawn,
    }


def build_withdrawal_journal_entries(
    calc: dict[str, Any],
    date_wib: str,
    who_pasted: str = "LedgerBot",
) -> list[dict[str, Any]]:
    """Build the 4 standard journal rows representing the withdrawal and reinvestment."""
    owner = calc["owner"]
    principal = calc["principal_withdrawn_rp"]
    profit_gross = calc["profit_withdrawn_gross_rp"]
    fee = calc["fee_withdrawn_rp"]
    net_payout = calc["net_payout_rp"]
    buyer = calc.get("idle_cash_provider", "Faiz")

    entries = [
        {
            "date_wib": date_wib,
            "who_pasted": who_pasted,
            "type": "withdraw",
            "owner": owner,
            "amount": principal,
            "proof_text": "",
            "oscar_approved": "TRUE",
            "note": (
                f"Withdrawal net Rp{net_payout:,}: principal withdrawn Rp{principal:,}. "
                f"Shares absorbed by {buyer}."
            ),
        },
        {
            "date_wib": date_wib,
            "who_pasted": who_pasted,
            "type": "realized-profit",
            "owner": owner,
            "amount": profit_gross,
            "proof_text": "",
            "oscar_approved": "TRUE",
            "note": f"Realized profit on withdrawal buyout: gross Rp{profit_gross:,}",
        },
        {
            "date_wib": date_wib,
            "who_pasted": who_pasted,
            "type": "fee-5pct",
            "owner": owner,
            "amount": fee,
            "proof_text": "",
            "oscar_approved": "TRUE",
            "note": f"5% profit fee owed to Wahyu on withdrawal profit: Rp{fee:,}",
        },
        {
            "date_wib": date_wib,
            "who_pasted": who_pasted,
            "type": "deposit",
            "owner": "Wahyu",
            "amount": fee,
            "proof_text": "",
            "oscar_approved": "TRUE",
            "note": f"Automatic reinvestment of withdrawal fee from {owner}: Rp{fee:,}",
        },
    ]
    return entries


def format_withdrawal_alert(calc: dict[str, Any]) -> str:
    """Format human-facing Indonesian markdown alert for chat."""
    owner = calc["owner"]
    net_payout = f"Rp{calc['net_payout_rp']:,}".replace(",", ".")
    principal = f"Rp{calc['principal_withdrawn_rp']:,}".replace(",", ".")
    profit_net = f"Rp{calc['profit_withdrawn_net_rp']:,}".replace(",", ".")
    fee = f"Rp{calc['fee_withdrawn_rp']:,}".replace(",", ".")
    remaining = f"Rp{calc['remaining_equity_rp']:,}".replace(",", ".")
    buyer = calc.get("idle_cash_provider", "Faiz")

    lines = [
        f"💸 *Withdrawal Request: {owner}*",
        f"• Kas Ditarik: {net_payout}",
        f"• Komposisi: Modal {principal} + Profit Bersih {profit_net}",
        f"• Fee Wahyu (5%): {fee} (Reinvested)",
        f"• Sisa Saldo {owner}: {remaining}",
        f"• Buyout Kas: {buyer} (-{net_payout} kas, +porsi saham)",
        "",
        f"@Wahyu tolong transfer {net_payout} ke {owner}.",
    ]
    return "\n".join(lines)


def parse_withdraw_command(text: str) -> int | None:
    """Parse withdrawal amount from slash command or natural Indonesian chat."""
    clean = text.strip().lower()

    # Match /withdraw <arg>, withdraw <arg>, or tarik [optional words] <arg>
    pattern = r"(?:/withdraw|withdraw|tarik)(?:\s+(?:saldo|dana|uang|kas|modal))?\s+([0-9.,]+(?:\s*(?:jt|juta|rb|ribu|k|m))?)"
    match = re.search(pattern, clean)
    if not match:
        return None

    raw_val = match.group(1).replace(" ", "")

    multiplier = 1
    if "jt" in raw_val or "juta" in raw_val:
        multiplier = 1_000_000
        raw_val = raw_val.replace("juta", "").replace("jt", "")
    elif "rb" in raw_val or "ribu" in raw_val or "k" in raw_val:
        multiplier = 1_000
        raw_val = raw_val.replace("ribu", "").replace("rb", "").replace("k", "")
    elif "m" in raw_val:
        multiplier = 1_000_000
        raw_val = raw_val.replace("m", "")

    raw_val = raw_val.replace(",", ".")
    # Handle multiple dots like 1.000.000
    if raw_val.count(".") > 1:
        raw_val = raw_val.replace(".", "")
    elif raw_val.count(".") == 1 and multiplier == 1:
        # Check if it's thousands separator like 1.000 or decimal
        parts = raw_val.split(".")
        if len(parts[1]) == 3:
            raw_val = raw_val.replace(".", "")

    try:
        val = float(raw_val)
        return int(round(val * multiplier))
    except ValueError:
        return None
