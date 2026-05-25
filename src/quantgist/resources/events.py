"""Events resource for the QuantGist API."""

from __future__ import annotations

from typing import Any, List, Optional

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
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        q: Optional[str] = None,
        sentiment: Optional[str] = None,
        min_sentiment: Optional[float] = None,
        max_sentiment: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
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
        symbol: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
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
        response = self._client.get(f"{self._base_url}/events/historical", params=params)
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
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        q: Optional[str] = None,
        sentiment: Optional[str] = None,
        min_sentiment: Optional[float] = None,
        max_sentiment: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
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
        symbol: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
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
