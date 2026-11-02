# Leads (parked)

Not wired to any agent. `leads_sheets.py` and `sheets-leads/` were moved out of
the PM agent on 2026-11-02 because the feature never ran: `KIM_LEADS_SHEET_ID`
is unset on every host, and no cron job, agent, or skill consumed it.

Kept only so the read-only Sheets reader is not lost. To revive it:

1. Set `KIM_LEADS_SHEET_ID` (and the service account key path in
   `KIM_GOOGLE_SHEETS_KEY_FILE`).
2. Add the skill back to the `skills` array of the agent that should own it.
3. Fix the hardcoded import in `leads_sheets.py` — it loads
   `scripts.google_sheets` from the accountant workspace
   (`~/.hermes/profiles/kim-accountant/workspace`), which is a Hermes path.

Until all three are done, treat this folder as reference code, not a feature.
