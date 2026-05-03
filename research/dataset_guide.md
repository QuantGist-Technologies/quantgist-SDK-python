# QuantGist Dataset Guide

## What's in the dataset

The QuantGist API serves macro economic event data from multiple sources, normalized into a consistent schema.

### Event fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique event identifier |
| `title` | `str` | Event name (e.g. "US Non-Farm Payrolls") |
| `currency` | `str` | Primary currency affected (ISO 4217) |
| `country` | `str` | ISO 2-letter country code |
| `impact` | `str` | `"high"`, `"medium"`, or `"low"` |
| `release_time` | `datetime` | UTC release timestamp |
| `actual` | `float \| None` | Reported value (None before release) |
| `forecast` | `float \| None` | Consensus estimate |
| `previous` | `float \| None` | Prior period value |
| `affected_symbols` | `list[str]` | Forex/commodity symbols likely affected |
| `source` | `str` | Data source identifier |

---

## Coverage

| Region | High-Impact Events | Coverage |
|--------|--------------------|----------|
| United States | NFP, CPI, PCE, FOMC, GDP, Retail Sales, ISM | 2019–present |
| Eurozone | ECB Rate Decision, CPI Flash, GDP | 2019–present |
| United Kingdom | BoE Rate, CPI, GDP | 2019–present |
| Japan | BoJ Rate, CPI, GDP, Trade | 2019–present |
| Canada | BoC Rate, CPI, GDP | 2020–present |
| Australia | RBA Rate, CPI, Employment | 2020–present |

Free tier: 30 days history. Paid tiers: full history from 2019.

---

## Most useful events for trading strategies

### Tier 1 — Market-moving (always high impact)

| Event | Currency | Symbol Impact |
|-------|----------|---------------|
| Non-Farm Payrolls (NFP) | USD | All USD pairs, Gold, Indices |
| CPI (US) | USD | All USD pairs |
| Fed Rate Decision / FOMC | USD | All markets |
| ECB Rate Decision | EUR | All EUR pairs |
| BoE Rate Decision | GBP | All GBP pairs |

### Tier 2 — Often high impact

| Event | Currency | Notes |
|-------|----------|-------|
| GDP (US, EU, UK) | USD/EUR/GBP | Quarterly |
| PCE Price Index | USD | Fed's preferred inflation gauge |
| ISM Manufacturing/Services | USD | Sentiment |
| Retail Sales (US) | USD | Consumer spending |

---

## Filtering recipes

### Get only US Tier 1 events
```python
TIER1_KEYWORDS = ["Non-Farm", "CPI", "FOMC", "Fed Rate", "Retail Sales GDP"]

events = client.get_events(country="US", impact="high")
tier1 = [e for e in events if any(kw in e.title for kw in TIER1_KEYWORDS)]
```

### Get events affecting Gold (XAUUSD)
```python
events = client.get_events(impact="high")
gold_events = [e for e in events if "XAUUSD" in (e.affected_symbols or [])]
```

### Get events with surprise data (actual ≠ forecast)
```python
events = client.get_events(from_time=..., to_time=..., impact="high")
with_surprise = [
    e for e in events
    if e.actual is not None and e.forecast is not None and e.actual != e.forecast
]
```

---

## Data quality notes

- **Forecast may be None** for events where no consensus exists (e.g. some central bank speeches)
- **Actual is None** for future events — always check before computing surprise
- **release_time is always UTC** — convert to broker time for MT5/chart alignment
- **affected_symbols** is best-effort — a CPI event affecting USD will list major USD pairs but may not list every exotic

---

## Pagination

The API returns up to 500 events per request. For large date ranges, paginate:

```python
from datetime import datetime, timedelta, timezone

def fetch_all_events(client, from_time, to_time, **kwargs):
    results = []
    cursor = from_time
    chunk = timedelta(days=90)

    while cursor < to_time:
        end = min(cursor + chunk, to_time)
        batch = client.get_events(from_time=cursor, to_time=end, **kwargs)
        results.extend(batch)
        cursor = end

    return results
```

---

## Building a research DataFrame

```python
import pandas as pd
from quantgist import QuantGistClient

client = QuantGistClient()
events = client.get_events(country="US", impact="high", ...)

df = pd.DataFrame([e.model_dump() for e in events])
df["release_time"] = pd.to_datetime(df["release_time"], utc=True)
df["surprise"] = df["actual"] - df["forecast"]
df.set_index("release_time", inplace=True)
df.sort_index(inplace=True)
```
