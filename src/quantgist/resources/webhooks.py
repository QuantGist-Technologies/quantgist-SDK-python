"""Webhooks resource for the QuantGist API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from .._http import _clean_params, _raise_for_status


class WebhooksResource:
    """Sync webhooks resource.

    All endpoints require the Pro plan or higher.
    """

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def create(
        self,
        url: str,
        *,
        events: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        impact_filter: Optional[List[str]] = None,
        payload_template: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Register a new HTTPS webhook endpoint."""
        body: Dict[str, Any] = {"url": url}
        if events is not None:
            body["events"] = events
        if filters is not None:
            body["filters"] = filters
        if impact_filter is not None:
            body["impact_filter"] = impact_filter
        if payload_template is not None:
            body["payload_template"] = payload_template
        if custom_headers is not None:
            body["custom_headers"] = custom_headers
        response = self._client.post(
            f"{self._base_url}/webhooks",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    def list(self, *, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """List webhook endpoints for the authenticated user."""
        params = _clean_params({"page": page, "per_page": per_page})
        response = self._client.get(f"{self._base_url}/webhooks", params=params)
        _raise_for_status(response)
        return response.json()

    def get(self, endpoint_id: str) -> Dict[str, Any]:
        """Retrieve a single webhook endpoint by ID."""
        response = self._client.get(f"{self._base_url}/webhooks/{endpoint_id}")
        _raise_for_status(response)
        return response.json()

    def update(
        self,
        endpoint_id: str,
        *,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
        impact_filter: Optional[List[str]] = None,
        payload_template: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Update a webhook endpoint."""
        body: Dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if filters is not None:
            body["filters"] = filters
        if is_active is not None:
            body["is_active"] = is_active
        if impact_filter is not None:
            body["impact_filter"] = impact_filter
        if payload_template is not None:
            body["payload_template"] = payload_template
        if custom_headers is not None:
            body["custom_headers"] = custom_headers
        response = self._client.put(
            f"{self._base_url}/webhooks/{endpoint_id}",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    def delete(self, endpoint_id: str) -> None:
        """Delete a webhook endpoint and all its delivery history."""
        response = self._client.delete(f"{self._base_url}/webhooks/{endpoint_id}")
        _raise_for_status(response)

    def deliveries(
        self,
        endpoint_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List delivery history for a webhook endpoint."""
        params = _clean_params({"page": page, "per_page": per_page, "status": status})
        response = self._client.get(
            f"{self._base_url}/webhooks/{endpoint_id}/deliveries", params=params
        )
        _raise_for_status(response)
        return response.json()

    def test(self, endpoint_id: str) -> Dict[str, Any]:
        """Dispatch a synthetic test event to a webhook endpoint."""
        response = self._client.post(f"{self._base_url}/webhooks/{endpoint_id}/test")
        _raise_for_status(response)
        return response.json()

    def get_branding(self) -> Dict[str, Any]:
        """Return the user's white-label notification branding config."""
        response = self._client.get(f"{self._base_url}/webhooks/branding")
        _raise_for_status(response)
        return response.json()

    def update_branding(
        self,
        *,
        bot_name: Optional[str] = None,
        bot_avatar_url: Optional[str] = None,
        color_hex: Optional[str] = None,
        footer_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or update the user's notification branding (upsert)."""
        body: Dict[str, Any] = {}
        if bot_name is not None:
            body["bot_name"] = bot_name
        if bot_avatar_url is not None:
            body["bot_avatar_url"] = bot_avatar_url
        if color_hex is not None:
            body["color_hex"] = color_hex
        if footer_text is not None:
            body["footer_text"] = footer_text
        response = self._client.put(
            f"{self._base_url}/webhooks/branding",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()


class AsyncWebhooksResource:
    """Async webhooks resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def create(
        self,
        url: str,
        *,
        events: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        impact_filter: Optional[List[str]] = None,
        payload_template: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Async version of :meth:`WebhooksResource.create`."""
        body: Dict[str, Any] = {"url": url}
        if events is not None:
            body["events"] = events
        if filters is not None:
            body["filters"] = filters
        if impact_filter is not None:
            body["impact_filter"] = impact_filter
        if payload_template is not None:
            body["payload_template"] = payload_template
        if custom_headers is not None:
            body["custom_headers"] = custom_headers
        response = await self._client.post(
            f"{self._base_url}/webhooks",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    async def list(self, *, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Async version of :meth:`WebhooksResource.list`."""
        params = _clean_params({"page": page, "per_page": per_page})
        response = await self._client.get(f"{self._base_url}/webhooks", params=params)
        _raise_for_status(response)
        return response.json()

    async def get(self, endpoint_id: str) -> Dict[str, Any]:
        """Async version of :meth:`WebhooksResource.get`."""
        response = await self._client.get(f"{self._base_url}/webhooks/{endpoint_id}")
        _raise_for_status(response)
        return response.json()

    async def update(
        self,
        endpoint_id: str,
        *,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
        impact_filter: Optional[List[str]] = None,
        payload_template: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Async version of :meth:`WebhooksResource.update`."""
        body: Dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if filters is not None:
            body["filters"] = filters
        if is_active is not None:
            body["is_active"] = is_active
        if impact_filter is not None:
            body["impact_filter"] = impact_filter
        if payload_template is not None:
            body["payload_template"] = payload_template
        if custom_headers is not None:
            body["custom_headers"] = custom_headers
        response = await self._client.put(
            f"{self._base_url}/webhooks/{endpoint_id}",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()

    async def delete(self, endpoint_id: str) -> None:
        """Async version of :meth:`WebhooksResource.delete`."""
        response = await self._client.delete(f"{self._base_url}/webhooks/{endpoint_id}")
        _raise_for_status(response)

    async def deliveries(
        self,
        endpoint_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Async version of :meth:`WebhooksResource.deliveries`."""
        params = _clean_params({"page": page, "per_page": per_page, "status": status})
        response = await self._client.get(
            f"{self._base_url}/webhooks/{endpoint_id}/deliveries", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def test(self, endpoint_id: str) -> Dict[str, Any]:
        """Async version of :meth:`WebhooksResource.test`."""
        response = await self._client.post(f"{self._base_url}/webhooks/{endpoint_id}/test")
        _raise_for_status(response)
        return response.json()

    async def get_branding(self) -> Dict[str, Any]:
        """Async version of :meth:`WebhooksResource.get_branding`."""
        response = await self._client.get(f"{self._base_url}/webhooks/branding")
        _raise_for_status(response)
        return response.json()

    async def update_branding(
        self,
        *,
        bot_name: Optional[str] = None,
        bot_avatar_url: Optional[str] = None,
        color_hex: Optional[str] = None,
        footer_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Async version of :meth:`WebhooksResource.update_branding`."""
        body: Dict[str, Any] = {}
        if bot_name is not None:
            body["bot_name"] = bot_name
        if bot_avatar_url is not None:
            body["bot_avatar_url"] = bot_avatar_url
        if color_hex is not None:
            body["color_hex"] = color_hex
        if footer_text is not None:
            body["footer_text"] = footer_text
        response = await self._client.put(
            f"{self._base_url}/webhooks/branding",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        _raise_for_status(response)
        return response.json()
