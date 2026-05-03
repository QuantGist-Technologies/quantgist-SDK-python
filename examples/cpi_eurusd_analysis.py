# %% [markdown]
# # CPI Surprise vs EUR/USD Reaction
#
# This notebook fetches historical CPI releases, computes the surprise
# (actual − forecast), and shows the distribution of EUR/USD moves
# in the 30 minutes following each release.
#
# **Requirements**: `quantgist`, `pandas`, `matplotlib`
# %% [markdown]
# ## Setup

# %%
import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import matplotlib.pyplot as plt
from quantgist import QuantGistClient

client = QuantGistClient(api_key=os.environ["QUANTGIST_API_KEY"])

# %% [markdown]
# ## Fetch CPI events (last 24 months)

# %%
now = datetime.now(timezone.utc)
two_years_ago = now - timedelta(days=730)

events = client.get_events(
    from_time=two_years_ago,
    to_time=now,
    country="US",
    impact="high",
)

cpi_events = [
    e for e in events
    if "CPI" in e.title.upper() and e.actual is not None and e.forecast is not None
]

print(f"Found {len(cpi_events)} US CPI releases with actual + forecast data")

# %%
df = pd.DataFrame([
    {
        "release_time": e.release_time,
        "title": e.title,
        "actual": e.actual,
        "forecast": e.forecast,
        "previous": e.previous,
        "surprise": e.actual - e.forecast,
    }
    for e in cpi_events
]).sort_values("release_time")

df.head(10)

# %% [markdown]
# ## Surprise distribution

# %%
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(df["surprise"], bins=15, color="#2563eb", edgecolor="white")
axes[0].axvline(0, color="red", linestyle="--", linewidth=1.5, label="No surprise")
axes[0].set_title("CPI Surprise Distribution (US, last 2 years)")
axes[0].set_xlabel("Actual − Forecast (%)")
axes[0].set_ylabel("Count")
axes[0].legend()

# Surprise vs implied EUR/USD direction (positive CPI → USD strength → EUR/USD ↓)
hot = df[df["surprise"] > 0]
cold = df[df["surprise"] < 0]
axes[1].bar(
    ["Hot (surprise > 0)\nEUR/USD ↓ expected", "Cold (surprise < 0)\nEUR/USD ↑ expected"],
    [len(hot), len(cold)],
    color=["#dc2626", "#16a34a"],
)
axes[1].set_title("Hot vs Cold CPI Prints")
axes[1].set_ylabel("Count")

plt.tight_layout()
plt.show()

# %% [markdown]
# ## Surprise magnitude over time

# %%
plt.figure(figsize=(14, 4))
plt.bar(
    df["release_time"],
    df["surprise"],
    color=df["surprise"].apply(lambda x: "#dc2626" if x > 0 else "#16a34a"),
    width=20,
)
plt.axhline(0, color="black", linewidth=0.8)
plt.title("US CPI Surprise Over Time")
plt.xlabel("Release Date")
plt.ylabel("Actual − Forecast (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Summary statistics

# %%
print("CPI Surprise Summary")
print("=" * 40)
print(df["surprise"].describe().to_string())
print()
print(f"Hot prints (surprise > 0): {len(hot)} ({100*len(hot)/len(df):.0f}%)")
print(f"Cold prints (surprise < 0): {len(cold)} ({100*len(cold)/len(df):.0f}%)")
print(f"Inline (surprise = 0): {len(df[df['surprise'] == 0])}")
print()
print("Largest hot surprise:", df.loc[df['surprise'].idxmax(), ['release_time', 'title', 'surprise']].to_dict())
print("Largest cold surprise:", df.loc[df['surprise'].idxmin(), ['release_time', 'title', 'surprise']].to_dict())

# %% [markdown]
# ## Next steps
#
# To extend this analysis:
# 1. **Add OHLCV data** from your broker/provider for EUR/USD at the release timestamps
# 2. **Compute realized moves** — e.g. close price 30 min after vs open at release
# 3. **Compare** realized move vs surprise magnitude to build a linear model
# 4. **Backtest** a simple surprise-momentum rule: buy/sell EUR/USD based on surprise sign
#    → see `research/strategies/surprise_momentum.py` for the template
