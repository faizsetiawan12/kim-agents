---
topic: index
source: both
last_updated: 2026-05-28
related: []
---

# Gappy Wiki — KIM Quant Knowledge Base

TL;DR: This wiki distills Giuseppe Paleologo's two books into actionable pages for KIM principals asking Quant Bot questions or running backtests in Sekuritasmology.

## Source Books

- **APM**: *Advanced Portfolio Management: A Quant's Guide for Fundamental Investors* (Paleologo, 2021) — 211 pages. Practical framework for fundamental investors: factor models, alpha sizing, risk management, stop-loss, leverage.
- **TEQI**: *The Elements of Quantitative Investing* (Paleologo, 2025) — 403 pages. Rigorous mathematical treatment: factor models, risk evaluation, Kelly criterion, performance attribution, market microstructure.

Local copies: `/mnt/d/paleologo-books/`

## Usage Note

When a KIM principal asks a quant or market question, Quant Bot answers from these pages first. For IDX-specific context not in the books, Quant adds IDX color based on domain knowledge.

Pages are written at practitioner level — concrete, IDX-anchored, formula-light. Mathematical derivations live in the source books.

## Page List

| File | Topic | Primary Source |
| --- | --- | --- |
| `alpha_decay.md` | Signal half-life and holding period implications | TEQI |
| `factor_exposure.md` | Factor loading, beta decomposition, IDX factors | APM |
| `kelly_criterion.md` | Kelly formula, fractional Kelly, position sizing | TEQI |
| `portfolio_construction.md` | Mean-variance basics, equal-weight vs. fixed-cash | APM |
| `risk_management.md` | Stop-loss, take-profit, drawdown mechanics | APM |
| `backtesting_concepts.md` | Bias, overfitting, Rademacher, report metrics | Both |
| `market_microstructure.md` | Bid-ask spread, IDX lot size, slippage, intraday | TEQI |
| `signals_and_strategies.md` | Signal-to-noise, bool_filters, rank_by, artifacts | TEQI |
| `performance_metrics.md` | Sharpe, Sortino, Calmar, drawdown, win rate | APM |
| `indonesia_equity_context.md` | IDX rules, WIB hours, T+2, auto-rejection, Stockbit | IDX |
