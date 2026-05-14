from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Event(BaseModel):
    id: str
    title: str
    country: str
    currency: str
    release_time: datetime
    impact: Literal["low", "medium", "high"]
    forecast: float | None = None
    previous: float | None = None
    actual: float | None = None
    surprise_score: float | None = None
    affected_symbols: list[str] = Field(default_factory=list)
    source: str


class EventsResponse(BaseModel):
    data: list[Event]
    meta: ResponseMeta


class ResponseMeta(BaseModel):
    total: int
    page: int
    per_page: int
    rate_limit_remaining: int | None = None


# ---------------------------------------------------------------------------
# Earnings models
# ---------------------------------------------------------------------------


class EarningsEvent(BaseModel):
    """A single earnings report event."""

    id: str
    ticker: str
    company_name: str
    report_date: date
    fiscal_quarter: str | None = None  # e.g. "Q1 2025"
    eps_estimate: float | None = None
    eps_actual: float | None = None
    revenue_estimate: float | None = None
    revenue_actual: float | None = None
    surprise_pct: float | None = None  # EPS % surprise
    beat_miss: Literal["beat", "miss", "in-line"] | None = None
    market_cap: float | None = None
    sector: str | None = None
    report_time: Literal["before_open", "after_close", "during_market"] | None = None
    sec_filing_url: str | None = None
    sec_accession_number: str | None = None
    sec_filed_at: date | None = None
    field_sources: dict[str, str] = Field(default_factory=dict)


class EarningsCursorMeta(BaseModel):
    """Pagination metadata for cursor-based earnings endpoints."""

    next_cursor: str | None = None
    has_more: bool = False
    total: int | None = None
    rate_limit_remaining: int | None = None


class EarningsResponse(BaseModel):
    data: list[EarningsEvent]
    meta: EarningsCursorMeta


class EarningsSummary(BaseModel):
    """Beat/miss/in-line counts for a single ticker."""

    ticker: str
    company_name: str | None = None
    beat: int
    miss: int
    in_line: int
    total: int
    beat_rate: float | None = None  # percentage


class EarningsSurprise(BaseModel):
    """Largest EPS surprises across the market."""

    ticker: str
    company_name: str | None = None
    report_date: date
    surprise_pct: float
    beat_miss: Literal["beat", "miss", "in-line"] | None = None
    sector: str | None = None


class EarningsMover(BaseModel):
    """Earnings event ranked by market impact."""

    ticker: str
    company_name: str | None = None
    report_date: date
    price_change_pct: float | None = None
    volume_ratio: float | None = None  # volume vs 30-day avg
    beat_miss: Literal["beat", "miss", "in-line"] | None = None
    market_cap: float | None = None


class EarningsWeekDay(BaseModel):
    """A single day in the week-ahead calendar."""

    date: date
    events: list[EarningsEvent]


class EarningsWeekCalendar(BaseModel):
    """Week-ahead earnings calendar grouped by day."""

    week_start: date
    week_end: date
    days: list[EarningsWeekDay]


class EarningsSeasonSummary(BaseModel):
    """Index-level aggregate for the current earnings season."""

    season_label: str | None = None  # e.g. "Q1 2025"
    as_of: date | None = None
    total_reported: int
    beat_count: int
    miss_count: int
    in_line_count: int
    beat_rate: float | None = None
    average_surprise_pct: float | None = None
    index: str | None = None  # e.g. "S&P 500"


# ---------------------------------------------------------------------------
# Markets models
# ---------------------------------------------------------------------------


class MarketQuote(BaseModel):
    """End-of-day quote for a single instrument (Stooq)."""

    symbol: str
    name: str | None = None
    close: float
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None
    change_pct: float | None = None
    as_of: date | None = None


class MarketsOverviewResponse(BaseModel):
    data: list[MarketQuote]


# ---------------------------------------------------------------------------
# Changelog model
# ---------------------------------------------------------------------------


class ChangelogEntry(BaseModel):
    """A single API changelog entry (no auth required)."""

    version: str
    date: date
    summary: str
    breaking: bool = False
    changes: list[str] = Field(default_factory=list)


class ChangelogResponse(BaseModel):
    data: list[ChangelogEntry]
