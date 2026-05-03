# %% [markdown]
# # News Avoidance Strategy Template
#
# A framework for backtesting "pause trading before high-impact events"
# rules. Simulates a simple trend-following EA that goes flat N minutes
# before each release and resumes M minutes after.
#
# Plug in your own entry/exit logic in the `_strategy_signal()` function.

# %%
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Literal

import pandas as pd
import matplotlib.pyplot as plt
from quantgist import QuantGistClient

# %%
# ─── Parameters ──────────────────────────────────────────────────────────────
SYMBOL = "EURUSD"
PAUSE_MINUTES_BEFORE = 10
PAUSE_MINUTES_AFTER = 5
IMPACT_FILTER: Literal["high", "medium", "low"] = "high"
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Bar:
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass
class BacktestResult:
    total_bars: int
    paused_bars: int
    trades_taken: int
    trades_skipped: int
    pause_pct: float
    equity_curve: list[float] = field(default_factory=list)


def load_events(client: QuantGistClient, from_time: datetime, to_time: datetime) -> list:
    """Fetch all high-impact events for the backtest window."""
    return client.get_events(
        from_time=from_time,
        to_time=to_time,
        impact=IMPACT_FILTER,
        symbol=SYMBOL,
    )


def build_pause_windows(events: list, before: int, after: int) -> list[tuple[datetime, datetime]]:
    """Return (start, end) UTC windows where trading is paused."""
    windows = []
    for ev in events:
        if ev.release_time is None:
            continue
        start = ev.release_time - timedelta(minutes=before)
        end = ev.release_time + timedelta(minutes=after)
        windows.append((start, end))
    return windows


def is_in_pause_window(bar_time: datetime, windows: list[tuple[datetime, datetime]]) -> bool:
    for start, end in windows:
        if start <= bar_time <= end:
            return True
    return False


def _strategy_signal(bar: Bar, prev_bar: Bar | None) -> Literal["buy", "sell", "flat"]:
    """
    Plug your own logic here.
    This default: simple momentum — buy if close > prev close, sell otherwise.
    """
    if prev_bar is None:
        return "flat"
    if bar.close > prev_bar.close:
        return "buy"
    if bar.close < prev_bar.close:
        return "sell"
    return "flat"


def run_backtest(
    bars: list[Bar],
    events: list,
    pause_before: int = PAUSE_MINUTES_BEFORE,
    pause_after: int = PAUSE_MINUTES_AFTER,
    pip_value: float = 0.0001,
    lot_pips: float = 10.0,
) -> BacktestResult:
    windows = build_pause_windows(events, pause_before, pause_after)
    equity = 0.0
    equity_curve = []
    trades_taken = trades_skipped = paused = 0

    prev_bar = None
    for bar in bars:
        paused_this_bar = is_in_pause_window(bar.time, windows)
        if paused_this_bar:
            paused += 1

        signal = _strategy_signal(bar, prev_bar)

        if signal != "flat":
            if paused_this_bar:
                trades_skipped += 1
            else:
                trades_taken += 1
                pnl_pips = (
                    (bar.close - bar.open) / pip_value
                    if signal == "buy"
                    else (bar.open - bar.close) / pip_value
                )
                equity += pnl_pips * lot_pips

        equity_curve.append(equity)
        prev_bar = bar

    return BacktestResult(
        total_bars=len(bars),
        paused_bars=paused,
        trades_taken=trades_taken,
        trades_skipped=trades_skipped,
        pause_pct=100.0 * paused / max(len(bars), 1),
        equity_curve=equity_curve,
    )


# %% [markdown]
# ## Run the backtest

# %%
client = QuantGistClient(api_key=os.environ["QUANTGIST_API_KEY"])

# Define your backtest window
FROM = datetime(2023, 1, 1, tzinfo=timezone.utc)
TO = datetime(2024, 1, 1, tzinfo=timezone.utc)

events = load_events(client, FROM, TO)
print(f"Loaded {len(events)} {IMPACT_FILTER}-impact events for {SYMBOL}")

# ── Replace this with real OHLCV data from your broker ──────────────────────
# bars: list[Bar] = load_ohlcv_from_broker(SYMBOL, "H1", FROM, TO)
# For demonstration, create synthetic bars:
import random
rng = random.Random(42)
price = 1.1000
bars: list[Bar] = []
t = FROM
while t < TO:
    change = rng.gauss(0, 0.0005)
    o = price
    h = o + abs(rng.gauss(0, 0.0002))
    l = o - abs(rng.gauss(0, 0.0002))
    c = o + change
    bars.append(Bar(time=t, open=o, high=h, low=l, close=c))
    price = c
    t += timedelta(hours=1)
# ─────────────────────────────────────────────────────────────────────────────

result_with_pause = run_backtest(bars, events, pause_before=10, pause_after=5)
result_no_pause = run_backtest(bars, events, pause_before=0, pause_after=0)

# %% [markdown]
# ## Results

# %%
print("=" * 50)
print(f"News Avoidance Backtest — {SYMBOL}")
print("=" * 50)
print(f"Bars total:          {result_with_pause.total_bars:,}")
print(f"Bars paused:         {result_with_pause.paused_bars:,} ({result_with_pause.pause_pct:.1f}%)")
print(f"Trades (with pause): {result_with_pause.trades_taken:,}")
print(f"Trades skipped:      {result_with_pause.trades_skipped:,}")
print(f"Trades (no pause):   {result_no_pause.trades_taken:,}")

# %%
plt.figure(figsize=(14, 5))
plt.plot(result_with_pause.equity_curve, label="With news pause", color="#2563eb")
plt.plot(result_no_pause.equity_curve, label="No pause (baseline)", color="#94a3b8", alpha=0.7)
plt.title(f"Equity Curve — {SYMBOL} News Avoidance ({pause_before}min before / {pause_after}min after)")
plt.xlabel("Bar #")
plt.ylabel("Equity (pips)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

PAUSE_MINUTES_BEFORE = PAUSE_MINUTES_BEFORE  # keep reference for title
pause_before = PAUSE_MINUTES_BEFORE
