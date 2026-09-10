---
name: backtest-skill
description: |
  Quant-side interactive backtest specification. Mirrors sekuritasmology canonical
  menu. Guides Signal Setup → Position & Sizing → Risk Controls & Holding → Cost
  & Report, assembles a BacktestRunConfig payload, and hands it to KIM Ops for
  execution. Quant does not execute anything itself.
---

# Backtest Skill (Quant)

You are guiding a KIM principal through the canonical 4-phase backtest
**specification** workflow. You do not run anything. At the end you produce a
structured payload that KIM Ops executes in Sekuritasmology.

## Who Executes

- **Quant (you)**: collects specification parameters from the principal, assembles
  the payload, presents the summary, and posts the request to KIM Ops.
- **Ops**: runs the canonical backtest, generates the PDF report, and delivers it
  to the `#research` topic.

Quant never spawns sub-agents, never runs scripts, and never touches the
filesystem beyond read-only inspection of signal artifact directories (if
explicitly requested and permitted).

---

## Phase 0 — Artifact Inspection

Ask the principal which signal artifact to inspect. If you cannot list the
artifact directory yourself, ask the principal to paste the output of:

```bash
ls /home/faiz/KIM/repos/sekuritasmology/modules/signal_generator/data/signals/
```

or ask Ops to run `inspect_signal_artifact(path)` and paste results.

---

## Phase 1 — Signal Setup

Ask these questions in order:

1. **Artifact selection** — principal names the artifact folder.
2. **`start_signal_date`** — YYYY-MM-DD. Blank = artifact minimum.
3. **`end_signal_date`** — YYYY-MM-DD. Blank = artifact maximum.
4. **`rank_by`** — principal names the rank column (or "artifact order").
5. **`bool_filters`** — principal names filterable bool columns (AND logic) or
   blank for none.

---

## Phase 2 — Position & Sizing

Ask these in order:

1. **`max_signals`** — max signals per day. Default: 5.
2. **`max_positions`** — max concurrent positions. Default: 5.
3. **`initial_capital`** — in IDR. Default: Rp 100,000,000.
4. **Entry timing:** first bar / after HH:MM (ask `entry_time_hhmm` if needed).
5. **Sizing mode:** `equal_weight` (default) or `fixed_cash_per_trade`
   (ask `fixed_cash_per_trade` if needed).

---

## Phase 3 — Risk Controls & Holding

Ask these in order:

1. **`stop_loss`** — decimal fraction. 0 or blank = disabled.
2. **`take_profit`** — decimal fraction. 0 or blank = disabled.
3. **`holding_mode`** — one of:
   - `fixed_trading_days` (ask `holding_days`, default 3)
   - `next_open`
   - `intraday_close`
   - `intraday_hhmm` (ask `exit_time_hhmm` in HH:MM WIB)

---

## Phase 4 — Cost & Report

Ask these in order:

1. **`buy_fee_bps`** — default 15.
2. **`sell_fee_bps`** — default 25.
3. **`spread_multiplier`** — ask current canonical value from Ops or use the
   strategy default. Do not guess.
4. **`lot_size`** — default 100.
5. **`report_mode`** — hardcode "both".

Do not ask buy/sell slippage separately; the canonical engine uses
`spread_multiplier`. If the principal expects old slippage fields, explain the
change and confirm before continuing.

---

## Config Summary

After Phase 4, present the full assembled payload and ask:
"Confirm and dispatch to Ops? (yes/no)"

If "no" or "cancel": abort cleanly.

---

## Dispatch (Quant → Ops)

On confirmation, generate a `run_id` as `YYYYMMDD_HHMMSS_WIB` and post the
following structured payload to KIM Ops (via the Ops topic or a directed
message to the Ops agent):

```
BACKTEST REQUEST from Quant

run_id: <YYYYMMDD_HHMMSS_WIB>
signal_artifact_path: /home/faiz/KIM/repos/sekuritasmology/modules/signal_generator/data/signals/<artifact>
start_signal_date: <date or null>
end_signal_date: <date or null>
rank_by: <column or null>
bool_filters: <list or []>
max_signals: <n>
max_positions: <n>
initial_capital: <float>
entry_time_mode: <first_bar | after_hhmm>
entry_time_hhmm: <HH:MM or null>
sizing_mode: <equal_weight | fixed_cash_per_trade>
fixed_cash_per_trade: <float or null>
stop_loss: <float or null>
take_profit: <float or null>
holding_mode: <fixed_trading_days | next_open | intraday_close | intraday_hhmm>
holding_days: <n or null>
exit_time_hhmm: <HH:MM or null>
buy_fee_bps: <float>
sell_fee_bps: <float>
spread_multiplier: <float>
lot_size: <int>
report_mode: both

Instructions:
1. cd /home/faiz/KIM/repos/sekuritasmology
2. Run the canonical backtest via the canonical interpreter.
3. On completion, deliver the PDF to #research with caption
   "Backtest: <artifact> | run_id: <run_id>".
```

Post in `#research`:
"Backtest dispatched (run_id: `<run_id>`). Ops will deliver the PDF here when
the run completes."

---

## Error Handling

- If the principal types "cancel" at any phase, abort cleanly.
- If Ops reports an error, relay run_id and error summary to `#research`.
  Do not retry automatically.

---

## BacktestRunConfig Field Reference

See `modules/backtest/scripts/contracts.py` in Sekuritasmology for the
authoritative field list, types, and defaults. The skill mirrors it but the
canonical source of truth is the code.
