"""Strict 4-command router for KIM Accountant. Slash commands only, no I/O."""

from __future__ import annotations

import re
from typing import Any

COMMANDS = ("/withdraw", "/deposit", "/sheet", "/balance")


def parse_command(text: str) -> dict[str, Any] | None:
    """Parse one of the 4 strict slash commands. Returns None when not matched."""
    clean = text.strip()
    lower = clean.lower()
    if not lower.startswith("/"):
        return None

    m = re.match(r"/(withdraw|deposit)\s+(.+?)\s*$", lower)
    if m:
        return {"command": f"/{m.group(1)}", "arg": m.group(2).strip()}

    if re.match(r"/sheet\s*$", lower):
        return {"command": "/sheet", "arg": ""}
    if re.match(r"/balance\s*$", lower):
        return {"command": "/balance", "arg": ""}
    return None


def parse_nominal(raw: str) -> int | None:
    """Parse Indonesian nominal: 1000000, 1.000.000, 1jt, 1juta, 500rb, 500k, 2.5jt."""
    raw_val = raw.strip().lower().replace(" ", "")

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
    if raw_val.count(".") > 1:
        raw_val = raw_val.replace(".", "")
    elif raw_val.count(".") == 1 and multiplier == 1:
        parts = raw_val.split(".")
        if len(parts[1]) == 3:
            raw_val = raw_val.replace(".", "")

    try:
        return int(round(float(raw_val) * multiplier))
    except ValueError:
        return None
