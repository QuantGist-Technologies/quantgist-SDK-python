"""Tests for Pydantic models in quantgist.models."""
from __future__ import annotations

from datetime import datetime

import pytest

from quantgist.models import Event, EventsResponse, ResponseMeta

REALISTIC_EVENT_JSON = {
    "id": "evt_002",
    "title": "CPI m/m",
    "country": "US",
    "currency": "USD",
    "release_time": "2024-07-11T12:30:00Z",
    "impact": "high",
    "forecast": 0.1,
    "previous": 0.0,
    "actual": 0.1,
    "surprise_score": 0.0,
    "symbols": ["EURUSD", "XAUUSD", "USDJPY"],
    "source": "bls.gov",
}


# ---------------------------------------------------------------------------
# Event model
# ---------------------------------------------------------------------------


def test_event_parses_realistic_json() -> None:
    event = Event.model_validate(REALISTIC_EVENT_JSON)

    assert event.id == "evt_002"
    assert event.title == "CPI m/m"
    assert event.country == "US"
    assert event.currency == "USD"
    assert event.impact == "high"
    assert event.source == "bls.gov"
    assert event.affected_symbols == ["EURUSD", "XAUUSD", "USDJPY"]


def test_event_release_time_is_datetime() -> None:
    event = Event.model_validate(REALISTIC_EVENT_JSON)

    assert isinstance(event.release_time, datetime)
    # Pydantic parses ISO-8601 with Z suffix as UTC-aware datetime
    assert event.release_time.year == 2024
    assert event.release_time.month == 7
    assert event.release_time.day == 11
    assert event.release_time.hour == 12
    assert event.release_time.minute == 30


def test_event_optional_fields_accept_none() -> None:
    minimal = {
        "id": "evt_003",
        "title": "Trade Balance",
        "country": "DE",
        "currency": "EUR",
        "release_time": "2024-08-01T06:00:00Z",
        "impact": "medium",
        "source": "destatis.de",
    }
    event = Event.model_validate(minimal)

    assert event.forecast is None
    assert event.previous is None
    assert event.actual is None
    assert event.surprise_score is None
    assert event.affected_symbols == []


def test_event_forecast_accepts_none_explicitly() -> None:
    data = {**REALISTIC_EVENT_JSON, "forecast": None, "actual": None}
    event = Event.model_validate(data)

    assert event.forecast is None
    assert event.actual is None


def test_event_impact_literal_values() -> None:
    for level in ("low", "medium", "high"):
        data = {**REALISTIC_EVENT_JSON, "impact": level}
        event = Event.model_validate(data)
        assert event.impact == level


def test_event_surprise_score_float() -> None:
    data = {**REALISTIC_EVENT_JSON, "surprise_score": 1.23}
    event = Event.model_validate(data)
    assert event.surprise_score == pytest.approx(1.23)


# ---------------------------------------------------------------------------
# EventsResponse model
# ---------------------------------------------------------------------------


def test_events_response_parses_correctly() -> None:
    # Current API shape: pagination is top-level (no nested "meta").
    payload = {
        "data": [REALISTIC_EVENT_JSON],
        "total": 1,
        "page": 1,
        "per_page": 50,
        "has_more": False,
        "total_pages": 1,
        "backtest_safe": False,
        "rate_limit_remaining": 980,
    }
    response = EventsResponse.model_validate(payload)

    assert len(response.data) == 1
    assert isinstance(response.data[0], Event)
    assert response.total == 1
    assert response.has_more is False
    # Back-compat: the .meta property derives from the top-level fields.
    assert response.meta.total == 1
    assert response.meta.page == 1
    assert response.meta.per_page == 50
    assert response.meta.rate_limit_remaining == 980


def test_events_response_rate_limit_remaining_optional() -> None:
    payload = {"data": [], "total": 0, "page": 1, "per_page": 50}
    response = EventsResponse.model_validate(payload)
    assert response.meta.rate_limit_remaining is None


def test_event_parses_news_row_with_nulls_and_string_values() -> None:
    """Regression: news-type rows have null country/currency, no source, and
    display-formatted string forecast/previous/actual."""
    news = {
        "id": "evt_news",
        "title": "GDP (YoY) (Q1)",
        "country": None,
        "currency": None,
        "release_time": "2026-06-30T12:00:00Z",
        "impact": "high",
        "forecast": "5.90%",
        "previous": "-12K",
        "actual": None,
        "symbols": ["USDBRL"],
        "event_type": "economic_release",
    }
    event = Event.model_validate(news)
    assert event.country is None
    assert event.currency is None
    assert event.source is None
    assert event.forecast == "5.90%"
    assert event.previous == "-12K"
    assert event.affected_symbols == ["USDBRL"]


def test_response_meta_fields() -> None:
    meta = ResponseMeta(total=500, page=3, per_page=100, rate_limit_remaining=50)
    assert meta.total == 500
    assert meta.page == 3
    assert meta.per_page == 100
    assert meta.rate_limit_remaining == 50
