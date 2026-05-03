# %% [markdown]
# # Surprise Momentum Strategy Template
#
# Entry rule: when a high-impact event releases with a significant surprise
# (|actual − forecast| > threshold), open a momentum trade in the direction
# of the surprise and hold for a fixed duration.
#
# Positive surprise on a USD event → USD strength → sell EURUSD / buy USDJPY
# Negative surprise → USD weakness → buy EURUSD / sell USDJPY

# %%
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

import pandas as pd
import matplotlib.pyplot as plt
from quantgist import QuantGistClient

# ──────────────────────────────────────────────────────────────────────────────
# Parameters
# ──────────────────────────────────────────────────────────────────────────────
SYMBOL = "EURUSD"
EVENT_COUNTRY = "US"  # positive US surprise → USD up → EURUSD down
SURPRISE_THRESHOLD = 0.1  # minimum |surprise| to trigger a trade
HOLD_MINUTES = 30  # hold the trade for N minutes after entry
ENTRY_DELAY_SECONDS = 30  # wait N seconds after release before entering
IMPACT_FILTER = "high"
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class Trade:
    event_title: str
    release_time: datetime
    direction: Literal["long", "short"]
    entry_time: datetime
    exit_time: datetime
    surprise: float
    entry_price: float = 0.0
    exit_price: float = 0.0
    pnl_pips: float = 0.0


def compute_surprise(event) -> float | None:
    if event.actual is None or event.forecast is None:
        return None
    return event.actual - event.forecast


def signal_direction(surprise: float, event_currency: str, symbol: str) -> Literal["long", "short"] | None:
    """
    Determine trade direction based on surprise and symbol.
    For USD events on EURUSD: positive surprise → USD up → short EURUSD
    """
    base_currency = symbol[:3]
    quote_currency = symbol[3:]

    if event_currency == quote_currency:
        return "long" if surprise > 0 else "short"
    if event_currency == base_currency:
        return "short" if surprise > 0 else "long"
    return None  # event currency not in symbol — skip


def get_price_at_time(ohlcv_df: pd.DataFrame, target_time: datetime) -> float | None:
    """Get the close price at or after target_time."""
    idx = ohlcv_df.index.searchsorted(target_time)
    if idx >= len(ohlcv_df):
        return None
    return float(ohlcv_df.iloc[idx]["close"])


def run_strategy(
    events: list,
    ohlcv_df: pd.DataFrame,
    threshold: float = SURPRISE_THRESHOLD,
    hold_minutes: int = HOLD_MINUTES,
    pip_value: float = 0.0001,
) -> list[Trade]:
    trades: list[Trade] = []

    for event in events:
        surprise = compute_surprise(event)
        if surprise is None or abs(surprise) < threshold:
            continue

        direction = signal_direction(surprise, event.currency, SYMBOL)
        if direction is None:
            continue

        entry_time = event.release_time + timedelta(seconds=ENTRY_DELAY_SECONDS)
        exit_time = entry_time + timedelta(minutes=hold_minutes)

        entry_price = get_price_at_time(ohlcv_df, entry_time)
        exit_price = get_price_at_time(ohlcv_df, exit_time)

        if entry_price is None or exit_price is None:
            continue

        raw_pnl = (exit_price - entry_price) / pip_value
        pnl_pips = raw_pnl if direction == "long" else -raw_pnl

        trades.append(
            Trade(
                event_title=event.title,
                release_time=event.release_time,
                direction=direction,
                entry_time=entry_time,
                exit_time=exit_time,
                surprise=surprise,
                entry_price=entry_price,
                exit_price=exit_price,
                pnl_pips=pnl_pips,
            )
        )

    return trades


# %% [markdown]
# ## Load data and run

# %%
client = QuantGistClient(api_key=os.environ["QUANTGIST_API_KEY"])

FROM = datetime(2023, 1, 1, tzinfo=timezone.utc)
TO = datetime(2024, 1, 1, tzinfo=timezone.utc)

events = client.get_events(
    from_time=FROM,
    to_time=TO,
    country=EVENT_COUNTRY,
    impact=IMPACT_FILTER,
)
print(f"Loaded {len(events)} events. Events with surprise data: "
      f"{sum(1 for e in events if compute_surprise(e) is not None)}")

# ── Replace with real OHLCV data from your broker ────────────────────────────
# ohlcv_df = load_ohlcv(SYMBOL, "M1", FROM, TO)  # minute bars work best
# For demonstration, synthetic 1-min data:
import random
rng = random.Random(42)
price = 1.1000
idx = pd.date_range(FROM, TO, freq="1min", tz="UTC")
closes = []
for _ in idx:
    price += rng.gauss(0, 0.00005)
    closes.append(price)
ohlcv_df = pd.DataFrame({"close": closes}, index=idx)
# ─────────────────────────────────────────────────────────────────────────────

trades = run_strategy(events, ohlcv_df)
print(f"\nTrades triggered: {len(trades)}")

# %% [markdown]
# ## Results

# %%
if not trades:
    print("No trades triggered — try lowering SURPRISE_THRESHOLD")
else:
    df = pd.DataFrame([
        {
            "event": t.event_title,
            "release_time": t.release_time.strftime("%Y-%m-%d %H:%M"),
            "surprise": f"{t.surprise:+.3f}",
            "direction": t.direction,
            "pnl_pips": round(t.pnl_pips, 1),
        }
        for t in trades
    ])
    print(df.to_string(index=False))

    total_pnl = sum(t.pnl_pips for t in trades)
    win_rate = 100 * sum(1 for t in trades if t.pnl_pips > 0) / len(trades)

    print(f"\nTotal P&L:  {total_pnl:+.1f} pips")
    print(f"Win rate:   {win_rate:.0f}%")
    print(f"Avg trade:  {total_pnl/len(trades):+.1f} pips")

# %%
if trades:
    equity = [sum(t.pnl_pips for t in trades[:i+1]) for i in range(len(trades))]
    plt.figure(figsize=(12, 4))
    plt.plot(equity, marker="o", markersize=4, color="#2563eb")
    plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
    plt.title(f"Surprise Momentum — {SYMBOL} on {EVENT_COUNTRY} events (threshold={SURPRISE_THRESHOLD})")
    plt.xlabel("Trade #")
    plt.ylabel("Cumulative P&L (pips)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

# %% [markdown]
# ## Parameter sensitivity
#
# Run this cell to sweep SURPRISE_THRESHOLD and HOLD_MINUTES.

# %%
results = []
for threshold in [0.05, 0.1, 0.15, 0.2, 0.3]:
    for hold in [15, 30, 60, 120]:
        ts = run_strategy(events, ohlcv_df, threshold=threshold, hold_minutes=hold)
        if ts:
            results.append({
                "threshold": threshold,
                "hold_min": hold,
                "trades": len(ts),
                "total_pnl": round(sum(t.pnl_pips for t in ts), 1),
                "win_pct": round(100 * sum(1 for t in ts if t.pnl_pips > 0) / len(ts), 0),
            })

sens_df = pd.DataFrame(results)
print(sens_df.to_string(index=False))
