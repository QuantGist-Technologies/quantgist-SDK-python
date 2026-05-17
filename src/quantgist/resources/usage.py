"""Usage resource for the QuantGist API."""

from __future__ import annotations

from typing import Any, List

import httpx

from .._http import _clean_params, _raise_for_status
from ..types import UsageEndpointItemDict, UsageHistoryItemDict, UsageSummaryDict


class UsageResource:
    """Sync usage resource."""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def summary(self) -> UsageSummaryDict:
        """Retrieve the current usage summary for the authenticated API key."""
        response = self._client.get(f"{self._base_url}/usage")
        _raise_for_status(response)
        return response.json()

    def history(self, *, days: int = 30) -> List[UsageHistoryItemDict]:
        """Retrieve daily request counts for the past *days* days (1–90)."""
        params = _clean_params({"days": days})
        response = self._client.get(f"{self._base_url}/usage/history", params=params)
        _raise_for_status(response)
        return response.json()

    def endpoints(self, *, days: int = 30) -> List[UsageEndpointItemDict]:
        """Retrieve per-endpoint request counts for the past *days* days."""
        params = _clean_params({"days": days})
        response = self._client.get(f"{self._base_url}/usage/endpoints", params=params)
        _raise_for_status(response)
        return response.json()

    def keys(self) -> List[Any]:
        """Retrieve usage breakdown by API key."""
        response = self._client.get(f"{self._base_url}/usage/keys")
        _raise_for_status(response)
        return response.json()


class AsyncUsageResource:
    """Async usage resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def summary(self) -> UsageSummaryDict:
        """Async version of :meth:`UsageResource.summary`."""
        response = await self._client.get(f"{self._base_url}/usage")
        _raise_for_status(response)
        return response.json()

    async def history(self, *, days: int = 30) -> List[UsageHistoryItemDict]:
        """Async version of :meth:`UsageResource.history`."""
        params = _clean_params({"days": days})
        response = await self._client.get(f"{self._base_url}/usage/history", params=params)
        _raise_for_status(response)
        return response.json()

    async def endpoints(self, *, days: int = 30) -> List[UsageEndpointItemDict]:
        """Async version of :meth:`UsageResource.endpoints`."""
        params = _clean_params({"days": days})
        response = await self._client.get(f"{self._base_url}/usage/endpoints", params=params)
        _raise_for_status(response)
        return response.json()

    async def keys(self) -> List[Any]:
        """Async version of :meth:`UsageResource.keys`."""
        response = await self._client.get(f"{self._base_url}/usage/keys")
        _raise_for_status(response)
        return response.json()
