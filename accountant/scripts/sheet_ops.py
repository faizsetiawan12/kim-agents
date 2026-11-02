"""Append rows and read values from Google Sheets using stdlib only."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from scripts.google_sheets import get_access_token


def append_journal_rows(
    sheet_id: str,
    rows: list[dict[str, Any]],
    token: str | None = None,
    verify: bool = True,
) -> dict[str, Any]:
    """Append validated journal rows to the Journal tab and verify by re-reading.

    Row schema: [date_wib, who_pasted, type, owner, amount_rp, proof_text, oscar_approved, note]
    Amount is stored as signed numeric integer (no currency symbols) for formula calculation.
    """
    auth_token = token or get_access_token()

    values = []
    for r in rows:
        amount_val = r["amount"]
        sign = -1 if r["type"] in ("withdraw", "realized-loss", "fee-5pct") else 1
        numeric_amount = sign * abs(amount_val)

        row_data = [
            r.get("date_wib", ""),
            r.get("who_pasted", ""),
            r.get("type", ""),
            r.get("owner", ""),
            numeric_amount,
            r.get("proof_text", ""),
            str(r.get("oscar_approved", "FALSE")),
            r.get("note", ""),
        ]
        values.append(row_data)

    body = {
        "range": "Journal!A:H",
        "majorDimension": "ROWS",
        "values": values,
    }

    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/"
        f"Journal!A:H:append?valueInputOption=USER_ENTERED"
    )
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        append_res = json.loads(resp.read().decode("utf-8"))

    if verify:
        updated_range = append_res.get("updates", {}).get("updatedRange")
        if not updated_range:
            raise RuntimeError("Google Sheets append response missing updatedRange for verification.")

        read_url = (
            f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/"
            f"{urllib.parse.quote(updated_range)}"
        )
        read_req = urllib.request.Request(
            read_url,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        with urllib.request.urlopen(read_req, timeout=30) as read_resp:
            read_res = json.loads(read_resp.read().decode("utf-8"))
            read_values = read_res.get("values", [])
            if len(read_values) != len(rows):
                raise RuntimeError(
                    f"Verification mismatch: expected {len(rows)} rows appended, got {len(read_values)}."
                )

    return append_res
