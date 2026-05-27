"""News resource for the QuantGist API."""

from __future__ import annotations

import builtins

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
        source: str | None = None,
        currency: str | None = None,
        symbol: str | None = None,
        symbols: builtins.list[str] | None = None,
        impact: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 25,
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
                "per_page": per_page,
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
        source: str | None = None,
        currency: str | None = None,
        symbol: str | None = None,
        symbols: builtins.list[str] | None = None,
        impact: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 25,
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
                "per_page": per_page,
            }
        )
        response = await self._client.get(f"{self._base_url}/news", params=params)
        _raise_for_status(response)
        return response.json()


# ---------------------------------------------------------------------------
# News Radar — scored, asset-linked event clusters
# ---------------------------------------------------------------------------


def _radar_params(
    *,
    topic: str | None,
    symbols: builtins.list[str] | None,
    min_impact: float | None,
    event_type: str | None,
    status: str | None,
    lookback_hours: int | None,
    limit: int | None,
) -> dict:
    return _clean_params(
        {
            "topic": topic,
            "symbols": symbols,
            "min_impact": min_impact,
            "event_type": event_type,
            "status": status,
            "lookback_hours": lookback_hours,
            "limit": limit,
        }
    )


# Re-open the sync resource to attach the radar / topics helpers. Keeping
# them on the same NewsResource class preserves the discoverability of
# ``client.news.radar(...)`` / ``client.news.topics()``.


def _attach_sync(cls):  # noqa: ANN001
    def radar(
        self,
        *,
        topic: str | None = None,
        symbols: builtins.list[str] | None = None,
        min_impact: float | None = None,
        event_type: str | None = None,
        status: str | None = None,
        lookback_hours: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """List scored, asset-linked News Radar event clusters.

        Args:
            topic: Topic slug (e.g. ``"iran-war"``). See :meth:`topics`.
            symbols: Tickers to intersect with affected_assets.
            min_impact: Minimum impact_score in [0, 1].
            event_type: Topic-pack event_type filter.
            status: ``"developing"`` / ``"breaking"`` / ``"fading"`` / ``"resolved"``.
            lookback_hours: Window over ``latest_seen`` (default 72h).
            limit: Maximum clusters to return.
        """
        params = _radar_params(
            topic=topic,
            symbols=symbols,
            min_impact=min_impact,
            event_type=event_type,
            status=status,
            lookback_hours=lookback_hours,
            limit=limit,
        )
        response = self._client.get(f"{self._base_url}/news/radar", params=params)
        _raise_for_status(response)
        return response.json()

    def topics(self) -> dict:
        """List supported News Radar topic packs."""
        response = self._client.get(f"{self._base_url}/news/topics")
        _raise_for_status(response)
        return response.json()

    def topic(self, slug: str) -> dict:
        """Return one topic pack's detail; raises on 404."""
        response = self._client.get(f"{self._base_url}/news/topics/{slug}")
        _raise_for_status(response)
        return response.json()

    cls.radar = radar
    cls.topics = topics
    cls.topic = topic
    return cls


def _attach_async(cls):  # noqa: ANN001
    async def radar(
        self,
        *,
        topic: str | None = None,
        symbols: builtins.list[str] | None = None,
        min_impact: float | None = None,
        event_type: str | None = None,
        status: str | None = None,
        lookback_hours: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Async version of :meth:`NewsResource.radar`."""
        params = _radar_params(
            topic=topic,
            symbols=symbols,
            min_impact=min_impact,
            event_type=event_type,
            status=status,
            lookback_hours=lookback_hours,
            limit=limit,
        )
        response = await self._client.get(
            f"{self._base_url}/news/radar", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def topics(self) -> dict:
        response = await self._client.get(f"{self._base_url}/news/topics")
        _raise_for_status(response)
        return response.json()

    async def topic(self, slug: str) -> dict:
        response = await self._client.get(f"{self._base_url}/news/topics/{slug}")
        _raise_for_status(response)
        return response.json()

    cls.radar = radar
    cls.topics = topics
    cls.topic = topic
    return cls


_attach_sync(NewsResource)
_attach_async(AsyncNewsResource)
