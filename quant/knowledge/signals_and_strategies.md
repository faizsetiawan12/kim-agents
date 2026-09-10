---
topic: signals_and_strategies
source: TEQI
last_updated: 2026-05-28
related: [alpha_decay, factor_exposure, portfolio_construction, backtesting_concepts, market_microstructure]
---

# Signals and Strategies

TL;DR: A signal is a ranked prediction of future relative returns. Signal quality is measured by Information Coefficient (IC). The `rank_by` and `bool_filters` parameters in the backtest skill directly control how signals are filtered and ordered.

## What Is a Signal?

TEQI defines an alpha signal as any function of observable data that produces a cross-sectional ranking of expected excess returns. A strong signal is one where high-ranked stocks subsequently outperform low-ranked stocks.

In Sekuritasmology, signals are stored as `.parquet` files (artifacts) under `signal_generator/data/signals/`. Each artifact contains one row per (date, ticker) pair with signal metadata, score columns, and optionally pre-computed analytics.

## Signal-to-Noise Ratio

Not all signals are equally good. Signal-to-noise (SNR) is roughly `IC / IC_volatility`. TEQI Chapter 8 shows that IC is a time series — it varies by market regime, signal type, and horizon. A signal with IC = 0.05 and high IC volatility has worse SNR than a signal with IC = 0.03 and low IC volatility.

For Sekuritasmology signals, the `_kelly_fraction` columns encode a version of SNR: they combine IC level with IC stability into a single sizing recommendation. Ranking by `_kelly_fraction` is implicitly SNR-sorted.

## `rank_by` Mechanics

Phase 1 of the Backtest Skill asks which column to rank by. The engine sorts all signal rows for each day by the selected column (descending by default — higher value = better rank) and takes the top `max_signals` as candidates. Options:

- **Artifact order**: Use the original row order in the parquet file. Only appropriate if the artifact is pre-sorted by a meaningful criterion.
- **Rankable numeric column**: Any float column (e.g., `score`, `z_score`, `_kelly_fraction`). Higher values are taken first.

Choosing the wrong `rank_by` is a common mistake. If a column is not predictive of returns, ranking by it introduces noise. When uncertain, prefer a `_kelly_fraction` column or ask Quant to inspect the artifact metadata.

## `bool_filters` AND Logic

Phase 1 also offers boolean filter columns. Setting `bool_filters = ["is_liquid", "is_trending"]` means only signals where BOTH `is_liquid == True` AND `is_trending == True` are considered. This is strict AND logic — each additional filter reduces the signal universe.

Common IDX-relevant boolean filters in Sekuritasmology artifacts:
- **is_liquid**: True if the stock's average daily trading volume exceeds a threshold.
- **is_trending**: True if price momentum is positive over a lookback window.
- **broker_filter**: True if a specific broker pattern condition is met.

Adding too many bool_filters can shrink the signal pool to near-zero on some days. If `max_signals = 5` but only 2 signals pass all filters, the portfolio underuses capital. Phase 0 inspection shows filterable columns and the Plan B of asking Quant to estimate filter pass rates.

## Artifact Pipeline

Signal artifacts are produced by the Sekuritasmology pipeline:
1. `data_collection` → raw OHLCV and broker data.
2. `data_cleaning` → removes bad data, adjusts for corporate actions.
3. `feature_engine` → computes indicators, broker summary statistics.
4. `signal_scanner` → applies strategy rules, outputs parquet with signal rows and metadata columns.

The parquet files under `signal_generator/data/signals/` are the outputs of step 4. Each subdirectory corresponds to a strategy variant. The directory name is the artifact name shown in Phase 1.

## IDX-Specific Example

The `sekuritasmology_broksum_analysis_base` artifact contains broker flow summary signals. Each row is a (date, ticker) pair where the broker pattern fired. Typical columns include `net_flow_rank` (a rankable numeric column reflecting institutional net buying), `is_accumulation` (a filterable bool), and `broksum_kelly_fraction` (pre-computed Kelly weight). A sensible default for this artifact: `rank_by = broksum_kelly_fraction`, `bool_filters = ["is_accumulation"]`.

## Cross-Links

- See `alpha_decay.md` for how signal IC decay should guide your `holding_days` choice.
- See `portfolio_construction.md` for how `max_signals` and `max_positions` shape the portfolio.
- See `backtesting_concepts.md` for overfitting risk when selecting `rank_by` columns in-sample.
- See `market_microstructure.md` for why liquidity `bool_filters` matter for execution realism.
