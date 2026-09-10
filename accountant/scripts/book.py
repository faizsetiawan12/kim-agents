"""RDN book rules: fee, validation, ledger. Pure functions, no I/O."""

from __future__ import annotations

ALLOWED_TYPES = (
    "deposit",
    "realized-profit",
    "realized-loss",
    "fee-5pct",
    "withdraw",
    "reversing-entry",
)

ALLOWED_OWNERS = ("Faiz", "Jimmy", "Oscar", "Wahyu-fee")


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
