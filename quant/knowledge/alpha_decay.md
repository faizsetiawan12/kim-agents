---
topic: alpha_decay
source: TEQI
last_updated: 2026-05-28
related: [signals_and_strategies, performance_metrics, backtesting_concepts, market_microstructure]
---

# Alpha Decay

TL;DR: Signals lose predictive power over time. The speed of that decay sets the maximum sensible holding period — holding too long turns your edge into noise.

## What Is Alpha Decay?

A signal predicts future excess returns at the moment it fires. But the information edge embedded in the signal erodes as other market participants act on similar information, prices adjust, and the original catalyst fades. This erosion is alpha decay. TEQI formalizes it through the concept of information coefficients (IC) — the correlation between a signal's predicted return rank and its realized return rank — measured at increasing horizons.

If your signal has strong IC at day 1 but near-zero IC by day 5, the alpha half-life is roughly 2–3 days. Holding positions for 10 days after a day-3 decay is deadweight: you bear position risk with no expected return benefit.

## Key Concepts

**IC decay curve**: Plot IC vs. horizon. The rate of decay tells you when to exit. Flat IC means the signal is broadly persistent; steep IC means the signal is short-lived.

**Half-life**: The horizon at which IC drops to half its initial value. A signal with a 3-day half-life is best matched with a 2–5 day holding mode in Sekuritasmology's backtest engine (`holding_days = 3` is the default for a reason).

**Interaction with liquidity**: In illiquid markets, decaying alpha is compounded by market impact — you can't always exit when IC hits zero. IDX mid- and small-caps have wide spreads and thin order books; exiting a 20-lot position at the wrong time costs more than theoretical slippage.

**Over-fitting danger**: A signal that looks like it has strong IC at day 3 in a backtest may be over-fit. TEQI's Chapter 8 on evaluating excess returns warns that reusing historical data for both signal construction and IC measurement inflates estimates.

## IDX-Specific Example

Sekuritasmology's `broksum_analysis_base` signal fires based on broker summary patterns. These patterns are typically short-lived on IDX — institutional order flow is detectable for 1–3 sessions before the market fully adjusts. Using `holding_days = 3` (the default) is consistent with this decay profile. Using `holding_days = 10` would extend well past the signal's useful horizon and is likely to reduce Sharpe.

## In the Backtest Skill

Phase 3 asks for `holding_mode` and `holding_days`. If you are unsure, ask: "How long does this signal type typically retain predictive power?" The answer guides the holding mode choice. Fixed Trading Days with 2–5 days is appropriate for most IDX short-term signals.

## Cross-Links

- See `signals_and_strategies.md` for `rank_by` mechanics and signal-to-noise ratio.
- See `market_microstructure.md` for how IDX liquidity amplifies decay cost.
- See `backtesting_concepts.md` for how to detect over-estimated IC in historical tests.
- See `performance_metrics.md` for how win rate and Sharpe interact with holding period.
