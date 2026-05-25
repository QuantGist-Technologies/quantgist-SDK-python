"""v2 API resource — official-source, revision-aware, backtest-safe.

Endpoints
---------
GET /v2/events            — filterable list; ``?as_of=`` for revision-aware reads
GET /v2/events/{id}       — single event; ``?include_vintages=true`` for full history
GET /v2/events/{id}/vintages — raw revision history
GET /v2/canonical-events  — discovery: what can I query?
GET /v2/backtest          — convenience shortcut with all four safety flags forced on

The v2 namespace guarantees:
- Every ``actual`` value comes from an official source (BLS, BEA, ECB, Eurostat,
  ONS, FRED/ALFRED, Fed calendar).
- ``?as_of=YYYY-MM-DD`` returns the first-print value published on or before that
  date — suitable for point-in-time backtesting.
- The ``/v2/backtest`` endpoint forces ``released_only``, ``actual_required``,
  ``official_only``, and ``first_print_only`` simultaneously.

Quick start::

    client = QuantGistClient(api_key="qg_live_...")

    # All verified US CPI releases for 2024
    cpi = client.v2.events(
        canonical_id="US_CPI_YOY",
        from_date="2024-01-01",
        to_date="2024-12-31",
    )

    # First-print CPI value as of 2024-06-15 (before any revisions)
    first_print = client.v2.backtest(
        canonical_id="US_CPI_YOY",
        as_of="2024-06-15",
    )
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .._http import _clean_params, _raise_for_status


class V2Resource:
    """Sync v2 API resource.

    Initialised with an ``httpx.Client`` and the **v2** base URL
    (``https://api.quantgist.com/v2``).  The :class:`QuantGistClient`
    builds this automatically — you do not need to pass it yourself.
    """

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        # base_url is already the v2 base (e.g. https://api.quantgist.com/v2)
        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # /v2/events
    # ------------------------------------------------------------------

    def events(
        self,
        *,
        canonical_id: Optional[str] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        as_of: Optional[str] = None,
        verification_status: Optional[str] = None,
        source_rank_max: Optional[int] = None,
        released_only: Optional[bool] = None,
        actual_required: Optional[bool] = None,
        official_only: Optional[bool] = None,
        first_print_only: Optional[bool] = None,
        per_page: int = 50,
        cursor: Optional[str] = None,
    ) -> Any:
        """``GET /v2/events`` — filterable list of verified official-source events.

        Args:
            canonical_id: Filter to a specific canonical event (e.g.
                ``"US_CPI_YOY"``, ``"US_NFP"``, ``"EU_ECB_RATE_DFR"``).
                Call :meth:`canonical_events` to discover available IDs.
            country: ISO 3166-1 alpha-2 code (``"US"``, ``"GB"``, …).
            currency: ISO 4217 code (``"USD"``, ``"EUR"``, …).
            impact: ``"high"``, ``"medium"``, or ``"low"``.
            from_date: ISO 8601 — ``release_time >= from_date``.
            to_date: ISO 8601 — ``release_time <= to_date``.
            as_of: ISO 8601 cutoff for revision-aware reads.  Returns the
                first-print value published on or before this date.
            verification_status: ``"verified"`` (default), ``"conflicting"``,
                ``"unverified"``, or ``"any"``.
            source_rank_max: Only include rows from sources with rank ≤ this
                value (1 = official agencies only).
            released_only: Exclude future events (``release_time <= NOW()``).
            actual_required: Exclude rows where ``actual IS NULL``.
            official_only: Restrict to official-source adapters only
                (excludes ForexFactory, Investing, etc.).
            first_print_only: Return the vintage with ``revision_seq=0``
                instead of the latest revised value.
            per_page: Results per page (max 500, default 50).
            cursor: Opaque pagination cursor.

        Returns:
            Raw dict with ``data`` (list of v2 events), ``meta``, and
            ``backtest_mode`` flag.
        """
        params = _clean_params(
            {
                "canonical_id": canonical_id,
                "country": country,
                "currency": currency,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "as_of": as_of,
                "verification_status": verification_status,
                "source_rank_max": source_rank_max,
                "released_only": released_only,
                "actual_required": actual_required,
                "official_only": official_only,
                "first_print_only": first_print_only,
                "per_page": per_page,
                "cursor": cursor,
            }
        )
        response = self._client.get(f"{self._base_url}/events", params=params)
        _raise_for_status(response)
        return response.json()

    def get_event(
        self,
        event_id: str,
        *,
        include_vintages: bool = False,
    ) -> Any:
        """``GET /v2/events/{id}`` — single event with optional vintage history.

        Args:
            event_id: UUID of the event.
            include_vintages: When ``True``, embeds the full revision history
                in the response under ``vintages``.

        Returns:
            Raw dict with the event data.
        """
        params = _clean_params({"include_vintages": include_vintages or None})
        response = self._client.get(
            f"{self._base_url}/events/{event_id}", params=params
        )
        _raise_for_status(response)
        return response.json()

    def vintages(self, event_id: str) -> Any:
        """``GET /v2/events/{id}/vintages`` — full revision history for an event.

        Returns a list of vintage rows, each with ``revision_seq``,
        ``vintage_date``, ``actual``, and ``source_url``.

        Args:
            event_id: UUID of the event.
        """
        response = self._client.get(
            f"{self._base_url}/events/{event_id}/vintages"
        )
        _raise_for_status(response)
        return response.json()

    # ------------------------------------------------------------------
    # /v2/canonical-events
    # ------------------------------------------------------------------

    def canonical_events(
        self,
        *,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
    ) -> Any:
        """``GET /v2/canonical-events`` — discovery endpoint.

        Returns the list of canonical event IDs (e.g. ``US_CPI_YOY``,
        ``US_NFP``, ``EU_ECB_RATE_DFR``) together with their per-source
        series mappings.

        Args:
            country: ISO 3166-1 alpha-2 filter.
            currency: ISO 4217 filter.
            impact: ``"high"``, ``"medium"``, or ``"low"``.
        """
        params = _clean_params(
            {"country": country, "currency": currency, "impact": impact}
        )
        response = self._client.get(
            f"{self._base_url}/canonical-events", params=params
        )
        _raise_for_status(response)
        return response.json()

    # ------------------------------------------------------------------
    # /v2/backtest  (P2 convenience shortcut)
    # ------------------------------------------------------------------

    def backtest(
        self,
        *,
        canonical_id: Optional[str] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        as_of: Optional[str] = None,
        per_page: int = 50,
        cursor: Optional[str] = None,
    ) -> Any:
        """``GET /v2/backtest`` — backtest-safe event query.

        Equivalent to calling :meth:`events` with all four safety flags
        enabled (``released_only=True``, ``actual_required=True``,
        ``official_only=True``, ``first_print_only=True``) and
        ``verification_status="verified"``.

        The response always contains ``backtest_mode: true``.

        Example — first-print US CPI value as of 2024-06-15::

            result = client.v2.backtest(
                canonical_id="US_CPI_YOY",
                as_of="2024-06-15",
            )
            for row in result["data"]:
                print(row["release_time"], row["actual"])

        Args:
            canonical_id: Canonical event ID (e.g. ``"US_CPI_YOY"``).
            country: ISO 3166-1 alpha-2 filter.
            currency: ISO 4217 filter.
            impact: ``"high"``, ``"medium"``, or ``"low"``.
            from_date: ISO 8601 lower bound (default: 2 years ago).
            to_date: ISO 8601 upper bound.
            as_of: Revision cutoff date.
            per_page: Results per page (max 500).
            cursor: Pagination cursor.
        """
        params = _clean_params(
            {
                "canonical_id": canonical_id,
                "country": country,
                "currency": currency,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "as_of": as_of,
                "per_page": per_page,
                "cursor": cursor,
            }
        )
        response = self._client.get(f"{self._base_url}/backtest", params=params)
        _raise_for_status(response)
        return response.json()

    # ------------------------------------------------------------------
    # /v2/health
    # ------------------------------------------------------------------

    def health(self) -> Any:
        """``GET /v2/health`` — check v2 namespace availability."""
        response = self._client.get(f"{self._base_url}/health")
        _raise_for_status(response)
        return response.json()


class AsyncV2Resource:
    """Async v2 API resource — mirrors :class:`V2Resource`."""

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")

    async def events(
        self,
        *,
        canonical_id: Optional[str] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        as_of: Optional[str] = None,
        verification_status: Optional[str] = None,
        source_rank_max: Optional[int] = None,
        released_only: Optional[bool] = None,
        actual_required: Optional[bool] = None,
        official_only: Optional[bool] = None,
        first_print_only: Optional[bool] = None,
        per_page: int = 50,
        cursor: Optional[str] = None,
    ) -> Any:
        """Async version of :meth:`V2Resource.events`."""
        params = _clean_params(
            {
                "canonical_id": canonical_id,
                "country": country,
                "currency": currency,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "as_of": as_of,
                "verification_status": verification_status,
                "source_rank_max": source_rank_max,
                "released_only": released_only,
                "actual_required": actual_required,
                "official_only": official_only,
                "first_print_only": first_print_only,
                "per_page": per_page,
                "cursor": cursor,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/events", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def get_event(
        self,
        event_id: str,
        *,
        include_vintages: bool = False,
    ) -> Any:
        """Async version of :meth:`V2Resource.get_event`."""
        params = _clean_params({"include_vintages": include_vintages or None})
        response = await self._client.get(
            f"{self._base_url}/events/{event_id}", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def vintages(self, event_id: str) -> Any:
        """Async version of :meth:`V2Resource.vintages`."""
        response = await self._client.get(
            f"{self._base_url}/events/{event_id}/vintages"
        )
        _raise_for_status(response)
        return response.json()

    async def canonical_events(
        self,
        *,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
    ) -> Any:
        """Async version of :meth:`V2Resource.canonical_events`."""
        params = _clean_params(
            {"country": country, "currency": currency, "impact": impact}
        )
        response = await self._client.get(
            f"{self._base_url}/canonical-events", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def backtest(
        self,
        *,
        canonical_id: Optional[str] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        as_of: Optional[str] = None,
        per_page: int = 50,
        cursor: Optional[str] = None,
    ) -> Any:
        """Async version of :meth:`V2Resource.backtest`."""
        params = _clean_params(
            {
                "canonical_id": canonical_id,
                "country": country,
                "currency": currency,
                "impact": impact,
                "from_date": from_date,
                "to_date": to_date,
                "as_of": as_of,
                "per_page": per_page,
                "cursor": cursor,
            }
        )
        response = await self._client.get(
            f"{self._base_url}/backtest", params=params
        )
        _raise_for_status(response)
        return response.json()

    async def health(self) -> Any:
        """Async version of :meth:`V2Resource.health`."""
        response = await self._client.get(f"{self._base_url}/health")
        _raise_for_status(response)
        return response.json()
