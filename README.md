# quantgist

[![PyPI version](https://img.shields.io/pypi/v/quantgist.svg)](https://pypi.org/project/quantgist/)
[![Python versions](https://img.shields.io/pypi/pyversions/quantgist.svg)](https://pypi.org/project/quantgist/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for the [QuantGist](https://quantgist.com) macro economic event API. Get real-time and historical central bank decisions, employment reports, inflation releases, and more — with a single line of Python.

Get a free API key at [quantgist.com/signup](https://quantgist.com/signup).

---

## Install

```bash
pip install quantgist
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add quantgist
```

Requires Python 3.10+.

---

## Quick start — sync

```python
from quantgist import QuantGistClient

client = QuantGistClient(api_key="qg_live_...")

# Macro events
response = client.get_events(impact="high", currency="USD", limit=10)
for event in response.data:
    print(event.release_time, event.title, event.actual)

# Fetch a single event by ID
event = client.get_event("evt_abc123")
print(event.title, event.surprise_score)

# Earnings — upcoming reports
upcoming = client.get_earnings_upcoming(limit=10)
for e in upcoming.data:
    print(e.report_date, e.ticker, e.eps_estimate)

# Earnings — per-ticker beat/miss summary
summary = client.get_earnings_summary("AAPL")
print(f"AAPL beat rate: {summary.beat_rate:.0%}")

# Markets overview
overview = client.get_markets_overview()
for q in overview.data:
    print(q.symbol, q.close, q.change_pct)

# Changelog (no auth required)
changelog = client.get_changelog()
print(changelog.data[0].version, changelog.data[0].summary)
```

## Quick start — async

```python
import asyncio
from quantgist import AsyncQuantGistClient

async def main():
    async with AsyncQuantGistClient(api_key="qg_live_...") as client:
        response = await client.get_events(
            impact="high",
            currency="USD",
            from_date="2024-01-01",
            to_date="2024-12-31",
        )
        for event in response.data:
            print(event.release_time, event.title, event.actual)

asyncio.run(main())
```

---

## Environment variable

Set `QUANTGIST_API_KEY` and omit the `api_key=` argument entirely:

```bash
export QUANTGIST_API_KEY="qg_live_..."
```

```python
client = QuantGistClient()  # reads from env
```

---

## API reference

### `QuantGistClient(api_key, base_url, timeout)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str \| None` | `None` | API key. Falls back to `QUANTGIST_API_KEY` env var. |
| `base_url` | `str` | `"https://api.quantgist.com/v1"` | Override for self-hosted or staging environments. |
| `timeout` | `float` | `30.0` | Request timeout in seconds. |

Raises `AuthenticationError` immediately if no key is found.

Supports use as a context manager:

```python
with QuantGistClient(api_key="qg_live_...") as client:
    response = client.get_events()
```

---

### Methods — macro events

| Method | Returns | Description |
|--------|---------|-------------|
| `get_events(*, from_date, to_date, country, currency, impact, symbol, limit)` | `EventsResponse` | Fetch a paginated list of macro events with optional filters. |
| `get_event(event_id)` | `Event` | Fetch a single event by its unique ID. |
| `close()` | `None` | Close the underlying HTTP connection. Called automatically as a context manager. |

#### `get_events` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `from_date` | `date \| datetime \| str \| None` | `None` | Start of time range (ISO 8601, e.g. `"2024-01-01"`). |
| `to_date` | `date \| datetime \| str \| None` | `None` | End of time range (ISO 8601). |
| `country` | `str \| None` | `None` | ISO 2-char country code, e.g. `"US"`, `"GB"`. |
| `currency` | `str \| None` | `None` | Currency code, e.g. `"USD"`, `"EUR"`. |
| `impact` | `"low" \| "medium" \| "high" \| None` | `None` | Filter by market impact level. |
| `symbol` | `str \| None` | `None` | Instrument symbol, e.g. `"XAUUSD"`, `"EURUSD"`. |
| `limit` | `int` | `50` | Maximum number of results (1–500). |

---

### Methods — earnings

| Method | Returns | Description |
|--------|---------|-------------|
| `get_earnings(*, ticker, from_date, to_date, sector, beat_miss, cursor, limit)` | `EarningsResponse` | Filtered, cursor-paginated list of earnings events. |
| `get_earnings_upcoming(*, limit)` | `EarningsResponse` | Next N upcoming earnings reports ordered by date. |
| `get_earnings_for_ticker(ticker, *, cursor, limit)` | `EarningsResponse` | Earnings history for a single ticker. |
| `get_earnings_summary(ticker)` | `EarningsSummary` | Beat/miss/in-line counts for a ticker. |
| `get_earnings_history(ticker, *, cursor, limit)` | `EarningsResponse` | Paginated earnings history (**Pro+ plan required**). |
| `get_earnings_surprises(*, limit)` | `list[EarningsSurprise]` | Largest cross-market EPS surprises. |
| `get_earnings_movers(*, limit)` | `list[EarningsMover]` | Earnings events ranked by price/volume impact. |
| `get_earnings_week_calendar()` | `EarningsWeekCalendar` | Week-ahead earnings calendar grouped by day. |
| `get_earnings_season_summary()` | `EarningsSeasonSummary` | Index-level aggregate for the current earnings season. |

---

### Methods — markets

| Method | Returns | Description |
|--------|---------|-------------|
| `get_markets_overview()` | `MarketsOverviewResponse` | Major indices and instruments (EOD Stooq data). |
| `get_markets_sectors()` | `MarketsOverviewResponse` | Major sector ETF quotes. |
| `get_markets_currencies()` | `MarketsOverviewResponse` | Major currency pair quotes. |
| `get_markets_commodities()` | `MarketsOverviewResponse` | Major commodity quotes. |
| `get_market_quote(symbol)` | `MarketQuote` | Latest EOD quote for a single symbol. |

---

### Methods — changelog

| Method | Returns | Description |
|--------|---------|-------------|
| `get_changelog()` | `ChangelogResponse` | Public API changelog — no elevated plan required. |

---

### `AsyncQuantGistClient`

Drop-in async replacement. Identical constructor and method signatures; all methods are `async`. Additionally supports a `page: int` parameter on `get_events` for explicit pagination.

```python
async with AsyncQuantGistClient(api_key="qg_live_...") as client:
    page1 = await client.get_events(limit=100, page=1)
    page2 = await client.get_events(limit=100, page=2)
```

---

### Data models

#### `Event`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique event identifier. |
| `title` | `str` | Human-readable event name, e.g. `"US Non-Farm Payrolls"`. |
| `country` | `str` | ISO country code of the releasing country. |
| `currency` | `str` | Primary affected currency. |
| `release_time` | `datetime` | Release timestamp (UTC, timezone-aware). |
| `impact` | `"low" \| "medium" \| "high"` | Market impact classification. |
| `forecast` | `float \| None` | Analyst consensus forecast. |
| `previous` | `float \| None` | Prior period's value. |
| `actual` | `float \| None` | Released actual value (`None` if not yet released). |
| `surprise_score` | `float \| None` | Deviation of actual vs forecast, normalised. |
| `affected_symbols` | `list[str]` | Instruments expected to react (e.g. `["EURUSD", "XAUUSD"]`). |
| `source` | `str` | Data source identifier. |

#### `EventsResponse`

| Field | Type | Description |
|-------|------|-------------|
| `data` | `list[Event]` | The list of events. |
| `meta` | `ResponseMeta` | Pagination and rate-limit metadata. |

#### `ResponseMeta`

| Field | Type | Description |
|-------|------|-------------|
| `total` | `int` | Total matching events (across all pages). |
| `page` | `int` | Current page number. |
| `per_page` | `int` | Results per page. |
| `rate_limit_remaining` | `int \| None` | Remaining requests in the current window. |

---

#### `EarningsEvent`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique earnings event identifier. |
| `ticker` | `str` | Stock ticker symbol. |
| `company_name` | `str` | Company display name. |
| `report_date` | `date` | Date of the earnings release. |
| `fiscal_quarter` | `str \| None` | Fiscal period label, e.g. `"Q1 2025"`. |
| `eps_estimate` | `float \| None` | Consensus EPS estimate. |
| `eps_actual` | `float \| None` | Reported EPS (`None` if not yet released). |
| `revenue_estimate` | `float \| None` | Consensus revenue estimate (USD). |
| `revenue_actual` | `float \| None` | Reported revenue (`None` if pending). |
| `surprise_pct` | `float \| None` | EPS % surprise vs estimate. |
| `beat_miss` | `"beat" \| "miss" \| "in-line" \| None` | Outcome classification. |
| `market_cap` | `float \| None` | Market cap at time of report (USD). |
| `sector` | `str \| None` | GICS sector. |
| `report_time` | `"before_open" \| "after_close" \| "during_market" \| None` | When the report was released. |
| `sec_filing_url` | `str \| None` | URL to the SEC EDGAR 8-K filing. |
| `sec_accession_number` | `str \| None` | SEC accession number, e.g. `"0000320193-26-000001"`. |
| `sec_filed_at` | `date \| None` | Date filed with the SEC. |
| `field_sources` | `dict[str, str]` | Provenance map per field, e.g. `{"eps_actual": "fmp", "sec_filing_url": "sec_edgar"}`. |

#### `EarningsSummary`

| Field | Type | Description |
|-------|------|-------------|
| `ticker` | `str` | Ticker symbol. |
| `company_name` | `str \| None` | Company display name. |
| `beat` | `int` | Number of quarters where EPS beat estimates. |
| `miss` | `int` | Number of quarters where EPS missed estimates. |
| `in_line` | `int` | Number of in-line quarters. |
| `total` | `int` | Total quarters in the history. |
| `beat_rate` | `float \| None` | Beat rate as a percentage (0–100). |

#### `MarketQuote`

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Instrument symbol. |
| `name` | `str \| None` | Display name. |
| `close` | `float` | Latest close price. |
| `open` | `float \| None` | Open price. |
| `high` | `float \| None` | Day high. |
| `low` | `float \| None` | Day low. |
| `volume` | `float \| None` | Volume. |
| `change_pct` | `float \| None` | Day change percentage. |
| `as_of` | `date \| None` | Quote date. |

#### `ChangelogEntry`

| Field | Type | Description |
|-------|------|-------------|
| `version` | `str` | Semantic version string. |
| `date` | `date` | Release date. |
| `summary` | `str` | Short description of the release. |
| `breaking` | `bool` | Whether this version contains breaking changes. |
| `changes` | `list[str]` | Bullet-point change list. |

---

## Error handling

All exceptions inherit from `QuantGistError` and expose a `.status_code` attribute.

```python
from quantgist import (
    QuantGistClient,
    QuantGistError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    PlanUpgradeRequired,
)

client = QuantGistClient(api_key="qg_live_...")

try:
    event = client.get_event("evt_does_not_exist")
except AuthenticationError as e:
    # 401 — invalid or missing API key
    print(f"Auth failed: {e}")
except RateLimitError as e:
    # 429 — too many requests; upgrade plan or back off
    print(f"Rate limited (status {e.status_code}): {e}")
except NotFoundError as e:
    # 404 — event ID does not exist
    print(f"Not found: {e}")
except PlanUpgradeRequired as e:
    # 402 — feature requires a higher subscription tier
    print(f"Upgrade required: {e}")
except QuantGistError as e:
    # catch-all for any other API errors
    print(f"API error {e.status_code}: {e}")
```

| Exception | HTTP status | Cause |
|-----------|-------------|-------|
| `AuthenticationError` | 401 | Invalid or missing API key. |
| `RateLimitError` | 429 | Request quota exceeded for the current plan. |
| `NotFoundError` | 404 | The requested resource does not exist. |
| `PlanUpgradeRequired` | 402 | Feature is not available on the current plan tier. |
| `QuantGistError` | any | Base class; wraps all other unexpected errors. |

---

## Examples

See the [`examples/`](../../examples/) directory for runnable scripts covering:

- Basic event fetch and filtering
- Async batch fetching across multiple currencies
- Pandas DataFrame integration
- Discord bot with real-time event alerts

---

## Links

- API docs: [quantgist.com/docs](https://quantgist.com/docs)
- Sign up for a free key: [quantgist.com/signup](https://quantgist.com/signup)
- GitHub: [github.com/quantgist/quantgist-python](https://github.com/quantgist/quantgist-python)
- Issue tracker: [github.com/quantgist/quantgist-python/issues](https://github.com/quantgist/quantgist-python/issues)
