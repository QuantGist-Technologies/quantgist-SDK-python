# Changelog

All notable changes to `quantgist` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2025-05-03

Initial public release of the official QuantGist Python SDK.

### Added

- `QuantGistClient` — synchronous client backed by `httpx.Client`
  - `get_events(from_date, to_date, country, currency, impact, symbol, limit)` — fetch paginated macro events with optional filters
  - `get_event(event_id)` — fetch a single event by ID
  - Context-manager support (`with QuantGistClient(...) as client`)
  - `close()` for explicit connection cleanup
- `AsyncQuantGistClient` — async-native client backed by `httpx.AsyncClient`
  - Same methods as sync client, all `async`; additionally supports `page` parameter on `get_events`
  - Async context-manager support (`async with AsyncQuantGistClient(...) as client`)
- Pydantic v2 data models: `Event`, `EventsResponse`, `ResponseMeta`
- Typed exception hierarchy: `QuantGistError`, `AuthenticationError`, `RateLimitError`, `NotFoundError`, `PlanUpgradeRequired`
- Automatic API key resolution from `QUANTGIST_API_KEY` environment variable
- `User-Agent` header set to `quantgist-python/<version>` on every request
- PEP 561 `py.typed` marker for downstream type checkers
- Optional extras: `quantgist[async]` (async transport), `quantgist[pandas]`
- Full type annotations; passes `pyright` in standard mode

[0.1.0]: https://github.com/quantgist/quantgist-python/releases/tag/v0.1.0
