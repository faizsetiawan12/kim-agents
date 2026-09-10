---
topic: indonesia_equity_context
source: IDX
last_updated: 2026-05-28
related: [market_microstructure, portfolio_construction, risk_management, backtesting_concepts]
---

# Indonesia Equity Context

TL;DR: IDX has distinct rules that differ from US and European exchanges: lot size of 100 shares, auto-rejection limits at ±25%, T+2 settlement, WIB (UTC+7) trading hours, and Stockbit as the primary data source for Sekuritasmology. These rules affect every backtest parameter choice.

## Trading Hours (WIB = UTC+7)

| Session | Time WIB |
| --- | --- |
| Pre-opening | 08:45 – 09:00 |
| Morning session | 09:00 – 11:30 |
| Lunch break | 11:30 – 13:30 |
| Afternoon session | 13:30 – 15:00 |
| Pre-closing | 15:00 – 15:15 |
| Closing auction | 15:15 – 15:20 |
| Post-trading | 15:20 – 15:30 |

**For backtests**: `entry_time_mode = first_bar` enters at the 09:00 open. `entry_time_mode = after_hhmm` with 09:30 allows the opening auction to settle. For intraday strategies, `exit_time_hhmm` must be before 15:00 for the afternoon session.

## Auto-Rejection Limits

IDX applies an auto-rejection mechanism that halts trading if a stock moves beyond these limits in a single session:
- **Standard stocks**: ±25% from the previous close reference price.
- **Certain listed stocks**: May have narrower limits.

**Practical implication for backtests**: If a stop-loss triggers at -10% but the stock gaps -30% at open (e.g., after a negative announcement), your backtest will model a -25% exit (auto-rejection limit) rather than -10%. This is one reason real execution can be worse than backtest results suggest. Do not set `stop_loss` levels deeper than 20% for IDX stocks.

## Lot Size: 100 Shares

All IDX shares trade in standard lots of 100 shares. An odd-lot market exists for fractional trading but is illiquid. Sekuritasmology uses `lot_size = 100` as default.

**Minimum position value**: At IDX minimum tick price Rp 50/share, one lot = Rp 5,000. At a typical mid-cap price of Rp 2,000/share, one lot = Rp 200,000. A Rp 20M position at Rp 2,000/share = 100 lots.

## T+2 Settlement

IDX uses T+2 settlement: trades executed today settle (cash and shares transfer) two business days later. For cash-funded long strategies, this means:
- You need capital available at trade time.
- Proceeds from a sale are not available for two days.
- In the Sekuritasmology backtest engine, T+2 is not explicitly modeled — the engine assumes cash is available immediately. In live trading, cash management must account for settlement cycles.

## Holiday Calendar

IDX observes Indonesian national holidays (typically 14–18 per year) plus Islamic calendar holidays (variable dates). This reduces the annual trading day count from 260 calendar weekdays to approximately 240–252 trading days. Sekuritasmology uses 252 for annualization. Signal artifacts include only actual trading days in date ranges.

When setting `start_signal_date` and `end_signal_date`, avoid expecting exact daily frequency — there will be gaps for holidays. The engine handles this correctly.

## Stockbit as Data Source

Sekuritasmology's primary market data comes from Stockbit (stockbit.com):
- **EXODUS token**: Used for market data (OHLCV, broker data).
- **CARINA token**: Used for orders and portfolio operations.

Tokens expire frequently (EXODUS has a ~24h TTL). The Engineer health check monitors token expiry. If data collection fails, signal artifacts may be stale — check `MEMORY.md` for current token status before requesting a backtest on recent dates.

## IDX-Specific Factors

IDX-relevant factor tilts in Sekuritasmology signals:
- **Broker flow**: Sekuritasmology specializes in broker summary (broksum) signals — detecting institutional accumulation/distribution patterns from broker-level order flow. This is an IDX-specific data advantage not available in US markets.
- **Commodity exposure**: IDX has heavy energy and mining sector weights. Macro commodity price moves create sector factor returns.
- **Foreign flow**: Foreign institutional investment in/out of IDX is a systemic factor. High foreign outflow periods coincide with IDR depreciation and broad equity sell-offs.

## Cross-Links

- See `market_microstructure.md` for bid-ask spread, slippage, and intraday patterns.
- See `risk_management.md` for auto-rejection interaction with stop-loss.
- See `portfolio_construction.md` for lot size and minimum position size calculations.
- See `backtesting_concepts.md` for how holiday calendar and T+2 affect backtest realism.
