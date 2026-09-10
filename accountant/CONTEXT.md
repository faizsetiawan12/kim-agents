# RDN Bookkeeping

Bookkeeping language for Wahyu's Stockbit RDN profit-share. Agent is scribe; Oscar reconciles.

## Language

**Deposit**:
Cash placed into the RDN for a named owner.
_Avoid_: top-up, transfer in

**Realized-Profit**:
Cash gain locked by a sell, attributable to a named owner.
_Avoid_: unrealized gain, paper profit, return

**Realized-Loss**:
Cash loss locked by a sell, attributable to a named owner. Stored negative in the Journal, appears as negative in ProfitShare, and carries no fee.
_Avoid_: paper loss, drawdown, deficit

**Fee-5pct**:
Five percent of a realized-profit row, owed to Wahyu. Never charged on losses or withdrawals.
_Avoid_: commission, cut, admin fee

**Withdraw**:
Cash taken out of the RDN by a named owner. Reduces balance with no fee.
_Avoid_: cash out, redemption

**Reversing-Entry**:
A new row that cancels a prior wrong row. Old rows are never edited or deleted.
_Avoid_: edit, delete, correction overwrite

**Derived Tab**:
A sheet tab (Ledger, ProfitShare) computed exclusively via Google Sheets formulas over Journal rows, ensuring continuous sync with zero agent-side writes. Ledger ends with Total Assets across owner balances.
_Avoid_: static ledger, snapshot tab

**Approved-Flag**:
Oscar's recorded yes on a reversing-entry before it is written.
_Avoid_: verified, checked, ok
