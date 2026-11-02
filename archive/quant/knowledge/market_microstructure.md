---
topic: market_microstructure
source: TEQI
last_updated: 2026-05-28
related: [signals_and_strategies, portfolio_construction, risk_management, indonesia_equity_context]
---

# Market Microstructure

TL;DR: Microstructure is the plumbing of how trades actually execute. Bid-ask spread and slippage are real costs that backtests tend to underestimate. On IDX, lot size and thin order books make these costs especially relevant for small-cap names.

## Bid-Ask Spread

The bid price is what buyers offer; the ask is what sellers demand. Every trade crosses the spread. If bid = 990 and ask = 1000, buying at the ask and immediately selling at the bid loses 10 IDR per share — 1% of position value.

TEQI covers spread as a component of transaction cost. For IDX large-caps (LQ45 names), spreads are typically 1–3 bps (one tick on the minimum tick size grid). For small-caps, spreads of 10–50 bps are common.

## Slippage

Slippage is the difference between the expected price and the actual execution price when placing a market or limit order. Causes:
1. **Market impact**: Your order moves the price, especially for large orders in thin markets.
2. **Partial fill**: At the expected price, not enough volume exists.
3. **Timing**: Between signal generation and order placement, price has moved.

In Sekuritasmology's backtest engine, slippage is modeled as:
```
buy_slippage_bps  = 0  (default)
sell_slippage_bps = 0  (default)
```

The default of 0 is optimistic. A more conservative setup for IDX small-caps might use 10–20 bps per side. Set `buy_slippage_bps` and `sell_slippage_bps` in Phase 4 based on the expected liquidity of the signal's target stocks.

## IDX Lot Size (100 Shares)

On IDX, shares trade in lots of 100 shares (odd-lot market exists but is less liquid). The `lot_size = 100` default in Sekuritasmology reflects this. Smaller lot sizes would be unrealistic for normal sessions.

**Implication for position sizing**: A stock at Rp 5,000/share trades in minimum units of Rp 500,000 (one lot). If your equal-weight allocation is Rp 20M per position, you can buy 40 lots. If the stock trades Rp 2M/day in daily volume, entering 40 lots (Rp 20M) is already 10x daily average — that is market-moving and your backtest slippage model is too optimistic.

## Intraday Patterns on IDX

IDX trading session: 09:00–11:30 WIB (morning), 13:30–15:00 WIB (afternoon), Pre-closing 15:00–15:15 WIB. Volume is typically highest at open and close. Key microstructure considerations:
- **Opening auction**: First available bar (09:00 WIB open) is often volatile with wide spreads.
- **Afternoon session**: Lower volume, wider spreads on most days.
- **Entry timing**: Using `entry_time_mode = after_hhmm` with `entry_time_hhmm = 09:30` avoids the opening auction noise and allows the market to settle.

## Bps in the Backtest

The cost model in Phase 4 uses basis points (bps) for all fees and slippage. One bps = 0.01% of notional. IDX standard broker fees:
- Buy: ~15–25 bps
- Sell: ~25–35 bps (includes IDX levy)

The default in Sekuritasmology (`buy_fee_bps = 15`, `sell_fee_bps = 25`) is on the lower end — matching discount broker rates. Traditional full-service brokers charge 25–30 bps buy and 35–40 bps sell.

## IDX-Specific Example

A signal fires on BBCA (Bank Central Asia) at Rp 9,500/share. With `initial_capital = 100,000,000` and `max_positions = 5`, the position size is Rp 20M = ~210 lots. BBCA trades 200,000+ lots per day, so market impact is negligible. Slippage ≈ 0. Now apply the same logic to a small-cap with Rp 1B/day volume: 210 lots is 21% of daily volume — you would definitely move the market. Set `buy_slippage_bps = 20` and `sell_slippage_bps = 20` to simulate realistic execution for small-cap names.

## Cross-Links

- See `indonesia_equity_context.md` for full IDX trading rules, auto-rejection, and T+2.
- See `portfolio_construction.md` for how lot size affects the minimum feasible position.
- See `risk_management.md` for how slippage interacts with stop-loss execution quality.
- See `signals_and_strategies.md` for how to filter for liquid names using `bool_filters`.
