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
Cash taken out of the RDN by a named owner. Reduces balance with no fee. For mark-to-market withdrawals from the initial risk pool, calculated proportionally across principal and net profit, funded via idle cash buyout, with Wahyu's 5% profit fee reinvested into Wahyu's balance.
_Avoid_: cash out, redemption

**Risk Pool (Old Pool)**:
The initial pooled capital (Rp14.640.313 across Faiz, Jimmy, Oscar, Wahyu) actively deployed in trading positions. Segregated from subsequent idle cash deposits to prevent profit dilution.

**Idle Cash**:
Fresh cash deposited into RDN that is not yet deployed in trading risk (e.g. Faiz Rp110.000.000). Provides liquidity for buyouts without diluting trading P&L.

**Reversing-Entry**:
A new row that cancels a prior wrong row. Old rows are never edited or deleted.
_Avoid_: edit, delete, correction overwrite

**Derived Tab**:
A sheet tab (Ledger, ProfitShare) computed exclusively via Google Sheets formulas over Journal rows, ensuring continuous sync with zero agent-side writes. Ledger ends with Total Assets across owner balances.
_Avoid_: static ledger, snapshot tab

**Approved-Flag**:
Oscar's recorded yes on a reversing-entry before it is written.
_Avoid_: verified, checked, ok
