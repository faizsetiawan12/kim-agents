---
topic: portfolio_construction
source: APM
last_updated: 2026-05-28
related: [factor_exposure, kelly_criterion, risk_management, performance_metrics, signals_and_strategies]
---

# Portfolio Construction

TL;DR: Portfolio construction answers the question: given a set of signals, how do you combine them into a portfolio of positions that maximizes expected return for your risk budget? Equal-weight is the robust default; optimization adds value only when inputs are reliable.

## Mean-Variance Basics

APM Chapter 6 grounds portfolio construction in mean-variance analysis. The ideal portfolio maximizes:

```
E[return] - (lambda / 2) * variance
```

Where `lambda` is a risk aversion parameter. The optimal weights are proportional to:

```
w* ∝ Omega^(-1) * alpha
```

Where `Omega` is the covariance matrix and `alpha` is the expected return vector.

In practice, this requires estimating expected returns (hard, noisy) and a covariance matrix (also noisy at small portfolio sizes). APM Chapter 6 advocates for simpler heuristics: risk-based sizing and position constraints, not unconstrained optimization.

## Equal Weight

**What it is**: Divide capital evenly across all `max_positions` slots.

**When it works**: When signal quality is roughly uniform across picks, or when you don't trust relative signal strengths enough to size differently.

**IDX context**: For short-term IDX signals (1–5 day holding), the trading friction of computing precise optimal weights outweighs any precision gain. Equal weight is the right default for most Sekuritasmology backtests. It also avoids concentration: with 5 equal-weight positions in a Rp 100M portfolio, each position is Rp 20M, which is feasible even for mid-cap IDX names at 100-share lot size.

## Fixed Cash Per Trade

**What it is**: Each new position gets exactly `fixed_cash_per_trade` IDR, regardless of available capital.

**When it works**: When you want consistent position sizing across time and don't want large positions just because capital has grown (or small positions because it has shrunk). It avoids the compounding effect of equal-weight re-sizing on every new entry.

**IDX context**: Useful for live trading where execution complexity grows with varying position sizes. For backtests, it produces more realistic results if your live strategy would use fixed notional.

## max_positions Constraint

APM Chapters 7 and 8 discuss diversification: `max_positions` is not just a risk control, it determines how many independent alpha bets you are running. With 5 positions and IDX market moves, your portfolio has significant concentration. APM's analysis suggests that 10–20 positions are needed to diversify away most idiosyncratic risk, but IDX liquidity constraints often force smaller books.

The `max_signals` parameter filters how many signals fire per day. Setting `max_signals = max_positions = 5` means you never enter more than 5 signals per day and never hold more than 5 concurrent positions — a conservative but realistic setup for retail-scale IDX trading.

## IDX-Specific Example

A backtest with `initial_capital = 100,000,000` IDR, `max_positions = 5`, equal weight, and `lot_size = 100` allocates Rp 20M per position. At an IDX stock price of Rp 2,000 per share, one lot = Rp 200,000. Rp 20M buys 100 lots, a moderate size for most LQ45 names. For small-cap names priced at Rp 500/share, one lot = Rp 50,000, so Rp 20M would buy 400 lots — potentially moving the price if daily volume is thin.

## Cross-Links

- See `factor_exposure.md` for how portfolio weights translate into factor bets.
- See `kelly_criterion.md` for the theoretical basis of capital allocation fractions.
- See `risk_management.md` for how position sizing interacts with stop-loss and drawdown.
- See `signals_and_strategies.md` for how `max_signals` and `bool_filters` shape the signal pool.
