from __future__ import annotations

import os
from datetime import date, datetime
from typing import Literal

import httpx

from quantgist._version import __version__
from quantgist.exceptions import (
    AuthenticationError,
    NotFoundError,
    PlanUpgradeRequired,
    QuantGistError,
    RateLimitError,
)
from quantgist.models import Event, EventsResponse

_DEFAULT_BASE_URL = "https://api.quantgist.com/v1"


class AsyncQuantGistClient:
    """Async variant of QuantGistClient using httpx.AsyncClient.

    Usage::

        async with AsyncQuantGistClient(api_key="qg_live_...") as client:
            events = await client.get_events(impact="high")
            for e in events.data:
                print(e.title)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("QUANTGIST_API_KEY", "")
        if not self._api_key:
            raise AuthenticationError(
                "API key required. Pass api_key= or set QUANTGIST_API_KEY env var."
            )
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "X-API-Key": self._api_key,
                "User-Agent": f"quantgist-python/{__version__}",
            },
            timeout=timeout,
        )

    async def get_events(
        self,
        *,
        from_date: date | datetime | str | None = None,
        to_date: date | datetime | str | None = None,
        country: str | None = None,
        currency: str | None = None,
        impact: Literal["low", "medium", "high"] | None = None,
        symbol: str | None = None,
        limit: int = 50,
        page: int | None = None,
    ) -> EventsResponse:
        """Fetch a list of macro events with optional filters.

        Args:
            from_date: Start of time range (ISO date or datetime string).
            to_date: End of time range (ISO date or datetime string).
            country: ISO 2-char country code (e.g. ``"US"``).
            currency: Currency code (e.g. ``"USD"``).
            impact: Filter by impact level: ``"low"``, ``"medium"``, or ``"high"``.
            symbol: Instrument symbol (e.g. ``"XAUUSD"``).
            limit: Maximum number of results to return (default 50).
            page: Page number for pagination.

        Returns:
            :class:`~quantgist.models.EventsResponse` containing events and metadata.
        """
        params: dict = {"limit": limit}
        if from_date:
            params["from"] = str(from_date)
        if to_date:
            params["to"] = str(to_date)
        if country:
            params["country"] = country
        if currency:
            params["currency"] = currency
        if impact:
            params["impact"] = impact
        if symbol:
            params["symbol"] = symbol
        if page is not None:
            params["page"] = page

        resp = await self._get("/events", params=params)
        return EventsResponse.model_validate(resp)

    async def get_event(self, event_id: str) -> Event:
        """Fetch a single event by ID.

        Args:
            event_id: The event's unique identifier.

        Returns:
            :class:`~quantgist.models.Event`
        """
        resp = await self._get(f"/events/{event_id}")
        return Event.model_validate(resp["data"])

    async def _get(self, path: str, params: dict | None = None) -> dict:
        response = await self._client.get(path, params=params)
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict:
        if response.status_code == 200:
            return response.json()
        body = response.json() if response.content else {}
        detail = body.get("detail", body.get("error", "Unknown error"))
        if response.status_code == 401:
            raise AuthenticationError(detail, status_code=401)
        if response.status_code == 429:
            raise RateLimitError(detail, status_code=429)
        if response.status_code == 404:
            raise NotFoundError(detail, status_code=404)
        if response.status_code == 402:
            raise PlanUpgradeRequired(detail, status_code=402)
        raise QuantGistError(detail, status_code=response.status_code)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncQuantGistClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
