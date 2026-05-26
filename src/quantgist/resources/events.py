"""Events resource for the QuantGist API."""

from __future__ import annotations

import builtins
from typing import Any

import httpx

from .._http import _clean_params, _raise_for_status
from ..types import EventDict, EventsResponseDict


class EventsResource:
    """Sync events resource."""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def list(
        self,
        *,
        symbol: str | None = None,
        symbols: builtins.list[str] | None = None,
        currency: str | None = None,
        impact: str | None = None,
        event_type: str | None = None,
        source: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        q: str | None = None,
        sentiment: str | None = None,
        min_sentiment: float | None = None,
        max_sentiment: float | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> EventsResponseDict:
        """List events with optional filters."""
        params = _clean_params(
            {
                "symbol": symbol,
                "symbols": symbols,
                "currency": currency,
                "impact": impact,
                "event_type": event_type,
                "source": source,
                "from_date": from_date,
                "to_date": to_date,
                "q": q,
                "sentiment": sentiment,
                "min_sentiment": min_sentiment,
                "max_sentiment": max_sentiment,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "page": page,
                "per_page": per_page,
            }
        )
        response = self._client.get(f"{self._base_url}/events", params=params)
        _raise_for_status(response)
        return response.json()

    def get(self, event_id: str) -> EventDict:
        """Retrieve a single event by ID."""
        response = self._client.get(f"{self._base_url}/events/{event_id}")
        _raise_for_status(response)
        return response.json()

    def historical(
        self,
        *,
        symbol: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        format: str = "json",
        page: int = 1,
        per_page: int = 25,
    ) -> Any:
        """Retrieve historical events.

        For ``format="ndjson"`` the raw response text is returned for streaming
        parsing; for ``format="json"`` (default) a paginated dict is returned.
        """
        params = _clean_params(
            {
                "symbol": symbol,
                "from_date": from_date,
                "to_date": to_date,
                "format": format,
                "page": page,
                "per_page": per_page,
            }
        )
        response = self._client.get(
            f"{self._base_url}/events/historical", params=params
        )
        _raise_for_status(response)
        if format == "ndjson":
            return response.text
        return response.json()


class AsyncEventsResource:
    """Async events resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def list(
        self,
        *,
        symbol: str | None = None,
        symbols: builtins.list[str] | None = None,
        currency: str | None = None,
        impact: str | None = None,
        event_type: str | None = None,
        source: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        q: str | None = None,
        sentiment: str | None = None,
        min_sentiment: float | None = None,
        max_sentiment: float | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> EventsResponseDict:
        """Async version of :meth:`EventsResource.list`."""
        params = _clean_params(
            {
                "symbol": symbol,
                "symbols": symbols,
                "currency": currency,
                "impact": impact,
                "event_type": event_type,
                "source": source,
                "from_date": from_date,
                "to_date": to_date,
                "q": q,
                "sentiment": sentiment,
                "min_sentiment": min_sentiment,
                "max_sentiment": max_sentiment,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "page": page,
                "per_page": per_page,
            }
        )
        response = await self._client.get(f"{self._base_url}/events", params=params)
        _raise_for_status(response)
        return response.json()

    async def get(self, event_id: str) -> EventDict:
        """Async version of :meth:`EventsResource.get`."""
        response = await self._client.get(f"{self._base_url}/events/{event_id}")
        _raise_for_status(response)
        return response.json()

    async def historical(
        self,
        *,
        symbol: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        format: str = "json",
        page: int = 1,
        per_page: int = 25,
    ) -> Any:
        """Async version of :meth:`EventsResource.historical`."""
        params = _clean_params(
            {
                "symbol": symbol,
                "from_date": from_date,
                "to_date": to_date,
                "format": format,
                "page": page,
                "per_page": per_page,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/events/historical", params=params
        )
        _raise_for_status(response)
        if format == "ndjson":
            return response.text
        return response.json()
