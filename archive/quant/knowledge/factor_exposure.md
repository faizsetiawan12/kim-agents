---
topic: factor_exposure
source: APM
last_updated: 2026-05-28
related: [portfolio_construction, risk_management, performance_metrics, backtesting_concepts]
---

# Factor Exposure

TL;DR: Every stock return is partly explained by broad market forces (factors) and partly by stock-specific surprises. Decomposing this is the foundation of modern risk management.

## What Is a Factor?

A factor is a systematic driver of returns shared across many stocks. APM Chapter 4 defines the multi-factor model as:

```
r_i = sum_k (beta_ik * f_k) + epsilon_i
```

Where:
- `r_i` = return of stock i
- `beta_ik` = factor loading (exposure) of stock i to factor k
- `f_k` = factor return (the market-wide move of that factor)
- `epsilon_i` = idiosyncratic return (stock-specific surprise)

Factor risk is systematic and hard to diversify away within a single factor group. Idiosyncratic risk is diversifiable — the more positions, the lower the average idiosyncratic contribution per position.

## Beta Decomposition

**Market beta**: The most basic factor. A stock with beta=1.5 moves 1.5% for every 1% market move. APM Chapter 3 discusses separating alpha (skill-driven excess return) from beta (market-driven return). You want to be paid for alpha, not rewarded for riding a bull market.

**Sector/industry beta**: Indonesian equity portfolios dominated by banking, commodity, or consumer names will have high sector factor exposure. A concentrated bet on five banking stocks is really a sector bet, not five independent alpha bets.

## Common IDX Factors

IDX equities are influenced by several factor families relevant to Sekuritasmology:

- **Size**: Large-cap IDX (LQ45 constituents) behave differently from small-caps. Small-caps have higher idiosyncratic variance and lower liquidity.
- **Value**: Price-to-book and price-to-earnings are meaningful on IDX. Value tends to outperform in recovery cycles.
- **Momentum**: 12-1 month price momentum is a well-documented factor globally. On IDX, broker order flow momentum (captured in `broksum` signals) is a shorter-term momentum proxy.
- **Liquidity**: Stocks with low average daily trading volume (ADTV) carry a liquidity risk premium but also amplify slippage in backtests. This is why `sell_slippage_bps` matters more for small-cap signals.

## Why It Matters for Backtesting

If your signal consistently selects high-beta stocks, your backtest returns will partially reflect market beta, not signal alpha. A strong bull market period in your backtest window will inflate results. APM Chapter 8 calls this selection vs. sizing attribution: decompose whether your historical returns came from picking the right names or simply from factor tilts.

## IDX-Specific Example

A signal that always selects the top 5 stocks by market-cap change (a size/momentum mix) will embed both size and momentum factor exposures. If the backtest window coincides with an IDX bull run (e.g., 2020–2021 recovery), the Sharpe will look excellent but most gains came from market beta. Using `rank_by` with a factor-neutral column (like a residual alpha score) reduces unintended factor tilts.

## Cross-Links

- See `portfolio_construction.md` for how factor exposure interacts with equal-weight vs. fixed-cash sizing.
- See `risk_management.md` for how factor concentration affects stop-loss mechanics.
- See `performance_metrics.md` for Sharpe vs. Information Ratio distinction.
- See `backtesting_concepts.md` for survivorship and lookahead biases that corrupt factor analysis.
