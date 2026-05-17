"""TypedDict definitions for QuantGist API response shapes (resource API)."""

from __future__ import annotations

from typing import Any, List, Optional

from typing_extensions import TypedDict


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class PaginatedResponse(TypedDict):
    data: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


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
    actual: Optional[float]
    forecast: Optional[float]
    previous: Optional[float]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    description: Optional[str]


class EventsResponseDict(TypedDict):
    data: List[EventDict]
    total: int
    page: int
    page_size: int
    pages: int


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------


class CalendarResponseDict(TypedDict):
    date: str
    events: List[EventDict]


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
    symbol: Optional[str]
    impact: Optional[str]
    summary: Optional[str]


class NewsResponseDict(TypedDict):
    data: List[NewsItemDict]
    total: int
    page: int
    page_size: int
    pages: int


# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------


class SymbolDict(TypedDict, total=False):
    symbol: str
    name: str
    currency: str
    exchange: Optional[str]
    asset_type: Optional[str]


class SymbolsResponseDict(TypedDict):
    data: List[SymbolDict]
    total: int
    page: int
    page_size: int
    pages: int


# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------


class UsageSummaryDict(TypedDict, total=False):
    plan: str
    requests_today: int
    requests_this_month: int
    daily_limit: Optional[int]
    monthly_limit: Optional[int]
    reset_at: Optional[str]


class UsageHistoryItemDict(TypedDict, total=False):
    date: str
    requests: int


class UsageEndpointItemDict(TypedDict, total=False):
    endpoint: str
    requests: int
    last_called_at: Optional[str]
