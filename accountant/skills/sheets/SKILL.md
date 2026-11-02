---
name: sheets
description: |
  Google Sheets for the single RDN book. Only permitted: create the book
  once, append validated rows, read rows for totals and link delivery.
  Never edit or delete rows, never move money, never print the key.
metadata: {"clawdbot":{"emoji":"📒"}}
---

# Sheets Skill (Accountant Scope)

Accountant uses this skill for the single live RDN book only.

## Permitted Operations

- **Append** validated rows to `Journal` only (signed amount: deposit/profit positive, withdraw/fee-5pct negative; reversing entries only after Oscar "approve"; withdrawal multi-entry sets: withdraw, realized-profit, fee-5pct, deposit-reinvest).
- **Read** rows or computed balances from `Journal`, `Ledger`, and `ProfitShare` for daily totals and link delivery.
- Never write directly to `Ledger` or `ProfitShare` (auto-derived via live spreadsheet formulas).

## Forbidden Operations

- Editing or deleting existing rows in `Journal`.
- Writing values into `Ledger` or `ProfitShare` directly (breaking dynamic formulas).
- Any money movement, trade, transfer, or reconciliation.
- Operations on any other sheet or account.
- Printing, copying, or storing the API key outside the server file.

## Tabs and Columns

- Tabs: `Journal`, `Ledger`, `ProfitShare`.
- Columns: date-WIB, who-pasted, type, owner, amount-Rp, proof-text (optional, blank if absent), oscar-approved, note.
- Sheet ID: resolved via `$KIM_RDN_SHEET_ID` at runtime.
- Sheet URL: derived from `$KIM_RDN_SHEET_ID` (`https://docs.google.com/spreadsheets/d/$KIM_RDN_SHEET_ID/edit`).

## Natural Chat Policy

- The agent extracts bookkeeping data from unstructured user messages.
- `proof-text` is never required; leave column blank when omitted.
- Missing date or timestamp defaults to message send time in WIB (UTC+7).
- If intent, owner, or amount is ambiguous, stop and ask the user before writing.

## API Basics

Credentials arrive via `KIM_*` environment variable only (never in chat, docs, or git). Append, then re-read the row to verify before confirming. If verification fails, disclose failure; never claim success.
