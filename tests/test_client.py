"""Tests for QuantGistClient (sync) and AsyncQuantGistClient.

All HTTP calls are intercepted by respx — no real network traffic.
"""
from __future__ import annotations

import httpx
import pytest
import respx

from quantgist import AsyncQuantGistClient, QuantGistClient
from quantgist.exceptions import AuthenticationError, NotFoundError, RateLimitError
from quantgist.models import Event, EventsResponse

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

TEST_BASE_URL = "https://test.quantgist.com/v1"
FAKE_API_KEY = "qg_live_testfakekey1234567890123456"

SAMPLE_EVENT = {
    "id": "evt_001",
    "title": "Nonfarm Payrolls",
    "country": "US",
    "currency": "USD",
    "release_time": "2024-06-07T12:30:00Z",
    "impact": "high",
    "forecast": 185.0,
    "previous": 165.0,
    "actual": 272.0,
    "surprise_score": 0.87,
    "affected_symbols": ["XAUUSD", "EURUSD", "US30"],
    "source": "bls.gov",
}

SAMPLE_EVENTS_RESPONSE = {
    "data": [SAMPLE_EVENT],
    "meta": {
        "total": 1,
        "page": 1,
        "per_page": 50,
        "rate_limit_remaining": 999,
    },
}

ERROR_401 = {"error": "Unauthorized", "detail": "Invalid API key.", "request_id": "req_abc"}
ERROR_429 = {"error": "Rate limit exceeded", "detail": "Too many requests.", "request_id": "req_def"}
ERROR_404 = {"error": "Not found", "detail": "Event not found.", "request_id": "req_ghi"}


# ---------------------------------------------------------------------------
# Sync client fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> QuantGistClient:
    return QuantGistClient(api_key=FAKE_API_KEY, base_url=TEST_BASE_URL)


@pytest.fixture
def async_client() -> AsyncQuantGistClient:
    return AsyncQuantGistClient(api_key=FAKE_API_KEY, base_url=TEST_BASE_URL)


# ---------------------------------------------------------------------------
# Sync client — get_events
# ---------------------------------------------------------------------------


@respx.mock
def test_get_events_returns_events_response(client: QuantGistClient) -> None:
    respx.get(f"{TEST_BASE_URL}/events").mock(
        return_value=httpx.Response(200, json=SAMPLE_EVENTS_RESPONSE)
    )
    result = client.get_events()

    assert isinstance(result, EventsResponse)
    assert len(result.data) == 1
    assert isinstance(result.data[0], Event)
    assert result.data[0].id == "evt_001"
    assert result.data[0].title == "Nonfarm Payrolls"
    assert result.data[0].impact == "high"
    assert result.meta.total == 1
    assert result.meta.rate_limit_remaining == 999


@respx.mock
def test_get_events_passes_filters(client: QuantGistClient) -> None:
    route = respx.get(f"{TEST_BASE_URL}/events").mock(
        return_value=httpx.Response(200, json=SAMPLE_EVENTS_RESPONSE)
    )
    client.get_events(impact="high", country="US", currency="USD", symbol="XAUUSD")

    assert route.called
    request = route.calls.last.request
    assert b"impact=high" in request.url.query
    assert b"country=US" in request.url.query
    assert b"currency=USD" in request.url.query
    assert b"symbol=XAUUSD" in request.url.query


# ---------------------------------------------------------------------------
# Sync client — get_event
# ---------------------------------------------------------------------------


@respx.mock
def test_get_event_returns_event(client: QuantGistClient) -> None:
    respx.get(f"{TEST_BASE_URL}/events/evt_001").mock(
        return_value=httpx.Response(200, json={"data": SAMPLE_EVENT})
    )
    result = client.get_event("evt_001")

    assert isinstance(result, Event)
    assert result.id == "evt_001"
    assert result.currency == "USD"
    assert result.affected_symbols == ["XAUUSD", "EURUSD", "US30"]


# ---------------------------------------------------------------------------
# Sync client — error handling
# ---------------------------------------------------------------------------


@respx.mock
def test_get_events_401_raises_authentication_error(client: QuantGistClient) -> None:
    respx.get(f"{TEST_BASE_URL}/events").mock(
        return_value=httpx.Response(401, json=ERROR_401)
    )
    with pytest.raises(AuthenticationError) as exc_info:
        client.get_events()
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in str(exc_info.value)


@respx.mock
def test_get_events_429_raises_rate_limit_error(client: QuantGistClient) -> None:
    respx.get(f"{TEST_BASE_URL}/events").mock(
        return_value=httpx.Response(429, json=ERROR_429)
    )
    with pytest.raises(RateLimitError) as exc_info:
        client.get_events()
    assert exc_info.value.status_code == 429


@respx.mock
def test_get_event_404_raises_not_found_error(client: QuantGistClient) -> None:
    respx.get(f"{TEST_BASE_URL}/events/bad_id").mock(
        return_value=httpx.Response(404, json=ERROR_404)
    )
    with pytest.raises(NotFoundError) as exc_info:
        client.get_event("bad_id")
    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Client init — missing API key
# ---------------------------------------------------------------------------


def test_missing_api_key_raises_authentication_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("QUANTGIST_API_KEY", raising=False)
    with pytest.raises(AuthenticationError) as exc_info:
        QuantGistClient(api_key=None, base_url=TEST_BASE_URL)
    assert "API key required" in str(exc_info.value)


def test_missing_api_key_async_raises_authentication_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("QUANTGIST_API_KEY", raising=False)
    with pytest.raises(AuthenticationError) as exc_info:
        AsyncQuantGistClient(api_key=None, base_url=TEST_BASE_URL)
    assert "API key required" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Async client tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_async_get_events_returns_events_response(
    async_client: AsyncQuantGistClient,
) -> None:
    respx.get(f"{TEST_BASE_URL}/events").mock(
        return_value=httpx.Response(200, json=SAMPLE_EVENTS_RESPONSE)
    )
    result = await async_client.get_events()

    assert isinstance(result, EventsResponse)
    assert len(result.data) == 1
    assert result.data[0].id == "evt_001"


@pytest.mark.asyncio
@respx.mock
async def test_async_get_event_returns_event(
    async_client: AsyncQuantGistClient,
) -> None:
    respx.get(f"{TEST_BASE_URL}/events/evt_001").mock(
        return_value=httpx.Response(200, json={"data": SAMPLE_EVENT})
    )
    result = await async_client.get_event("evt_001")

    assert isinstance(result, Event)
    assert result.id == "evt_001"


@pytest.mark.asyncio
@respx.mock
async def test_async_get_events_401_raises_authentication_error(
    async_client: AsyncQuantGistClient,
) -> None:
    respx.get(f"{TEST_BASE_URL}/events").mock(
        return_value=httpx.Response(401, json=ERROR_401)
    )
    with pytest.raises(AuthenticationError):
        await async_client.get_events()


@pytest.mark.asyncio
@respx.mock
async def test_async_get_events_429_raises_rate_limit_error(
    async_client: AsyncQuantGistClient,
) -> None:
    respx.get(f"{TEST_BASE_URL}/events").mock(
        return_value=httpx.Response(429, json=ERROR_429)
    )
    with pytest.raises(RateLimitError):
        await async_client.get_events()


@pytest.mark.asyncio
@respx.mock
async def test_async_get_event_404_raises_not_found_error(
    async_client: AsyncQuantGistClient,
) -> None:
    respx.get(f"{TEST_BASE_URL}/events/bad_id").mock(
        return_value=httpx.Response(404, json=ERROR_404)
    )
    with pytest.raises(NotFoundError):
        await async_client.get_event("bad_id")


# ---------------------------------------------------------------------------
# v2 resource tests
# ---------------------------------------------------------------------------

# v2 base URL is TEST_BASE_URL with /v1 replaced by /v2
TEST_V2_BASE_URL = TEST_BASE_URL.replace("/v1", "/v2")

SAMPLE_V2_EVENT = {
    "id": "v2evt_001",
    "source": "bls",
    "event_type": "economic",
    "release_time": "2024-06-07T12:30:00+00:00",
    "country": "US",
    "currency": "USD",
    "title": "US CPI YoY",
    "impact": "high",
    "canonical_id": "US_CPI_YOY",
    "actual": "3.3",
    "forecast": "3.4",
    "previous": "3.4",
    "verification_status": "verified",
    "conflict_status": None,
}

SAMPLE_V2_LIST_RESPONSE = {
    "data": [SAMPLE_V2_EVENT],
    "meta": {"total": 1, "per_page": 25, "cursor_next": None},
    "backtest_mode": False,
}

SAMPLE_V2_BACKTEST_RESPONSE = {
    "data": [SAMPLE_V2_EVENT],
    "meta": {"total": 1, "per_page": 25, "cursor_next": None},
    "backtest_mode": True,
}

SAMPLE_CANONICAL_EVENTS_RESPONSE = {
    "data": [
        {
            "canonical_id": "US_CPI_YOY",
            "title": "US Consumer Price Index YoY",
            "description": None,
            "country": "US",
            "currency": "USD",
            "impact": "high",
            "sources": {"bls": "CUUR0000SA0", "fred": "CPIAUCSL"},
        }
    ],
    "meta": {"total": 1},
}


@respx.mock
def test_v2_events_returns_list(client: QuantGistClient) -> None:
    """client.v2.events() calls /v2/events and returns raw dict."""
    respx.get(f"{TEST_V2_BASE_URL}/events").mock(
        return_value=httpx.Response(200, json=SAMPLE_V2_LIST_RESPONSE)
    )
    result = client.v2.events()
    assert result["backtest_mode"] is False
    assert len(result["data"]) == 1
    assert result["data"][0]["canonical_id"] == "US_CPI_YOY"


@respx.mock
def test_v2_events_passes_canonical_id(client: QuantGistClient) -> None:
    """canonical_id param is forwarded as query param."""
    route = respx.get(f"{TEST_V2_BASE_URL}/events").mock(
        return_value=httpx.Response(200, json=SAMPLE_V2_LIST_RESPONSE)
    )
    client.v2.events(canonical_id="US_CPI_YOY", from_date="2024-01-01")
    request = route.calls.last.request
    assert b"canonical_id=US_CPI_YOY" in request.url.query
    assert b"from_date=2024-01-01" in request.url.query


@respx.mock
def test_v2_backtest_returns_backtest_mode_true(client: QuantGistClient) -> None:
    """client.v2.backtest() calls /v2/backtest and echoes backtest_mode=True."""
    respx.get(f"{TEST_V2_BASE_URL}/backtest").mock(
        return_value=httpx.Response(200, json=SAMPLE_V2_BACKTEST_RESPONSE)
    )
    result = client.v2.backtest(canonical_id="US_CPI_YOY", as_of="2024-06-15")
    assert result["backtest_mode"] is True
    assert len(result["data"]) == 1


@respx.mock
def test_v2_canonical_events_returns_list(client: QuantGistClient) -> None:
    """client.v2.canonical_events() calls /v2/canonical-events."""
    respx.get(f"{TEST_V2_BASE_URL}/canonical-events").mock(
        return_value=httpx.Response(200, json=SAMPLE_CANONICAL_EVENTS_RESPONSE)
    )
    result = client.v2.canonical_events()
    assert result["meta"]["total"] == 1
    assert result["data"][0]["canonical_id"] == "US_CPI_YOY"


def test_v2_base_url_derived_from_v1(client: QuantGistClient) -> None:
    """v2 base URL replaces /v1 suffix with /v2."""
    # The fixture client was created with base_url=TEST_BASE_URL which ends in /v1
    assert client.v2._base_url == TEST_V2_BASE_URL


def test_v2_base_url_fallback_for_non_v1_url() -> None:
    """When base_url doesn't contain /v1, v2 falls back to the default v2 URL."""
    from quantgist.client import _DEFAULT_V2_BASE_URL
    c = QuantGistClient(api_key=FAKE_API_KEY, base_url="https://custom.example.com")
    assert c.v2._base_url == _DEFAULT_V2_BASE_URL


# ---------------------------------------------------------------------------
# Async v2 resource tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_async_v2_events_returns_list(
    async_client: AsyncQuantGistClient,
) -> None:
    respx.get(f"{TEST_V2_BASE_URL}/events").mock(
        return_value=httpx.Response(200, json=SAMPLE_V2_LIST_RESPONSE)
    )
    result = await async_client.v2.events()
    assert result["backtest_mode"] is False
    assert result["data"][0]["actual"] == "3.3"


@pytest.mark.asyncio
@respx.mock
async def test_async_v2_backtest_returns_backtest_mode_true(
    async_client: AsyncQuantGistClient,
) -> None:
    respx.get(f"{TEST_V2_BASE_URL}/backtest").mock(
        return_value=httpx.Response(200, json=SAMPLE_V2_BACKTEST_RESPONSE)
    )
    result = await async_client.v2.backtest(canonical_id="US_NFP")
    assert result["backtest_mode"] is True
