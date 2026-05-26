#!/usr/bin/env python3
"""
NFP vs Gold: How Non-Farm Payrolls Moves XAUUSD
================================================

Educational purpose:
    Non-Farm Payrolls (NFP) is the most market-moving US macro release.
    It measures the change in employed persons in the US (excluding farm workers).
    A stronger-than-expected NFP reading typically strengthens the USD, which
    tends to put downward pressure on XAUUSD (gold priced in USD).

    This script fetches NFP event history from QuantGist, computes the
    "surprise" (actual minus forecast), and shows the distribution of
    surprises over time.

    To pair with price data:
        Export the output CSV and merge on release_time with your OHLCV
        data. Always use release_time as the cutoff — never use `actual`
        before that timestamp in a backtest (lookahead bias).

Install:
    pip install quantgist-py

Run:
    export QUANTGIST_API_KEY="qg_live_..."
    python examples/nfp_gold_analysis.py
"""

# %% [markdown]
# # NFP vs Gold: How Non-Farm Payrolls Moves XAUUSD
#
# Non-Farm Payrolls (NFP) is released on the first Friday of each month at
# 08:30 ET (13:30 UTC). It is widely considered the single most market-moving
# US macro event, capable of moving XAUUSD by 1-3% within minutes.
#
# **Theory:**
# - NFP surprise > 0 (more jobs than expected) → USD strengthens → XAUUSD falls
# - NFP surprise < 0 (fewer jobs than expected) → USD weakens → XAUUSD rises
#
# **Point-in-time note:**
# The `actual` value only becomes known at `release_time`. Any backtest that
# uses `actual` before `release_time` has lookahead bias.

# %% [markdown]
# ## Step 1: Fetch NFP Events from QuantGist

# %%
import os
import sys
from datetime import datetime, timezone

# --- API key from environment — never hardcode secrets ---
api_key = os.getenv("QUANTGIST_API_KEY")
if not api_key:
    print("ERROR: QUANTGIST_API_KEY environment variable is not set.")
    print("Get a free API key at https://quantgist.com/signup")
    sys.exit(1)

from quantgist import QuantGistClient, AuthenticationError, RateLimitError, PlanUpgradeRequired


def fetch_nfp_events(client: QuantGistClient) -> list:
    """
    Fetch all available US NFP (Non-Farm Payrolls) events.

    We search for 'nonfarm' in the title, filtering to US country.
    The API returns events sorted by release_time descending by default.
    We paginate to collect all released events (actual is not None).
    """
    all_events = []
    page = 1
    per_page = 50

    print("Fetching NFP events from QuantGist API...")

    # Paginate through history — free tier returns 30 days; Starter+ returns full history
    while True:
        try:
            response = client.get_events(
                country="us",
                impact="high",
                limit=per_page,
            )
        except PlanUpgradeRequired:
            print("Note: Full historical data requires Starter plan or above.")
            print("      Free tier is limited to 30 days. Showing available data.")
            break
        except RateLimitError:
            print("Rate limit hit — consider upgrading your plan for higher limits.")
            break

        # Filter to NFP events only (title contains "nonfarm" or "non-farm")
        nfp_batch = [
            e for e in response.data
            if "nonfarm" in e.title.lower() or "non-farm" in e.title.lower()
            or "payroll" in e.title.lower()
        ]
        # Only include released events (actual value is known)
        released = [e for e in nfp_batch if e.actual is not None]
        all_events.extend(released)

        # Stop if we received fewer events than requested (last page)
        if len(response.data) < per_page:
            break

        # Basic pagination guard — avoid infinite loops
        if page >= 20:
            break
        page += 1

    print(f"Found {len(all_events)} released NFP events.")
    return all_events


# %% [markdown]
# ## Step 2: Compute Surprise Scores
#
# Surprise = actual - forecast
# A positive surprise means more jobs were created than economists expected.
# This is generally bullish for USD and bearish for gold.

# %%
def compute_surprises(events: list) -> list[dict]:
    """
    Compute surprise = actual - forecast for each NFP event.

    POINT-IN-TIME WARNING: `actual` is only valid AFTER `release_time`.
    In a backtest, only use this value after the event's release_time has passed.
    """
    results = []
    for e in events:
        if e.forecast is None or e.actual is None:
            # Cannot compute surprise without both values
            continue

        # Surprise in thousands of jobs (NFP is reported in thousands)
        surprise = e.actual - e.forecast

        # The surprise_score field (if populated by API) normalises by recent volatility
        # Here we use the raw surprise for transparency
        results.append({
            "date": e.release_time.strftime("%Y-%m-%d"),
            "release_time_utc": e.release_time.isoformat(),  # POINT-IN-TIME cutoff
            "title": e.title,
            "forecast_k": e.forecast,
            "actual_k": e.actual,
            "surprise_k": round(surprise, 1),   # thousands of jobs
            "usd_bias": "bullish" if surprise > 0 else ("bearish" if surprise < 0 else "neutral"),
            "xauusd_bias": "bearish" if surprise > 0 else ("bullish" if surprise < 0 else "neutral"),
            "api_surprise_score": e.surprise_score,  # normalised score from API (may be None)
        })

    # Sort chronologically
    results.sort(key=lambda x: x["release_time_utc"])
    return results


# %% [markdown]
# ## Step 3: Summary Statistics

# %%
def print_summary_stats(surprises: list[dict]) -> None:
    """Print descriptive statistics for the NFP surprise distribution."""
    if not surprises:
        print("No data to summarise.")
        return

    values = [r["surprise_k"] for r in surprises]
    n = len(values)
    mean = sum(values) / n
    sorted_vals = sorted(values)
    median = sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
    min_v = min(values)
    max_v = max(values)
    # Standard deviation
    variance = sum((x - mean) ** 2 for x in values) / n
    std = variance ** 0.5

    positive = sum(1 for v in values if v > 0)
    negative = sum(1 for v in values if v < 0)

    print("\n" + "=" * 60)
    print("NFP SURPRISE DISTRIBUTION (thousands of jobs)")
    print("=" * 60)
    print(f"  Observations : {n}")
    print(f"  Mean         : {mean:+.1f}k")
    print(f"  Median       : {median:+.1f}k")
    print(f"  Std Dev      : {std:.1f}k")
    print(f"  Min          : {min_v:+.1f}k  ({sorted_vals[0]})")
    print(f"  Max          : {max_v:+.1f}k")
    print(f"  Positive (USD bullish / gold bearish) : {positive} ({positive/n*100:.0f}%)")
    print(f"  Negative (USD bearish / gold bullish) : {negative} ({negative/n*100:.0f}%)")
    print("=" * 60)


# %% [markdown]
# ## Step 4: Biggest Upside and Downside Surprises

# %%
def print_extremes(surprises: list[dict], top_n: int = 5) -> None:
    """Show the biggest upside and downside surprises."""
    sorted_by_surprise = sorted(surprises, key=lambda x: x["surprise_k"])

    print(f"\nTop {top_n} DOWNSIDE surprises (fewer jobs than expected → USD weak → gold bullish):")
    print(f"  {'Date':<12} {'Forecast':>10} {'Actual':>10} {'Surprise':>10}")
    print("  " + "-" * 46)
    for r in sorted_by_surprise[:top_n]:
        print(f"  {r['date']:<12} {r['forecast_k']:>9.0f}k {r['actual_k']:>9.0f}k {r['surprise_k']:>+9.1f}k")

    print(f"\nTop {top_n} UPSIDE surprises (more jobs than expected → USD strong → gold bearish):")
    print(f"  {'Date':<12} {'Forecast':>10} {'Actual':>10} {'Surprise':>10}")
    print("  " + "-" * 46)
    for r in reversed(sorted_by_surprise[-top_n:]):
        print(f"  {r['date']:<12} {r['forecast_k']:>9.0f}k {r['actual_k']:>9.0f}k {r['surprise_k']:>+9.1f}k")


# %% [markdown]
# ## Step 5: ASCII Histogram of Surprise Distribution

# %%
def print_histogram(surprises: list[dict], bins: int = 10) -> None:
    """Simple ASCII histogram of surprise values."""
    values = [r["surprise_k"] for r in surprises]
    if not values:
        return

    min_v, max_v = min(values), max(values)
    bin_width = (max_v - min_v) / bins if max_v != min_v else 1
    counts = [0] * bins

    for v in values:
        idx = min(int((v - min_v) / bin_width), bins - 1)
        counts[idx] += 1

    max_count = max(counts)
    bar_scale = 30 / max_count if max_count > 0 else 1

    print("\nHistogram: NFP Surprise Distribution")
    print("(negative = fewer jobs than expected, positive = more jobs than expected)")
    print()
    for i, count in enumerate(counts):
        lo = min_v + i * bin_width
        hi = lo + bin_width
        bar = "#" * int(count * bar_scale)
        print(f"  [{lo:+7.0f}k, {hi:+7.0f}k) | {bar:<32} {count}")
    print()


# %% [markdown]
# ## Step 6: pandas DataFrame (optional)
#
# If pandas is installed, we show the data as a DataFrame.
# This is the format you would merge with price data for backtesting.

# %%
def show_pandas_view(surprises: list[dict]) -> None:
    """
    Display results as a pandas DataFrame if pandas is available.

    BACKTESTING USAGE:
        df['release_time_utc'] is the point-in-time cutoff.
        Only join price data AFTER this timestamp — never before.

        Example merge with OHLCV:
            price_df = pd.read_csv('xauusd_m5.csv', parse_dates=['time'])
            for _, event in nfp_df.iterrows():
                # Find the candle AFTER the NFP release
                post_release = price_df[price_df['time'] > pd.Timestamp(event['release_time_utc'])]
                first_candle = post_release.iloc[0] if len(post_release) else None
    """
    try:
        import pandas as pd
    except ImportError:
        print("\n[pandas not installed — skipping DataFrame view]")
        print("  Run: pip install pandas")
        return

    df = pd.DataFrame(surprises)
    df["release_time_utc"] = pd.to_datetime(df["release_time_utc"], utc=True)
    df = df.sort_values("release_time_utc")

    print("\n--- pandas DataFrame view ---")
    print(df[["date", "forecast_k", "actual_k", "surprise_k", "usd_bias", "xauusd_bias"]].to_string(index=False))
    print(f"\nNote: release_time_utc is the point-in-time cutoff for backtesting.")


# %% [markdown]
# ## Step 7: Export to CSV

# %%
def export_to_csv(surprises: list[dict], path: str = "nfp_surprises.csv") -> None:
    """
    Export NFP surprise data to CSV for pairing with price data.

    IMPORTANT: In your backtest, filter price data to timestamps AFTER
    `release_time_utc`. Using `actual_k` before that timestamp is lookahead bias.
    """
    import csv
    if not surprises:
        return

    fieldnames = list(surprises[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(surprises)

    print(f"\nExported {len(surprises)} NFP events to: {path}")
    print("  To pair with price data, merge on release_time_utc (the point-in-time cutoff).")


# %% [markdown]
# ## Main

# %%
def main() -> None:
    with QuantGistClient(api_key=api_key) as client:
        try:
            events = fetch_nfp_events(client)
        except AuthenticationError:
            print("ERROR: Invalid API key. Get one at https://quantgist.com/signup")
            sys.exit(1)

    if not events:
        print("No NFP events found. Check your plan tier — free accounts have 365-day history.")
        return

    surprises = compute_surprises(events)

    if not surprises:
        print("No events had both forecast and actual values — cannot compute surprises.")
        return

    print_summary_stats(surprises)
    print_extremes(surprises, top_n=5)
    print_histogram(surprises, bins=10)
    show_pandas_view(surprises)
    export_to_csv(surprises, "nfp_surprises.csv")

    print("\nNext steps:")
    print("  1. Load nfp_surprises.csv alongside your XAUUSD OHLCV data")
    print("  2. For each NFP release, look at the 30-min price move AFTER release_time_utc")
    print("  3. Compute correlation: surprise_k vs. XAUUSD % change")
    print("  4. Remember: only use actual_k AFTER release_time_utc in any backtest")


if __name__ == "__main__":
    main()
