from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    """A macro / market event row from ``GET /v1/events``.

    Most fields are optional: news-type events carry null ``country``/``currency``
    and no ``source``, and the API adds fields over time. The canonical symbol list
    is ``symbols`` (``affected_symbols`` remains as a read alias).
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    country: str | None = None
    currency: str | None = None
    release_time: datetime
    impact: str
    # The API returns these as display-formatted strings ("3.20%", "8K", "765.5B"),
    # occasionally bare numbers — accept both.
    forecast: float | str | None = None
    previous: float | str | None = None
    actual: float | str | None = None
    # Newer API fields (all optional).
    source_event_id: str | None = None
    event_type: str | None = None
    published_at: datetime | None = None
    title_normalized: str | None = None
    summary: str | None = None
    symbols: list[str] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)
    asset_classes: list[str] = Field(default_factory=list)
    sentiment_score: float | None = None
    sentiment_label: str | None = None
    impact_score: float | None = None
    surprise_score: float | None = None
    source: str | None = None

    @property
    def affected_symbols(self) -> list[str]:
        """Back-compat alias — the API field is now ``symbols``."""
        return self.symbols


class ResponseMeta(BaseModel):
    total: int
    page: int
    per_page: int
    rate_limit_remaining: int | None = None


class EventsResponse(BaseModel):
    """Response from ``GET /v1/events``.

    Pagination fields are top-level (the API no longer nests them under ``meta``).
    ``rate_limit_remaining`` is populated by the client from the response headers.
    """

    data: list[Event]
    total: int | None = None
    page: int | None = None
    per_page: int | None = None
    has_more: bool | None = None
    total_pages: int | None = None
    backtest_safe: bool | None = None
    rate_limit_remaining: int | None = None

    @property
    def meta(self) -> ResponseMeta:
        """Back-compat: older callers read ``response.meta.rate_limit_remaining``."""
        return ResponseMeta(
            total=self.total or 0,
            page=self.page or 1,
            per_page=self.per_page or len(self.data),
            rate_limit_remaining=self.rate_limit_remaining,
        )


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
