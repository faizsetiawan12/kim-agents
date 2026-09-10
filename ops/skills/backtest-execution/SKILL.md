---
name: backtest-execution
description: |
  Ops-side backtest execution. Receives a structured BACKTEST REQUEST from Quant,
  runs the canonical Sekuritasmology backtest, and delivers the PDF report to
  the #research Telegram topic.
---

# Backtest Execution Skill (Ops)

You execute backtest runs requested by KIM Quant in Sekuritasmology.

## Input

You receive a `BACKTEST REQUEST from Quant` payload with:
`run_id`, `signal_artifact_path`, and a full BacktestRunConfig field set
(see `modules/backtest/scripts/contracts.py` for authoritative fields).

## Execution

```bash
cd /home/faiz/KIM/repos/sekuritasmology
/home/faiz/miniconda3/envs/sekuritasmology/bin/python -m modules.backtest.scripts.run_backtest \
  <signal_artifact_path> <config_json_tmp_path>
```

- Write the config JSON to a temp file before invoking.
- Never modify strategy code or data artifacts as part of a run.
- If the request references stale fields (buy/sell slippage instead of
  `spread_multiplier`), ask Quant to re-send a corrected payload instead of
  guessing.

## Delivery

On success, deliver the PDF:

```bash
/home/faiz/miniconda3/envs/sekuritasmology/bin/python \
  /home/faiz/KIM/agents/quant/scripts/send_pdf_to_research.py \
  --pdf-path <report_path> \
  --caption "Backtest: <artifact> | run_id: <run_id>"
```

On failure, post the run_id and error summary to `#research` and `#ops`.
Never retry more than once without asking.

## Verification

- Confirm the PDF file exists and is non-empty.
- Confirm the Telegram delivery succeeded (script exit code 0).
