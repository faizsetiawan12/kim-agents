---
name: sheets-leads
description: |
  Read-only Google Sheets for the KATMA leads tracker (Firms + Tracker tabs).
  Permitted: read rows and stage counts from the leads sheet only.
  Never write, edit, delete, or touch the RDN money book.
metadata: {"clawdbot":{"emoji":"📊"}}
---

# Sheets-Leads Skill (PM Read-Only Scope)

PM uses this skill to read the KATMA leads tracker. Read-only. No writes ever.

## Permitted Operations

- **Read** rows from the leads sheet tabs `Firms` and `Tracker` via
  `pm/scripts/leads_sheets.py` (uses `KIM_GOOGLE_SHEETS_KEY_FILE`, same
  service account as accountant).
- **Count** funnel stages with `funnel_counts()` for 08:00/18:00 reports.
- Leads sheet ID comes from env `KIM_LEADS_SHEET_ID` only.

## Forbidden Operations

- Any write, append, edit, or delete on any sheet.
- Any read or write on the RDN money book (`1xSPJfRAfR0xj5FNeLGd_-kDXJoPunZa8Gu5bnMF6W-U`).
  The script asserts and refuses this ID.
- Printing, copying, or storing the key file path contents, Sheet IDs in chat
  beyond the link, or credentials in docs, git, or chat.
- Operations on any other sheet or account.

## Tabs and Columns

- Tabs: `Firms` (static DB), `Tracker` (live funnel).
- Firms columns: Firm | Email | Tel | Web | Address | AUM Jul 2026 (Rp) |
  AUM Agu 2026 (Rp).
- Tracker columns: Firm | AUM Jul 2026 (Rp) | AUM Agu 2026 (Rp) | Contact |
  Job Title | Email | Source | Stage | Last Touch | Next Follow-Up | PIC.
- Stage values (locked): Backlog, Contacted, Demo Scheduled, Demo Done,
  Trial, Paying, Dropped. No free text.

## Report Lines

- `Leads: {contacted}/{total} contacted · {demos} demos · {paying} paying`
- Stale (no PIC update 7+ days): append `· stale {n} rows, PIC {names} update?`

## API Basics

Key file reaches the script via env `KIM_GOOGLE_SHEETS_KEY_FILE` only
(never hardcoded, never committed — ADR-0001). Read, then report. If the
read fails, disclose failure; never claim success.
