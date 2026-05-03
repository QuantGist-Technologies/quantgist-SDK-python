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

response = client.get_events(impact="high", currency="USD", limit=10)
for event in response.data:
    print(event.release_time, event.title, event.actual)

# Fetch a single event by ID
event = client.get_event("evt_abc123")
print(event.title, event.surprise_score)
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

### Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `get_events` | `(*, from_date, to_date, country, currency, impact, symbol, limit) -> EventsResponse` | `EventsResponse` | Fetch a paginated list of macro events with optional filters. |
| `get_event` | `(event_id: str) -> Event` | `Event` | Fetch a single event by its unique ID. |
| `close` | `() -> None` | `None` | Close the underlying HTTP connection. Called automatically when used as a context manager. |

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
