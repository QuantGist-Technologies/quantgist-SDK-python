# Changelog

All notable changes to `quantgist` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — 2026-05-14

### Added

- **Earnings API** — full coverage of `GET /v1/earnings/*` routes:
  - `get_earnings(ticker, from_date, to_date, sector, beat_miss, cursor, limit)` — filtered list with cursor pagination
  - `get_earnings_upcoming(limit)` — next N upcoming reports
  - `get_earnings_for_ticker(ticker, cursor, limit)` — per-ticker history
  - `get_earnings_summary(ticker)` — beat/miss/in-line counts and beat rate
  - `get_earnings_history(ticker, cursor, limit)` — paginated history (Pro+ required)
  - `get_earnings_surprises(limit)` — largest cross-market EPS surprises
  - `get_earnings_movers(limit)` — events ranked by price/volume impact
  - `get_earnings_week_calendar()` — week-ahead calendar grouped by day
  - `get_earnings_season_summary()` — index-level aggregate for current season
- **Markets API** — `GET /v1/markets/*` EOD Stooq data:
  - `get_markets_overview()`, `get_markets_sectors()`, `get_markets_currencies()`, `get_markets_commodities()`
  - `get_market_quote(symbol)` — single symbol EOD quote
- **Changelog API** — `get_changelog()` — public API changelog (no elevated plan required)
- New Pydantic models: `EarningsEvent`, `EarningsCursorMeta`, `EarningsResponse`, `EarningsSummary`, `EarningsSurprise`, `EarningsMover`, `EarningsWeekCalendar`, `EarningsWeekDay`, `EarningsSeasonSummary`, `MarketQuote`, `MarketsOverviewResponse`, `ChangelogEntry`, `ChangelogResponse`
- `EarningsEvent` includes SEC EDGAR provenance fields: `sec_filing_url`, `sec_accession_number`, `sec_filed_at`, `field_sources`
- All new methods are available on both `QuantGistClient` (sync) and `AsyncQuantGistClient` (async)

---

## [0.1.0] — 2025-05-03

Initial public release of the official QuantGist Python SDK.

### Added

- `QuantGistClient` — synchronous client backed by `httpx.Client`
  - `get_events(from_date, to_date, country, currency, impact, symbol, limit)` — fetch paginated macro events with optional filters
  - `get_event(event_id)` — fetch a single event by ID
  - Context-manager support (`with QuantGistClient(...) as client`)
  - `close()` for explicit connection cleanup
- `AsyncQuantGistClient` — async-native client backed by `httpx.AsyncClient`
  - Same methods as sync client, all `async`; additionally supports `page` parameter on `get_events`
  - Async context-manager support (`async with AsyncQuantGistClient(...) as client`)
- Pydantic v2 data models: `Event`, `EventsResponse`, `ResponseMeta`
- Typed exception hierarchy: `QuantGistError`, `AuthenticationError`, `RateLimitError`, `NotFoundError`, `PlanUpgradeRequired`
- Automatic API key resolution from `QUANTGIST_API_KEY` environment variable
- `User-Agent` header set to `quantgist-python/<version>` on every request
- PEP 561 `py.typed` marker for downstream type checkers
- Optional extras: `quantgist[async]` (async transport), `quantgist[pandas]`
- Full type annotations; passes `pyright` in standard mode

[0.1.0]: https://github.com/quantgist/quantgist-python/releases/tag/v0.1.0
