# %% [markdown]
# # Central Bank Rate Decisions — Surprise & Market Reaction
#
# Fetches historical rate decisions from the QuantGist API, identifies
# surprise hikes/cuts (vs consensus), and visualises the pattern.
#
# Works for: Fed, ECB, BoE, BoJ, RBA, SNB, BoC, RBNZ
#
# **Requirements**: `quantgist`, `pandas`, `matplotlib`

# %%
import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import matplotlib.pyplot as plt
from quantgist import QuantGistClient

client = QuantGistClient(api_key=os.environ["QUANTGIST_API_KEY"])

# %% [markdown]
# ## Configure which central bank to analyse

# %%
BANK_CONFIG = {
    "Fed": {"country": "US", "keywords": ["Fed", "FOMC", "Interest Rate"]},
    "ECB": {"country": "EU", "keywords": ["ECB", "Interest Rate"]},
    "BoE": {"country": "GB", "keywords": ["BoE", "Bank Rate", "Interest Rate"]},
    "BoJ": {"country": "JP", "keywords": ["BoJ", "Interest Rate"]},
    "RBA": {"country": "AU", "keywords": ["RBA", "Cash Rate"]},
}

BANK = "Fed"  # ← change this
cfg = BANK_CONFIG[BANK]

# %%
now = datetime.now(timezone.utc)
three_years_ago = now - timedelta(days=1095)

events = client.get_events(
    from_time=three_years_ago,
    to_time=now,
    country=cfg["country"],
    impact="high",
)

rate_events = [
    e for e in events
    if any(kw.lower() in e.title.lower() for kw in cfg["keywords"])
    and e.actual is not None
    and e.forecast is not None
]

print(f"Found {len(rate_events)} {BANK} rate decisions with actual + forecast data")

# %%
df = pd.DataFrame([
    {
        "release_time": e.release_time,
        "title": e.title,
        "actual": e.actual,
        "forecast": e.forecast,
        "previous": e.previous,
        "surprise_bps": round((e.actual - e.forecast) * 100, 1),
        "change_bps": round((e.actual - (e.previous or e.actual)) * 100, 1),
    }
    for e in rate_events
]).sort_values("release_time")

df.head(10)

# %% [markdown]
# ## Rate path

# %%
plt.figure(figsize=(14, 5))
plt.step(df["release_time"], df["actual"], where="post", color="#2563eb", linewidth=2, label="Policy Rate")
plt.scatter(df["release_time"], df["actual"], color="#2563eb", s=40, zorder=5)

# Highlight surprises
surprises = df[df["surprise_bps"] != 0]
plt.scatter(
    surprises["release_time"],
    surprises["actual"],
    color="#dc2626",
    s=100,
    zorder=6,
    label=f"Surprise ({len(surprises)} events)",
    marker="*",
)

plt.title(f"{BANK} Policy Rate Path (last 3 years)")
plt.ylabel("Rate (%)")
plt.xlabel("Date")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Surprise analysis

# %%
print(f"\n{BANK} Rate Decision Surprises")
print("=" * 50)

if surprises.empty:
    print("No deviations from consensus in this period — all decisions were in-line.")
else:
    for _, row in surprises.iterrows():
        direction = "hawkish" if row["surprise_bps"] > 0 else "dovish"
        print(
            f"  {row['release_time'].strftime('%Y-%m-%d')} | "
            f"{row['surprise_bps']:+.0f}bps surprise ({direction}) | "
            f"Rate: {row['actual']:.2f}%"
        )

# %%
print(f"\nAll {BANK} decisions summary")
print(df[["release_time", "previous", "actual", "change_bps", "forecast", "surprise_bps"]]
    .to_string(index=False))

# %% [markdown]
# ## Decision breakdown

# %%
hikes = df[df["change_bps"] > 0]
cuts = df[df["change_bps"] < 0]
holds = df[df["change_bps"] == 0]

labels = ["Hike", "Cut", "Hold"]
sizes = [len(hikes), len(cuts), len(holds)]
colors = ["#dc2626", "#16a34a", "#94a3b8"]

fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    sizes, labels=labels, colors=colors,
    autopct="%1.0f%%", startangle=90,
)
ax.set_title(f"{BANK} Decisions — Last 3 Years")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Key takeaways
#
# - Rate decisions with **surprises** (actual ≠ forecast) are high-volatility events
# - Even a **hold** can be a surprise if the market priced in a cut
# - For trading strategies, focus on the **surprise magnitude** not just the direction
# - See `research/strategies/news_avoidance.py` for a framework to pause trading around these releases
