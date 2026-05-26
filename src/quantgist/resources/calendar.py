"""Calendar resource for the QuantGist API."""

from __future__ import annotations

from typing import Any

import httpx

from .._http import _clean_params, _raise_for_status
from ..types import CalendarResponseDict


class CalendarResource:
    """Sync calendar resource."""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def today(
        self,
        *,
        currency: str | None = None,
        impact: str | None = None,
        include_actual: bool | None = None,
    ) -> CalendarResponseDict:
        """Fetch the calendar for today (``GET /v1/calendar``)."""
        params = _clean_params(
            {
                "currency": currency,
                "impact": impact,
                "include_actual": include_actual,
            }
        )
        response = self._client.get(f"{self._base_url}/calendar", params=params)
        _raise_for_status(response)
        return response.json()

    def upcoming(
        self,
        *,
        currency: str | None = None,
        impact: str | None = None,
        limit: int | None = None,
    ) -> CalendarResponseDict:
        """Fetch upcoming calendar events (``GET /v1/calendar/upcoming``)."""
        params = _clean_params(
            {
                "currency": currency,
                "impact": impact,
                "limit": limit,
            }
        )
        response = self._client.get(
            f"{self._base_url}/calendar/upcoming", params=params
        )
        _raise_for_status(response)
        return response.json()

    def get(self, calendar_id: str) -> Any:
        """Fetch a single calendar event by ID (``GET /v1/calendar/{id}``)."""
        response = self._client.get(f"{self._base_url}/calendar/{calendar_id}")
        _raise_for_status(response)
        return response.json()

    def for_date(
        self,
        date: str,
        *,
        currency: str | None = None,
        impact: str | None = None,
        include_actual: bool | None = None,
    ) -> CalendarResponseDict:
        """Fetch the calendar for a specific date."""
        params = _clean_params(
            {
                "date": date,
                "currency": currency,
                "impact": impact,
                "include_actual": include_actual,
            }
        )
        response = self._client.get(f"{self._base_url}/calendar", params=params)
        _raise_for_status(response)
        return response.json()

    def range(
        self,
        start: str,
        end: str,
        *,
        currencies: list[str] | None = None,
        impact: str | None = None,
        limit: int | None = None,
    ) -> Any:
        """Fetch calendar events over a date range (``GET /v1/calendar/range``)."""
        params = _clean_params(
            {
                "start": start,
                "end": end,
                "currencies": currencies,
                "impact": impact,
                "limit": limit,
            }
        )
        response = self._client.get(f"{self._base_url}/calendar/range", params=params)
        _raise_for_status(response)
        return response.json()


class AsyncCalendarResource:
    """Async calendar resource."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def today(
        self,
        *,
        currency: str | None = None,
        impact: str | None = None,
        include_actual: bool | None = None,
    ) -> CalendarResponseDict:
        """Async version of :meth:`CalendarResource.today`."""
        params = _clean_params(
            {
                "currency": currency,
                "impact": impact,
                "include_actual": include_actual,
            }
        )
        response = await self._client.get(f"{self._base_url}/calendar", params=params)
        _raise_for_status(response)
        return response.json()

    async def upcoming(
        self,
        *,
        currency: str | None = None,
        impact: str | None = None,
        limit: int | None = None,
    ) -> CalendarResponseDict:
        """Async version of :meth:`CalendarResource.upcoming`."""
        params = _clean_params(
            {
                "currency": currency,
                "impact": impact,
                "limit": limit,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/calendar/upcoming", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def get(self, calendar_id: str) -> Any:
        """Async version of :meth:`CalendarResource.get`."""
        response = await self._client.get(f"{self._base_url}/calendar/{calendar_id}")
        _raise_for_status(response)
        return response.json()

    async def for_date(
        self,
        date: str,
        *,
        currency: str | None = None,
        impact: str | None = None,
        include_actual: bool | None = None,
    ) -> CalendarResponseDict:
        """Async version of :meth:`CalendarResource.for_date`."""
        params = _clean_params(
            {
                "date": date,
                "currency": currency,
                "impact": impact,
                "include_actual": include_actual,
            }
        )
        response = await self._client.get(f"{self._base_url}/calendar", params=params)
        _raise_for_status(response)
        return response.json()

    async def range(
        self,
        start: str,
        end: str,
        *,
        currencies: list[str] | None = None,
        impact: str | None = None,
        limit: int | None = None,
    ) -> Any:
        """Async version of :meth:`CalendarResource.range`."""
        params = _clean_params(
            {
                "start": start,
                "end": end,
                "currencies": currencies,
                "impact": impact,
                "limit": limit,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/calendar/range", params=params
        )
        _raise_for_status(response)
        return response.json()
