"""Notifications resource for the QuantGist API."""

from __future__ import annotations

from typing import Any

import httpx

from .._http import _clean_params, _raise_for_status


class NotificationsResource:
    """Sync notifications resource.

    All endpoints require the Starter plan or higher. Per-plan channel limits
    are enforced server-side: free = 0, starter = 1, pro = 3, team = unlimited.
    """

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def list_channels(self, *, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        """List notification channels for the authenticated user."""
        params = _clean_params({"page": page, "per_page": per_page})
        response = self._client.get(
            f"{self._base_url}/notifications/channels", params=params
        )
        _raise_for_status(response)
        return response.json()

    def create_channel(
        self,
        channel_type: str,
        *,
        name: str = "My Channel",
        config: dict[str, Any] | None = None,
        events: list[str] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new notification channel."""
        body: dict[str, Any] = {"channel_type": channel_type, "name": name}
        if config is not None:
            body["config"] = config
        if events is not None:
            body["events"] = events
        if filters is not None:
            body["filters"] = filters
        response = self._client.post(
            f"{self._base_url}/notifications/channels",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    def get_channel(self, channel_id: str) -> dict[str, Any]:
        """Retrieve a single notification channel by ID."""
        response = self._client.get(
            f"{self._base_url}/notifications/channels/{channel_id}"
        )
        _raise_for_status(response)
        return response.json()

    def update_channel(
        self,
        channel_id: str,
        *,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        events: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Update an existing notification channel."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if config is not None:
            body["config"] = config
        if events is not None:
            body["events"] = events
        if filters is not None:
            body["filters"] = filters
        if is_active is not None:
            body["is_active"] = is_active
        response = self._client.put(
            f"{self._base_url}/notifications/channels/{channel_id}",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    def delete_channel(self, channel_id: str) -> None:
        """Delete a notification channel."""
        response = self._client.delete(
            f"{self._base_url}/notifications/channels/{channel_id}"
        )
        _raise_for_status(response)

    def test_channel(self, channel_id: str) -> dict[str, Any]:
        """Dispatch a synthetic test notification through a channel."""
        response = self._client.post(
            f"{self._base_url}/notifications/channels/{channel_id}/test"
        )
        _raise_for_status(response)
        return response.json()


class AsyncNotificationsResource:
    """Async notifications resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def list_channels(
        self, *, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Async version of :meth:`NotificationsResource.list_channels`."""
        params = _clean_params({"page": page, "per_page": per_page})
        response = await self._client.get(
            f"{self._base_url}/notifications/channels", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def create_channel(
        self,
        channel_type: str,
        *,
        name: str = "My Channel",
        config: dict[str, Any] | None = None,
        events: list[str] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Async version of :meth:`NotificationsResource.create_channel`."""
        body: dict[str, Any] = {"channel_type": channel_type, "name": name}
        if config is not None:
            body["config"] = config
        if events is not None:
            body["events"] = events
        if filters is not None:
            body["filters"] = filters
        response = await self._client.post(
            f"{self._base_url}/notifications/channels",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    async def get_channel(self, channel_id: str) -> dict[str, Any]:
        """Async version of :meth:`NotificationsResource.get_channel`."""
        response = await self._client.get(
            f"{self._base_url}/notifications/channels/{channel_id}"
        )
        _raise_for_status(response)
        return response.json()

    async def update_channel(
        self,
        channel_id: str,
        *,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        events: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Async version of :meth:`NotificationsResource.update_channel`."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if config is not None:
            body["config"] = config
        if events is not None:
            body["events"] = events
        if filters is not None:
            body["filters"] = filters
        if is_active is not None:
            body["is_active"] = is_active
        response = await self._client.put(
            f"{self._base_url}/notifications/channels/{channel_id}",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    async def delete_channel(self, channel_id: str) -> None:
        """Async version of :meth:`NotificationsResource.delete_channel`."""
        response = await self._client.delete(
            f"{self._base_url}/notifications/channels/{channel_id}"
        )
        _raise_for_status(response)

    async def test_channel(self, channel_id: str) -> dict[str, Any]:
        """Async version of :meth:`NotificationsResource.test_channel`."""
        response = await self._client.post(
            f"{self._base_url}/notifications/channels/{channel_id}/test"
        )
        _raise_for_status(response)
        return response.json()
