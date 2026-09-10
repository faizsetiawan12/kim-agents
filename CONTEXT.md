# KIM Domain Model

Ubiquitous language, canonical terminology, and domain boundaries for Kodja Investment Management (KIM).

See `CONTEXT-MAP.md` for repository-specific glossaries.

## Language & Terminology

### Company & Business

**KIM (Kodja Investment Management)**:
A holding company and proprietary investment partnership owned by Faiz, Jimmy, Oscar, and Wahyu. Self-funded: revenue from software products funds internal quantitative research.

**KATMA (Kodja Attribution Management)**:
KIM's commercial SaaS product (`repos/katma`). Calculates portfolio price return against IHSG, decomposes performance into sector and holding contributions, and generates client attribution reports for Indonesian fund managers.

**Kotrade**:
KIM's quantitative research and live execution platform (`repos/kotrade`). Formerly named Sekuritasmology; see Naming below.

**Sekuritasmology**:
Reserved strictly for: (1) the legacy strategy family `Sekuritasmology Broksum Analysis V1`, and (2) the GitHub remote URL `github.com/ytb664/sekuritasmology.git`. In all other contexts, use **Kotrade**.

**RDN (Rekening Dana Nasabah)**:
An Indonesian bank account registered under an individual investor's name dedicated to stock trading. Personal investment funds of KIM principals are managed in Wahyu's Stockbit RDN.

**Flywheel**:
KIM's operational financial model: Product revenue (KATMA) → funds research and infrastructure → yields alpha strategies in Kotrade → generates returns to scale without external capital.

### Indonesian Market (IDX)

**IDX (Indonesia Stock Exchange)**:
The equity exchange where KIM models operate.
_Avoid_: BEI, Jakarta Stock Exchange (outdated)

**IHSG (Indeks Harga Saham Gabungan)**:
The Jakarta Composite Index. KIM's primary benchmark for portfolio attribution and market-relative returns.

**LQ45**:
The index of the 45 most liquid, highly capitalized stocks on the IDX, reviewed semi-annually. Primary universe for sector models.

**WIB (Waktu Indonesia Barat, UTC+7)**:
The canonical timezone for all KIM operations, pipelines, timestamps, and cron jobs. Never use UTC or system-local time in logs or code without explicit conversion to WIB.

**Bandarmology (Broker Flow)**:
The study and quantitative modeling of institutional and broker order-flow patterns from IDX broker summary data. In KIM terminology, modeled rigorously as an alpha factor rather than informal retail charting.
_Avoid_: Bandar reading, retail tape reading

**Broker Summary**:
Per-broker, per-day buy and sell volume and value data released post-market for each ticker on the IDX.
_Avoid_: Broksum (acceptable only as informal shorthand), broker list

**Stockbit**:
The third-party platform that provides market-data feeds and order-execution access to the IDX for Kotrade.
_Note_: Stockbit is NOT an IDX broker firm; it is an investing platform and interface.

**Exodus Token vs Carina Token**:
Two different authentication JWTs provided by Stockbit:
- **Exodus Token**: Platform-layer token used for market data and broker summary scraping (`https://stockbit.com/stream`).
- **Carina Token**: Brokerage-layer token used for order execution and portfolio state (`https://stockbit.com/securities/portfolio`). Has ~8h TTL; must be refreshed pre-market.

### Quantitative & Research

**Alpha Factor**:
A mathematical formulation or quantitative signal designed to forecast relative asset returns.
_Avoid_: Indicator, technical formula, predictor

**Universe**:
The pre-defined set of tradable securities meeting explicit liquidity and asset-class criteria for analysis or modeling.
_Avoid_: Watchlist, stock list, pool

**Backtest Run**:
A simulated historical execution of a defined quantitative strategy against past market data, evaluated under explicit cost and risk assumptions.
_Avoid_: Simulation run, paper test

**Risk Model**:
A mathematical framework decomposing portfolio risk into systematic factor exposures and idiosyncratic risk.
_Avoid_: Risk checker, drawdown filter

**Trade Thesis**:
A structured analytical hypothesis outlining the quantitative rationale, expected horizon, and risk-reward profile for an investment idea.
_Avoid_: Trade call, tip, buy signal

**PVR (Position Valuation Report)**:
A portfolio valuation snapshot containing holdings, quantities, and market values, used as input for KATMA attribution calculations.

### Operations & Infrastructure

**Pipeline**:
The automated end-to-end data ingestion, validation, factor computation, and storage workflow in Kotrade.
_Avoid_: Data job, backend script

**Incident**:
An unexpected disruption, data pipeline failure, or infrastructure degradation impacting operations.
_Avoid_: Glitch, issue, bug report

**Auto-Repair**:
An autonomous diagnostic and recovery action executed by Ops to resolve low-risk operational failures without prior human intervention.
_Avoid_: Quick patch, self-fix

**Telemetry**:
Structured log events, execution metrics, and health data emitted by pipeline scripts.
_Avoid_: Print logs, script output

**today_entries.json**:
The canonical state file (`repos/kotrade/modules/live_execution/data/state/today_entries.json`) produced by the nightly trade decision, containing ranked and holdings-filtered candidate orders for morning dispatch.
