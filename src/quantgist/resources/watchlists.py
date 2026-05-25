"""Watchlists resource for the QuantGist API."""

from __future__ import annotations

from typing import Any, List, Optional

import httpx

from .._http import _clean_params, _raise_for_status


class WatchlistsResource:
    """Sync watchlists resource."""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def list(self) -> List[Any]:
        """List all watchlists for the authenticated user."""
        response = self._client.get(f"{self._base_url}/watchlists")
        _raise_for_status(response)
        return response.json()

    def create(self, name: str, *, description: Optional[str] = None) -> Any:
        """Create a new watchlist."""
        body: dict = {"name": name}
        if description is not None:
            body["description"] = description
        response = self._client.post(
            f"{self._base_url}/watchlists",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    def delete(self, watchlist_id: str) -> None:
        """Delete a watchlist by ID."""
        response = self._client.delete(f"{self._base_url}/watchlists/{watchlist_id}")
        _raise_for_status(response)

    def add_item(
        self,
        watchlist_id: str,
        item_type: str,
        item_value: str,
    ) -> Any:
        """Add an item to a watchlist."""
        body = {"item_type": item_type, "item_value": item_value}
        response = self._client.post(
            f"{self._base_url}/watchlists/{watchlist_id}/items",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    def remove_item(self, watchlist_id: str, item_id: str) -> None:
        """Remove an item from a watchlist."""
        response = self._client.delete(
            f"{self._base_url}/watchlists/{watchlist_id}/items/{item_id}"
        )
        _raise_for_status(response)

    def events(
        self,
        watchlist_id: str,
        *,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        impact: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> Any:
        """Retrieve events for all items in a watchlist."""
        params = _clean_params(
            {
                "from_date": from_date,
                "to_date": to_date,
                "impact": impact,
                "page": page,
                "per_page": per_page,
            }
        )
        response = self._client.get(
            f"{self._base_url}/watchlists/{watchlist_id}/events", params=params
        )
        _raise_for_status(response)
        return response.json()


class AsyncWatchlistsResource:
    """Async watchlists resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def list(self) -> List[Any]:
        """Async version of :meth:`WatchlistsResource.list`."""
        response = await self._client.get(f"{self._base_url}/watchlists")
        _raise_for_status(response)
        return response.json()

    async def create(self, name: str, *, description: Optional[str] = None) -> Any:
        """Async version of :meth:`WatchlistsResource.create`."""
        body: dict = {"name": name}
        if description is not None:
            body["description"] = description
        response = await self._client.post(
            f"{self._base_url}/watchlists",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    async def delete(self, watchlist_id: str) -> None:
        """Async version of :meth:`WatchlistsResource.delete`."""
        response = await self._client.delete(f"{self._base_url}/watchlists/{watchlist_id}")
        _raise_for_status(response)

    async def add_item(
        self,
        watchlist_id: str,
        item_type: str,
        item_value: str,
    ) -> Any:
        """Async version of :meth:`WatchlistsResource.add_item`."""
        body = {"item_type": item_type, "item_value": item_value}
        response = await self._client.post(
            f"{self._base_url}/watchlists/{watchlist_id}/items",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    async def remove_item(self, watchlist_id: str, item_id: str) -> None:
        """Async version of :meth:`WatchlistsResource.remove_item`."""
        response = await self._client.delete(
            f"{self._base_url}/watchlists/{watchlist_id}/items/{item_id}"
        )
        _raise_for_status(response)

    async def events(
        self,
        watchlist_id: str,
        *,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        impact: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> Any:
        """Async version of :meth:`WatchlistsResource.events`."""
        params = _clean_params(
            {
                "from_date": from_date,
                "to_date": to_date,
                "impact": impact,
                "page": page,
                "per_page": per_page,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/watchlists/{watchlist_id}/events", params=params
        )
        _raise_for_status(response)
        return response.json()
