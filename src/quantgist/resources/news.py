"""News resource for the QuantGist API."""

from __future__ import annotations

from typing import List, Optional

import httpx

from .._http import _clean_params, _raise_for_status
from ..types import NewsResponseDict


class NewsResource:
    """Sync news resource."""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def list(
        self,
        *,
        source: Optional[str] = None,
        currency: Optional[str] = None,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        impact: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        q: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> NewsResponseDict:
        """List news items with optional filters."""
        params = _clean_params(
            {
                "source": source,
                "currency": currency,
                "symbol": symbol,
                "symbols": symbols,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "q": q,
                "page": page,
                "page_size": page_size,
            }
        )
        response = self._client.get(f"{self._base_url}/news", params=params)
        _raise_for_status(response)
        return response.json()


class AsyncNewsResource:
    """Async news resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def list(
        self,
        *,
        source: Optional[str] = None,
        currency: Optional[str] = None,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        impact: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        q: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> NewsResponseDict:
        """Async version of :meth:`NewsResource.list`."""
        params = _clean_params(
            {
                "source": source,
                "currency": currency,
                "symbol": symbol,
                "symbols": symbols,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "q": q,
                "page": page,
                "page_size": page_size,
            }
        )
        response = await self._client.get(f"{self._base_url}/news", params=params)
        _raise_for_status(response)
        return response.json()
