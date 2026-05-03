# Point-in-Time Data with QuantGist

## The problem

When backtesting a news-based strategy, you must use data that was **available at the time of the decision** — not data that was revised or released later.

Example: The BLS revises CPI figures. If you use the revised figures in a backtest, your model "knows" information the market didn't have. This is **lookahead bias**.

QuantGist stores the original `actual`, `forecast`, and `previous` values as they were at release time. Revised figures appear as separate events.

---

## What QuantGist provides

Each event record includes:

| Field | Description | Point-in-time safe? |
|-------|-------------|---------------------|
| `release_time` | UTC timestamp of release | ✅ Yes |
| `forecast` | Consensus forecast at release | ✅ Yes |
| `actual` | Reported actual at release | ✅ Yes (initial print) |
| `previous` | Prior period value (as shown at release) | ✅ Yes |
| `revised` | Revision to `previous`, if any | ✅ Yes (separate record) |

---

## Safe backtest pattern

```python
from datetime import datetime, timezone
from quantgist import QuantGistClient

client = QuantGistClient()

# Fetch events for your backtest window
events = client.get_events(
    from_time=datetime(2023, 1, 1, tzinfo=timezone.utc),
    to_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
    country="US",
    impact="high",
)

# Process events in chronological order — as if you were live
for event in sorted(events, key=lambda e: e.release_time):
    if event.actual is None:
        continue  # skip scheduled events that hadn't released yet

    surprise = event.actual - event.forecast
    # Your strategy logic here — only using data available at event.release_time
    print(f"{event.release_time}: {event.title} surprise={surprise:+.2f}")
```

---

## Avoiding common pitfalls

### ❌ Don't do this
```python
# Fetching "today's" data and filtering by past dates
events = client.get_events()  # gets current/latest values
past_events = [e for e in events if e.release_time < my_backtest_end]
```

This is fine if you're only using `release_time`, `forecast`, and the **initial** `actual`. But if the API returns revised actuals in the same record, you'd be using future data.

### ✅ Do this instead
Fetch with an explicit `to_time` set to your backtest end date, and only use the `actual` field (the initial print). Treat any `revised` field as separate events with their own timestamps.

---

## Surprise calculation

```python
def compute_surprise(event) -> float | None:
    if event.actual is None or event.forecast is None:
        return None
    return event.actual - event.forecast

def surprise_direction(surprise: float) -> str:
    if surprise > 0.05:
        return "hot"
    if surprise < -0.05:
        return "cold"
    return "inline"
```

---

## Cross-referencing with OHLCV data

QuantGist provides event timestamps in UTC. When joining with broker OHLCV data:

1. Ensure your OHLCV index is timezone-aware (`tz_localize("UTC")` in pandas)
2. Use `searchsorted` or `asof` to find the candle at release time — avoid `loc` with exact match since candle open times rarely coincide exactly with event timestamps
3. Add a small offset (30–60 seconds) to avoid the first partial candle

```python
import pandas as pd

# ohlcv_df: DataFrame with DatetimeIndex (UTC)
def get_candle_at_release(ohlcv_df: pd.DataFrame, release_time, offset_seconds=60):
    target = release_time + pd.Timedelta(seconds=offset_seconds)
    idx = ohlcv_df.index.searchsorted(target)
    if idx >= len(ohlcv_df):
        return None
    return ohlcv_df.iloc[idx]
```
