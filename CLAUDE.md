# CLAUDE.md — quantgist-python

**Layer:** L1 Open Source · **Tentpole:** T2 SDK  
**PyPI package name:** `quantgist`  
**Target:** Python 3.10+

---

## Purpose

The official Python SDK for the QuantGist API. Primary organic discovery engine via GitHub and PyPI. This is the SDK developers integrate first — it creates the dependency that leads to paid upgrades.

## Aha moment
> "I fetched NFP data and filtered it to XAUUSD in 5 lines of Python."

---

## Commands

```bash
uv sync                   # install deps
uv run pytest             # run tests
uv run ruff check src/    # lint
uv run ruff format src/   # format
uv run python examples/quickstart.py  # smoke test
```

## Package structure

```
quantgist-python/
├── src/
│   └── quantgist/
│       ├── __init__.py       # exports: QuantGistClient, Event, ...
│       ├── client.py         # main sync client
│       ├── async_client.py   # async variant (httpx)
│       ├── models.py         # pydantic models matching API schema
│       ├── exceptions.py     # QuantGistError hierarchy
│       └── _version.py       # single source of truth for version
├── examples/
│   ├── quickstart.py
│   ├── nfp_gold.ipynb
│   ├── cpi_eurusd.ipynb
│   └── rate_decision_fx.ipynb
├── tests/
│   ├── test_client.py
│   └── test_models.py
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

---

## API conventions

- Base URL: configurable, defaults to `https://api.quantgist.com/v1`
- Auth: `X-API-Key` header
- Client reads key from `QUANTGIST_API_KEY` env var, or passed explicitly
- All methods return typed pydantic models — never raw dicts
- Sync client uses `httpx.Client`; async client uses `httpx.AsyncClient`

## Build rules

- No circular imports — `models.py` has zero imports from `client.py`
- `__init__.py` exports only the public API
- Keep `httpx` and `pydantic` as the only required dependencies
- Optional extras: `quantgist[pandas]`, `quantgist[async]`
- Tests use `respx` to mock httpx — never make real network calls in tests

---

## Publishing

```bash
uv build
uv publish   # requires PYPI_TOKEN env var
```
