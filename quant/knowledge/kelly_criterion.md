---
topic: kelly_criterion
source: TEQI
last_updated: 2026-05-28
related: [portfolio_construction, risk_management, performance_metrics, signals_and_strategies]
---

# Kelly Criterion

TL;DR: Kelly tells you the mathematically optimal fraction of capital to allocate to a strategy for maximum long-run growth. In practice, use fractional Kelly — full Kelly results in ruinous drawdowns.

## The Core Formula

TEQI Chapter 13 derives the Kelly criterion from first principles. For a strategy with expected excess return `mu` and volatility `sigma`:

```
x* ≈ mu / sigma^2 = Sharpe_Ratio / sigma
```

Equivalently:
```
x* ≈ SR / sigma
long-run growth rate ≈ 0.5 * SR^2
```

Where `SR = mu / sigma` is the Sharpe Ratio. The optimal fraction `x*` is the proportion of capital to allocate to the active strategy.

## Key Properties

**Kelly maximizes long-run growth**: TEQI proves that no strategy with a different expected growth rate will beat Kelly almost surely over the long run (Equation 13.12). This is mathematically optimal, not just practically useful.

**But drawdowns are severe**: A full Kelly strategy applied to the US market benchmark (S&P 500) with SR ≈ 0.4 and annual volatility ≈ 19% would call for roughly 200% leverage. The historical drawdowns of such a strategy are enormous — capital can drop by 50–80% before recovering.

**Fractional Kelly**: Use a fraction `f` of the full Kelly allocation. Common choices are 0.25x or 0.5x. TEQI Insight 13.2 notes that "all reasonable investors use fractional Kelly without knowing it" — any strategy with constant volatility-to-capital ratio implicitly is fractional Kelly.

**Parameter uncertainty shrinks Kelly**: When the true expected return is uncertain (as it always is in practice), the optimal allocation is smaller than the point estimate suggests. TEQI Example 13.6 shows that adding estimation uncertainty to the S&P500 parameters reduces the optimal fraction from 1.88x to 1.52x.

## Why `_kelly_fraction` Columns Appear in Artifacts

Sekuritasmology signal artifacts often contain columns ending in `_kelly_fraction`. These are pre-computed signal-level Kelly fractions derived from each signal's historical IC and volatility estimates. When you `rank_by` a `_kelly_fraction` column, you are ordering signals by their theoretically optimal allocation size rather than by raw predicted return. This tends to produce more stable portfolios than ranking by raw score.

## IDX-Specific Example

Suppose a broksum signal has an estimated annualized Sharpe Ratio of 0.8 on IDX data, with a strategy volatility of 15%. The full Kelly fraction would be `0.8 / 0.15 ≈ 5.3x` — clearly impractical on IDX given lot-size constraints and thin liquidity. Even 0.25x fractional Kelly (1.3x) would be aggressive for small-cap IDX names. In practice, `initial_capital = 100,000,000` IDR with `max_positions = 5` and equal weighting already embeds a sensible capital constraint.

## In the Backtest Skill

Phase 4 does not ask for a Kelly input directly. However, when `rank_by` selects a `_kelly_fraction` column in Phase 1, the signal ordering already incorporates Kelly-theoretic sizing guidance. The resulting selection feeds into equal-weight or fixed-cash sizing in Phase 2.

## Cross-Links

- See `signals_and_strategies.md` for `rank_by` and artifact column structure.
- See `portfolio_construction.md` for how sizing mode interacts with Kelly intuition.
- See `risk_management.md` for how stop-loss effectively caps the downside that makes full Kelly dangerous.
- See `performance_metrics.md` for Sharpe Ratio interpretation and annualization.
