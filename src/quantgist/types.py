"""TypedDict definitions for QuantGist API response shapes (resource API)."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict

# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class PaginatedResponse(TypedDict):
    data: list[Any]
    total: int
    page: int
    per_page: int
    total_pages: int


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


class EventDict(TypedDict, total=False):
    id: str
    symbol: str
    currency: str
    event_type: str
    source: str
    impact: str
    release_time: str
    title: str
    actual: float | None
    forecast: float | None
    previous: float | None
    sentiment: str | None
    sentiment_score: float | None
    description: str | None


class EventsResponseDict(TypedDict):
    data: list[EventDict]
    total: int
    page: int
    per_page: int
    total_pages: int


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------


class CalendarResponseDict(TypedDict):
    date: str
    events: list[EventDict]


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------


class NewsItemDict(TypedDict, total=False):
    id: str
    title: str
    source: str
    url: str
    published_at: str
    currency: str
    symbol: str | None
    impact: str | None
    summary: str | None


class NewsResponseDict(TypedDict):
    data: list[NewsItemDict]
    total: int
    page: int
    per_page: int
    total_pages: int


# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------


class SymbolDict(TypedDict, total=False):
    symbol: str
    name: str
    currency: str
    exchange: str | None
    asset_type: str | None


class SymbolsResponseDict(TypedDict):
    data: list[SymbolDict]
    total: int
    page: int
    per_page: int
    total_pages: int


# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------


class UsageSummaryDict(TypedDict, total=False):
    plan: str
    requests_today: int
    requests_this_month: int
    daily_limit: int | None
    monthly_limit: int | None
    reset_at: str | None


class UsageHistoryItemDict(TypedDict, total=False):
    date: str
    requests: int


class UsageEndpointItemDict(TypedDict, total=False):
    endpoint: str
    requests: int
    last_called_at: str | None
