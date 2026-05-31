from __future__ import annotations

import os
import warnings
from datetime import date, datetime, timedelta
from typing import Literal

import httpx

from quantgist._version import __version__
from quantgist.exceptions import (
    AuthenticationError,
    NotFoundError,
    PlanUpgradeRequired,
    QuantGistError,
    RateLimitError,
)
from quantgist.models import (
    ChangelogResponse,
    EarningsMover,
    EarningsResponse,
    EarningsSeasonSummary,
    EarningsSummary,
    EarningsSurprise,
    EarningsWeekCalendar,
    Event,
    EventsResponse,
    MarketQuote,
    MarketsOverviewResponse,
)
from quantgist.resources import (
    CalendarResource,
    EventsResource,
    IntelligenceResource,
    NewsResource,
    NotificationsResource,
    SentimentResource,
    SymbolsResource,
    UsageResource,
    V2Resource,
    WatchlistsResource,
    WebhooksResource,
)

_DEFAULT_BASE_URL = "https://api.quantgist.com/v1"
_DEFAULT_V2_BASE_URL = "https://api.quantgist.com/v2"


class QuantGistClient:
    """Synchronous QuantGist client.

    Resource-based API (recommended)::

        client = QuantGistClient(api_key="qg_live_...")
        events = client.events.list(symbol="AAPL", impact="high")
        today  = client.calendar.today()
        news   = client.news.list()

    Legacy flat methods are also exposed on this class for backward
    compatibility (``get_events``, ``get_event``, ``get_earnings_*``,
    ``get_markets_*``, ``get_changelog``). The ``get_earnings_*`` methods
    are deprecated — see method docstrings.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("QUANTGIST_API_KEY", "")
        if not self._api_key:
            raise AuthenticationError(
                "API key required. Pass api_key= or set QUANTGIST_API_KEY env var."
            )
        self._base_url = base_url.rstrip("/")
        # v2 base URL: replace /v1 suffix with /v2, or derive from base_url.
        self._v2_base_url = (
            self._base_url.replace("/v1", "/v2")
            if "/v1" in self._base_url
            else _DEFAULT_V2_BASE_URL
        )
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "X-API-Key": self._api_key,
                "User-Agent": f"quantgist-python/{__version__}",
            },
            timeout=timeout,
        )

        # Resource-based API (canonical).
        self.events = EventsResource(self._client, self._base_url)
        self.calendar = CalendarResource(self._client, self._base_url)
        self.intelligence = IntelligenceResource(self._client, self._base_url)
        self.news = NewsResource(self._client, self._base_url)
        self.notifications = NotificationsResource(self._client, self._base_url)
        self.sentiment = SentimentResource(self._client, self._base_url)
        self.symbols = SymbolsResource(self._client, self._base_url)
        self.usage = UsageResource(self._client, self._base_url)
        self.watchlists = WatchlistsResource(self._client, self._base_url)
        self.webhooks = WebhooksResource(self._client, self._base_url)
        # v2 official-source, revision-aware API.
        self.v2 = V2Resource(self._client, self._v2_base_url)

    # ------------------------------------------------------------------
    # Legacy flat methods (kept for backward compatibility with 0.2.x)
    # ------------------------------------------------------------------
    # The resource-based API (``client.events.list(...)``) is the
    # recommended way to call the API. The methods below remain so existing
    # 0.2.x callers continue to work without modification.

    # ------------------------------------------------------------------
    # Macro events
    # ------------------------------------------------------------------

    def get_events(
        self,
        *,
        from_date: date | datetime | str | None = None,
        to_date: date | datetime | str | None = None,
        country: str | None = None,
        currency: str | None = None,
        impact: Literal["low", "medium", "high"] | None = None,
        symbol: str | None = None,
        limit: int = 50,
    ) -> EventsResponse:
        params: dict = {"per_page": limit}
        if from_date:
            params["from_date"] = str(from_date)
        if to_date:
            params["to_date"] = str(to_date)
        if country:
            params["country"] = country
        if currency:
            params["currency"] = currency
        if impact:
            params["impact"] = impact
        if symbol:
            params["symbol"] = symbol

        resp = self._get("/events", params=params)
        return EventsResponse.model_validate(resp)

    def get_event(self, event_id: str) -> Event:
        resp = self._get(f"/events/{event_id}")
        return Event.model_validate(resp["data"])

    # ------------------------------------------------------------------
    # Earnings
    # ------------------------------------------------------------------

    def get_earnings(
        self,
        *,
        ticker: str | None = None,
        from_date: date | str | None = None,
        to_date: date | str | None = None,
        sector: str | None = None,
        beat_miss: Literal["beat", "miss", "in-line"] | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> EarningsResponse:
        """Fetch a filtered, cursor-paginated list of earnings events.

        Args:
            ticker: Filter to a specific ticker symbol (e.g. ``"AAPL"``).
            from_date: Start of report date range (ISO date string).
            to_date: End of report date range (ISO date string).
            sector: Filter by sector (e.g. ``"Technology"``).
            beat_miss: Filter by outcome: ``"beat"``, ``"miss"``, or ``"in-line"``.
            cursor: Opaque cursor returned by a previous response for pagination.
            limit: Maximum results per page (default 50).

        Returns:
            :class:`~quantgist.models.EarningsResponse`
        """
        params: dict = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        if from_date:
            params["date_from"] = str(from_date)
        if to_date:
            params["date_to"] = str(to_date)
        if sector:
            params["sector"] = sector
        if beat_miss:
            params["beat_miss"] = beat_miss
        if cursor:
            params["cursor"] = cursor
        resp = self._get("/earnings", params=params)
        return EarningsResponse.model_validate(resp)

    def get_earnings_upcoming(self, *, limit: int = 20) -> EarningsResponse:
        """Return the next N upcoming earnings reports (ordered by report date).

        Args:
            limit: Number of upcoming reports to return (default 20).

        Returns:
            :class:`~quantgist.models.EarningsResponse`
        """
        resp = self._get("/earnings/upcoming", params={"limit": limit})
        return EarningsResponse.model_validate(resp)

    def get_earnings_for_ticker(
        self,
        ticker: str,
        *,
        cursor: str | None = None,
        limit: int = 20,
    ) -> EarningsResponse:
        """Return earnings history for a single ticker.

        Args:
            ticker: Ticker symbol (e.g. ``"MSFT"``).
            cursor: Pagination cursor from a previous response.
            limit: Results per page (default 20).

        Returns:
            :class:`~quantgist.models.EarningsResponse`
        """
        params: dict = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        resp = self._get(f"/earnings/{ticker.upper()}", params=params)
        return EarningsResponse.model_validate(resp)

    def get_earnings_summary(self, ticker: str) -> EarningsSummary:
        """Return beat/miss/in-line summary counts for a ticker.

        Args:
            ticker: Ticker symbol (e.g. ``"NVDA"``).

        Returns:
            :class:`~quantgist.models.EarningsSummary`
        """
        resp = self._get(f"/earnings/{ticker.upper()}/summary")
        return EarningsSummary.model_validate(resp.get("data", resp))

    def get_earnings_history(
        self,
        ticker: str,
        *,
        cursor: str | None = None,
        limit: int = 20,
    ) -> EarningsResponse:
        """Return paginated earnings history for a ticker (Pro+ plan required).

        Args:
            ticker: Ticker symbol.
            cursor: Pagination cursor from a previous response.
            limit: Results per page (default 20).

        Returns:
            :class:`~quantgist.models.EarningsResponse`

        Raises:
            :class:`~quantgist.exceptions.PlanUpgradeRequired`: If the account
                is not on the Pro plan or higher.
        """
        params: dict = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        resp = self._get(f"/earnings/{ticker.upper()}/history", params=params)
        return EarningsResponse.model_validate(resp)

    def get_earnings_surprises(self, *, limit: int = 20) -> list[EarningsSurprise]:
        """Return the largest cross-market EPS surprises.

        Args:
            limit: Maximum number of surprises to return (default 20).

        Returns:
            List of :class:`~quantgist.models.EarningsSurprise` objects.
        """
        resp = self._get("/earnings/surprises", params={"limit": limit})
        items = resp.get("data", resp) if isinstance(resp, dict) else resp
        return [EarningsSurprise.model_validate(i) for i in items]

    def get_earnings_movers(self, *, limit: int = 20) -> list[EarningsMover]:
        """Return earnings events ranked by market impact (price move / volume).

        Args:
            limit: Maximum number of movers to return (default 20).

        Returns:
            List of :class:`~quantgist.models.EarningsMover` objects.
        """
        resp = self._get("/earnings/movers", params={"limit": limit})
        items = resp.get("data", resp) if isinstance(resp, dict) else resp
        return [EarningsMover.model_validate(i) for i in items]

    def calendar_this_week(self) -> dict:
        """Return calendar events for the current week (Mon–Sun, UTC).

        Calls ``GET /v1/calendar`` with ``date_from``/``date_to`` covering the
        Monday-to-Sunday window containing today's UTC date. Returns the raw
        paginated response (``{"data": [...], "meta": {...}}``) — the shape is
        the standard QuantGist page response, not the legacy ``EarningsWeekCalendar``.

        Returns:
            Raw paginated dict with ``data`` (list of calendar events) and ``meta``.
        """
        from datetime import timezone as _tz
        today = datetime.now(tz=_tz.utc).date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        params: dict = {
            "date_from": monday.isoformat(),
            "date_to": sunday.isoformat(),
            "per_page": 100,
        }
        return self._get("/calendar", params=params)

    def get_earnings_week_calendar(self) -> EarningsWeekCalendar:
        """Deprecated. Use :meth:`calendar_this_week` instead.

        The ``/earnings/calendar/week`` endpoint no longer exists in the v1
        backend. This wrapper now calls ``/v1/calendar`` over the current
        Mon–Sun window and attempts to coerce the result into the legacy
        :class:`~quantgist.models.EarningsWeekCalendar` shape. Callers should
        migrate to :meth:`calendar_this_week`.
        """
        warnings.warn(
            "get_earnings_week_calendar() is deprecated; "
            "use calendar_this_week() instead. The /earnings/calendar/week "
            "endpoint no longer exists.",
            DeprecationWarning,
            stacklevel=2,
        )
        resp = self.calendar_this_week()
        return EarningsWeekCalendar.model_validate(resp.get("data", resp))

    def get_earnings_season_summary(self) -> EarningsSeasonSummary:
        """Return the index-level aggregate for the current earnings season.

        Returns:
            :class:`~quantgist.models.EarningsSeasonSummary`
        """
        resp = self._get("/earnings/season/summary")
        return EarningsSeasonSummary.model_validate(resp.get("data", resp))

    # ------------------------------------------------------------------
    # Markets (EOD Stooq data)
    # ------------------------------------------------------------------

    def get_markets_overview(self) -> MarketsOverviewResponse:
        """Return an overview of major market indices and instruments.

        Returns:
            :class:`~quantgist.models.MarketsOverviewResponse`
        """
        resp = self._get("/markets/overview")
        return MarketsOverviewResponse.model_validate(resp)

    def get_markets_sectors(self) -> MarketsOverviewResponse:
        """Return EOD quotes for major sector ETFs.

        Returns:
            :class:`~quantgist.models.MarketsOverviewResponse`
        """
        resp = self._get("/markets/sectors")
        return MarketsOverviewResponse.model_validate(resp)

    def get_markets_currencies(self) -> MarketsOverviewResponse:
        """Return EOD quotes for major currency pairs.

        Returns:
            :class:`~quantgist.models.MarketsOverviewResponse`
        """
        resp = self._get("/markets/currencies")
        return MarketsOverviewResponse.model_validate(resp)

    def get_markets_commodities(self) -> MarketsOverviewResponse:
        """Return EOD quotes for major commodities.

        Returns:
            :class:`~quantgist.models.MarketsOverviewResponse`
        """
        resp = self._get("/markets/commodities")
        return MarketsOverviewResponse.model_validate(resp)

    def get_market_quote(self, symbol: str) -> MarketQuote:
        """Return the latest EOD quote for a single symbol.

        Args:
            symbol: Instrument symbol as used by Stooq (e.g. ``"^SPX"``, ``"AAPL.US"``).

        Returns:
            :class:`~quantgist.models.MarketQuote`
        """
        resp = self._get(f"/markets/{symbol}")
        return MarketQuote.model_validate(resp.get("data", resp))

    # ------------------------------------------------------------------
    # Changelog (no auth required, but the client sends the key anyway)
    # ------------------------------------------------------------------

    def get_changelog(self) -> ChangelogResponse:
        """Return the public API changelog.

        No elevated plan is required. Useful for checking recent breaking changes
        or new feature availability.

        Returns:
            :class:`~quantgist.models.ChangelogResponse`
        """
        resp = self._get("/changelog")
        return ChangelogResponse.model_validate(resp)

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict | None = None) -> dict:
        response = self._client.get(path, params=params)
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict:
        if response.status_code == 200:
            return response.json()
        body = response.json() if response.content else {}
        detail = body.get("detail", body.get("error", "Unknown error"))
        if response.status_code == 401:
            raise AuthenticationError(detail, status_code=401)
        if response.status_code == 429:
            raise RateLimitError(detail, status_code=429)
        if response.status_code == 404:
            raise NotFoundError(detail, status_code=404)
        if response.status_code == 402:
            raise PlanUpgradeRequired(detail, status_code=402)
        raise QuantGistError(detail, status_code=response.status_code)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> QuantGistClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
