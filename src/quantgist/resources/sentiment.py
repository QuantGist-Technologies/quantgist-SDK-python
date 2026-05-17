"""Sentiment resource for the QuantGist API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from .._http import _clean_params, _raise_for_status


class SentimentResource:
    """Sync sentiment resource.

    All endpoints require the Starter plan or higher.
    """

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def summary(
        self,
        *,
        currency: Optional[str] = None,
        country: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        group_by: str = "currency",
    ) -> List[Dict[str, Any]]:
        """Aggregate sentiment statistics grouped by a dimension."""
        params = _clean_params(
            {
                "currency": currency,
                "country": country,
                "from_date": from_date,
                "to_date": to_date,
                "group_by": group_by,
            }
        )
        response = self._client.get(
            f"{self._base_url}/sentiment/summary", params=params
        )
        _raise_for_status(response)
        return response.json()

    def events(
        self,
        *,
        currency: Optional[str] = None,
        country: Optional[str] = None,
        sentiment: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Paginated events filtered and sorted by sentiment score."""
        params = _clean_params(
            {
                "currency": currency,
                "country": country,
                "sentiment": sentiment,
                "min_score": min_score,
                "max_score": max_score,
                "from_date": from_date,
                "to_date": to_date,
                "page": page,
                "per_page": per_page,
                "sort_order": sort_order,
            }
        )
        response = self._client.get(
            f"{self._base_url}/sentiment/events", params=params
        )
        _raise_for_status(response)
        return response.json()


class AsyncSentimentResource:
    """Async sentiment resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def summary(
        self,
        *,
        currency: Optional[str] = None,
        country: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        group_by: str = "currency",
    ) -> List[Dict[str, Any]]:
        """Async version of :meth:`SentimentResource.summary`."""
        params = _clean_params(
            {
                "currency": currency,
                "country": country,
                "from_date": from_date,
                "to_date": to_date,
                "group_by": group_by,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/sentiment/summary", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def events(
        self,
        *,
        currency: Optional[str] = None,
        country: Optional[str] = None,
        sentiment: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Async version of :meth:`SentimentResource.events`."""
        params = _clean_params(
            {
                "currency": currency,
                "country": country,
                "sentiment": sentiment,
                "min_score": min_score,
                "max_score": max_score,
                "from_date": from_date,
                "to_date": to_date,
                "page": page,
                "per_page": per_page,
                "sort_order": sort_order,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/sentiment/events", params=params
        )
        _raise_for_status(response)
        return response.json()
