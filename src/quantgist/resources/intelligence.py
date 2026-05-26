"""Intelligence resource for the QuantGist API."""

from __future__ import annotations

from typing import Any

import httpx

from .._http import _clean_params, _raise_for_status


class IntelligenceResource:
    """Sync intelligence resource."""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def surprises(
        self,
        *,
        currency: str | None = None,
        impact: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
    ) -> list[Any]:
        """Retrieve events with the largest actual-vs-forecast surprises."""
        params = _clean_params(
            {
                "currency": currency,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "limit": limit,
            }
        )
        response = self._client.get(
            f"{self._base_url}/intelligence/surprises", params=params
        )
        _raise_for_status(response)
        return response.json()

    def movers(
        self,
        *,
        currency: str | None = None,
        impact: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
    ) -> list[Any]:
        """Retrieve the biggest market movers based on event releases."""
        params = _clean_params(
            {
                "currency": currency,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "limit": limit,
            }
        )
        response = self._client.get(
            f"{self._base_url}/intelligence/movers", params=params
        )
        _raise_for_status(response)
        return response.json()


class AsyncIntelligenceResource:
    """Async intelligence resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def surprises(
        self,
        *,
        currency: str | None = None,
        impact: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
    ) -> list[Any]:
        """Async version of :meth:`IntelligenceResource.surprises`."""
        params = _clean_params(
            {
                "currency": currency,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "limit": limit,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/intelligence/surprises", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def movers(
        self,
        *,
        currency: str | None = None,
        impact: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
    ) -> list[Any]:
        """Async version of :meth:`IntelligenceResource.movers`."""
        params = _clean_params(
            {
                "currency": currency,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "limit": limit,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/intelligence/movers", params=params
        )
        _raise_for_status(response)
        return response.json()
