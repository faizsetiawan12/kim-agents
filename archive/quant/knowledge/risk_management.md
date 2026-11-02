---
topic: risk_management
source: APM
last_updated: 2026-05-28
related: [portfolio_construction, kelly_criterion, performance_metrics, backtesting_concepts, alpha_decay]
---

# Risk Management

TL;DR: Stop-loss and take-profit are execution rules, not predictions. Their value is behavioral and portfolio-level, not in predicting when a trade turns bad. Understand the cost-benefit tradeoff before enabling them.

## Stop-Loss Mechanics

APM Chapter 9 covers stop-loss in detail. A stop-loss exits a position when the price falls a specified fraction below the entry price. In Sekuritasmology's backtest engine:

```
stop_loss = 0.05  # exit if price falls 5% from entry
```

When the price hits the stop, the position is closed at that session's available price (open or intraday depending on holding mode).

**Why use it?**: APM Section 9.2 argues the main benefit is behavioral, not predictive. Stop-losses prevent a small loss from becoming catastrophic if a signal turns out to be wrong. They also cap the maximum loss per trade, which improves the drawdown profile.

**The cost**: APM Section 9.3 is explicit — stop-losses reduce expected return when the underlying strategy has positive alpha. A stop at 5% means you exit some winning trades early after a temporary drawdown. The benefit is reduced left-tail risk; the cost is giving up some upside from recovery.

## Take-Profit Mechanics

Take-profit exits a position when the price rises a specified fraction above entry:

```
take_profit = 0.10  # exit if price rises 10% from entry
```

**Why use it?**: Locks in gains on strong-moving positions. Prevents giving back profits if the signal has already fired and the price reverses.

**The cost**: If the signal has remaining alpha (the stock continues rising), you've capped your gain prematurely. Take-profit is more useful when signal half-life is short and you don't want to hold through the reversion phase.

## Interaction with Holding Mode

Risk controls and holding mode interact in Sekuritasmology. The engine checks stop/take on each available bar. If `holding_mode = fixed_trading_days` with `holding_days = 3`, the position exits either:
1. On day 3 (the scheduled exit), or
2. Earlier, if stop-loss or take-profit triggers first.

Whichever comes first wins. This means stop-loss during a 3-day hold is a tighter exit policy than stop-loss alone.

For `intraday_close` or `intraday_hhmm` modes, stop and take are checked within the entry session only. This makes risk controls less useful for intraday strategies since the window is too narrow.

## Drawdown

Maximum drawdown measures the peak-to-trough decline of the portfolio equity curve. APM Chapter 9 connects drawdown to stop-loss policy: tighter stops reduce max drawdown but also reduce return in trending markets.

In Sekuritasmology backtest reports, drawdown appears alongside Sharpe and win rate. A strategy with Sharpe = 1.0 but max drawdown = 40% is hard to trade in practice — most investors would abandon it before recovery.

## IDX-Specific Example

On IDX, auto-rejection limits exist at ±25% per session (for most stocks). A stop at 20% or more rarely fires as a clean stop — the stock may gap past your stop level at open, delivering more loss than the stop intended. For IDX, stop levels of 3–8% are more realistic. A 10% stop on a small-cap IDX name with a 3-day hold period is effectively no stop at all for most benign trades, but provides protection against news-driven gaps.

## Cross-Links

- See `portfolio_construction.md` for how position sizing interacts with stop level (a 5% stop on a 20% position is a 1% portfolio loss).
- See `performance_metrics.md` for Calmar ratio — return / max drawdown — which directly captures the risk management tradeoff.
- See `alpha_decay.md` for why stop-loss and holding period should be designed together.
- See `backtesting_concepts.md` for how stop-loss results in backtests can be optimistic vs. live.
- See `indonesia_equity_context.md` for auto-rejection limits and gap risk on IDX.
