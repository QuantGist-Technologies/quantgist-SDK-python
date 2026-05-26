"""
QuantGist Python SDK — 30-second quickstart
============================================

Install:
    pip install quantgist-py
    # or
    uv add quantgist-py

Set your API key (get one free at https://quantgist.com):
    export QUANTGIST_API_KEY="qg_live_..."

Then run:
    python examples/quickstart.py
"""

import os
import sys

# Require the API key from the environment so we never hardcode secrets.
api_key = os.environ.get("QUANTGIST_API_KEY")
if not api_key:
    print(
        "ERROR: QUANTGIST_API_KEY environment variable is not set.\n"
        "\n"
        "Get a free API key at https://quantgist.com, then run:\n"
        "  export QUANTGIST_API_KEY='qg_live_...'\n"
        "  python examples/quickstart.py"
    )
    sys.exit(1)

from quantgist import QuantGistClient  # noqa: E402  (import after env check)

client = QuantGistClient(api_key=api_key)

# Fetch the 10 most recent high-impact macro events
events = client.get_events(impact="high", limit=10)

print(f"Fetched {len(events.data)} high-impact events "
      f"(page {events.meta.page} of {(events.meta.total + events.meta.per_page - 1) // events.meta.per_page})\n")

for e in events.data:
    actual_str = f"actual={e.actual}" if e.actual is not None else "pending"
    print(f"{e.release_time.strftime('%Y-%m-%d %H:%M UTC')} | {e.country:2s} | {e.impact:6s} | {e.title} | {actual_str}")
