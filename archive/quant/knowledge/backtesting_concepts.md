---
topic: backtesting_concepts
source: both
last_updated: 2026-05-28
related: [signals_and_strategies, performance_metrics, alpha_decay, risk_management, factor_exposure]
---

# Backtesting Concepts

TL;DR: A backtest tells you what would have happened if you had followed a strategy perfectly in the past with perfect information. It does not predict the future. The main dangers are lookahead bias, survivorship bias, and overfitting to historical data.

## Lookahead Bias

Using information in a backtest that would not have been available at the signal generation time. Examples:
- Using same-day closing prices to generate entry signals that execute at the same close.
- Including fundamental data revisions not available in real time.
- Using future constituents of an index to select stocks.

Sekuritasmology's `signal_generator` pipeline uses only data available by signal generation time. The `start_signal_date` and `end_signal_date` parameters in Phase 1 restrict the backtest window to dates where signal data is complete.

## Survivorship Bias

Only including stocks that still exist (survived) at backtest time, ignoring stocks that were delisted, went bankrupt, or were acquired. This inflates backtest returns because bad outcomes (bankruptcies) are excluded.

TEQI Chapter 8 discusses this in the context of evaluating excess returns. On IDX, survivorship bias is real: several IDX-listed stocks have been delisted or suspended over the past decade. The `bool_filters` in Phase 1 can partially mitigate this if the signal artifact includes a quality filter.

## Overfitting

A strategy that was optimized to perform well on historical data but does not generalize to future data. Signs of overfitting:
- Sharpe ratio drops sharply in out-of-sample tests.
- Many parameters were tuned to historical data (buy fee, sell fee, stop level, holding days all optimized simultaneously).
- The strategy selects very specific parameter combinations that happen to work on one dataset.

TEQI Chapter 8 introduces the concept of the Rademacher anti-serum (RAS) as a framework for testing whether alpha is genuine or an artifact of in-sample optimization. The key principle: test on data you have never seen before.

## Rademacher Anti-Serum (RAS)

APM and TEQI both address strategies for detecting overfitting. The Rademacher complexity provides a mathematical bound on how much a model can overfit a dataset. In Sekuritasmology, the `rademacher_anti_serum` module implements a permutation test: if a strategy's performance on randomly shuffled signals is close to its performance on real signals, the strategy is over-fit.

When Quant Bot dispatches a backtest to Engineer, the PDF report includes RAS test results. A positive RAS test (strategy significantly beats shuffled baseline) is evidence of genuine alpha.

## Report Metrics

Sekuritasmology's PDF report includes:
- **Total return**: Cumulative return over the backtest window.
- **Annualized return**: Normalized to one year.
- **Sharpe Ratio**: Risk-adjusted return (see `performance_metrics.md`).
- **Sortino Ratio**: Sharpe using only downside volatility.
- **Max drawdown**: Worst peak-to-trough decline.
- **Win rate**: Fraction of trades that closed positive.
- **Trade count**: Total executed trades.

Each metric has in-sample and (if applicable) out-of-sample versions. Always check both.

## IDX-Specific Example

A backtest on IDX data from 2020–2021 (post-COVID recovery) will show inflated returns for almost any long-only strategy because the entire market rallied. The same strategy tested on 2022–2023 (rate-hike period) will often show much weaker results. When requesting a backtest, specify the `start_signal_date` and `end_signal_date` to include at least one stress period. Avoid cherry-picking a window that includes only the strongest market phase.

## Cross-Links

- See `signals_and_strategies.md` for how `bool_filters` and `rank_by` affect signal quality.
- See `performance_metrics.md` for interpreting Sharpe, Sortino, and drawdown in the report.
- See `alpha_decay.md` for how holding period choice interacts with in-sample vs. out-of-sample performance.
- See `risk_management.md` for how stop-loss parameters should not be optimized in-sample.
