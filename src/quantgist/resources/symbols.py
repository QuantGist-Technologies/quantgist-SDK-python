"""Symbols resource for the QuantGist API."""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .._http import _clean_params, _raise_for_status
from ..types import SymbolsResponseDict


class SymbolsResource:
    """Sync symbols resource."""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def list(
        self,
        *,
        q: Optional[str] = None,
        currency: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> SymbolsResponseDict:
        """Search and list available symbols."""
        params = _clean_params(
            {
                "q": q,
                "currency": currency,
                "page": page,
                "page_size": page_size,
            }
        )
        response = self._client.get(f"{self._base_url}/symbols", params=params)
        _raise_for_status(response)
        return response.json()

    def get(self, symbol: str) -> Any:
        """Retrieve details for a single symbol (``GET /v1/symbols/{symbol}``)."""
        response = self._client.get(f"{self._base_url}/symbols/{symbol}")
        _raise_for_status(response)
        return response.json()

    def events(
        self,
        symbol: str,
        *,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        impact: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Any:
        """Retrieve events associated with a symbol."""
        params = _clean_params(
            {
                "from_date": from_date,
                "to_date": to_date,
                "impact": impact,
                "page": page,
                "page_size": page_size,
            }
        )
        response = self._client.get(
            f"{self._base_url}/symbols/{symbol}/events", params=params
        )
        _raise_for_status(response)
        return response.json()


class AsyncSymbolsResource:
    """Async symbols resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def list(
        self,
        *,
        q: Optional[str] = None,
        currency: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> SymbolsResponseDict:
        """Async version of :meth:`SymbolsResource.list`."""
        params = _clean_params(
            {
                "q": q,
                "currency": currency,
                "page": page,
                "page_size": page_size,
            }
        )
        response = await self._client.get(f"{self._base_url}/symbols", params=params)
        _raise_for_status(response)
        return response.json()

    async def get(self, symbol: str) -> Any:
        """Async version of :meth:`SymbolsResource.get`."""
        response = await self._client.get(f"{self._base_url}/symbols/{symbol}")
        _raise_for_status(response)
        return response.json()

    async def events(
        self,
        symbol: str,
        *,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        impact: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Any:
        """Async version of :meth:`SymbolsResource.events`."""
        params = _clean_params(
            {
                "from_date": from_date,
                "to_date": to_date,
                "impact": impact,
                "page": page,
                "page_size": page_size,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/symbols/{symbol}/events", params=params
        )
        _raise_for_status(response)
        return response.json()
