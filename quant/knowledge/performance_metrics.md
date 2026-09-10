---
topic: performance_metrics
source: APM
last_updated: 2026-05-28
related: [backtesting_concepts, risk_management, kelly_criterion, portfolio_construction, factor_exposure]
---

# Performance Metrics

TL;DR: Sharpe is the workhorse metric — risk-adjusted return. Sortino is better for downside-focused evaluation. Calmar captures drawdown relative to return. Max drawdown is non-negotiable to report; win rate alone is misleading without knowing the win/loss ratio.

## Sharpe Ratio

```
Sharpe = (mean_return - risk_free_rate) / std_deviation_of_return
```

Annualized on 252-day convention (IDX trading days per year):
```
Annualized Sharpe = (daily_mean * 252) / (daily_std * sqrt(252))
                  = (daily_mean / daily_std) * sqrt(252)
```

**Interpretation**: Sharpe = 1.0 means you earn one unit of return for each unit of risk. Above 1.0 is good; above 2.0 is excellent and should be scrutinized for overfitting. APM Chapter 6 discusses Sharpe extensively and notes that most real-world strategies achieve 0.3–0.8 in live trading.

**Limitation**: Sharpe penalizes upside volatility equally with downside. A strategy that occasionally makes large gains looks worse on Sharpe than a strategy that makes steady small gains.

## Sortino Ratio

```
Sortino = (mean_return - risk_free_rate) / downside_deviation
```

Downside deviation uses only returns below a threshold (typically zero). This punishes losses but not gains. More appropriate for asymmetric return distributions common in short-term equity strategies.

APM Chapter 8 discusses performance attribution in a context where Sortino is a cleaner measure for strategies with right-skewed return profiles.

## Calmar Ratio

```
Calmar = Annualized_Return / Max_Drawdown
```

Higher Calmar means better return per unit of worst historical loss. A strategy with 30% annualized return and 60% max drawdown has Calmar = 0.5. A strategy with 20% return and 10% max drawdown has Calmar = 2.0 — much more practical to trade.

Calmar is the most relevant metric for practitioners who worry about surviving a drawdown. APM Chapter 9 on stop-loss directly targets improving Calmar by capping the max drawdown.

## Max Drawdown

```
Max_Drawdown = (peak_equity - trough_equity) / peak_equity
```

The worst observed peak-to-trough decline in the equity curve. Always stated as a positive fraction.

**Why it matters**: Even a strategy with excellent Sharpe is untradeble if max drawdown is 50%. Most investors stop trading or reduce size before recovery, realizing losses. APM Chapter 9 shows that stop-loss policy and position concentration are the primary levers.

## Win Rate

```
Win_Rate = (number of profitable trades) / (total trades)
```

**Warning**: Win rate alone is misleading. A 60% win rate with average win of +1% and average loss of -5% is a losing strategy. Always pair win rate with average win/loss ratio. Sekuritasmology reports include both.

For IDX short-term strategies, win rates of 50–60% with win/loss ratios of 1.2–1.5x are typical for genuine alpha. Higher win rates (>70%) in backtests are usually a sign of overfitting.

## 252-Day Annualization Convention

IDX has approximately 240–252 trading days per year. Sekuritasmology uses 252 as the annualization constant (standard for most equity markets). To annualize daily metrics:
```
Annualized return    = daily_return * 252
Annualized std       = daily_std * sqrt(252)
Annualized Sharpe    = daily_Sharpe * sqrt(252)
```

## IDX-Specific Example

A Sekuritasmology backtest over 2022–2024 on `broksum_analysis_base` might produce:
- Annualized return: 28%
- Annualized volatility: 22%
- Sharpe Ratio: 1.27
- Max drawdown: 18%
- Win rate: 55%
- Calmar: 1.56

This would be a strong result. Before acting on it: check out-of-sample periods, look at the RAS test result, and ensure the backtest window includes both trending and ranging market phases.

## Cross-Links

- See `backtesting_concepts.md` for how these metrics can be misleading in overfitted backtests.
- See `risk_management.md` for how stop-loss improves Calmar at the cost of Sharpe.
- See `kelly_criterion.md` for how Sharpe Ratio directly determines the optimal Kelly fraction.
- See `factor_exposure.md` for why reported Sharpe may be inflated by factor tilts rather than stock-level alpha.
