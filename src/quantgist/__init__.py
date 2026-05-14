from quantgist._version import __version__
from quantgist.async_client import AsyncQuantGistClient
from quantgist.client import QuantGistClient
from quantgist.exceptions import (
    AuthenticationError,
    NotFoundError,
    PlanUpgradeRequired,
    QuantGistError,
    RateLimitError,
)
from quantgist.models import (
    ChangelogEntry,
    ChangelogResponse,
    EarningsCursorMeta,
    EarningsEvent,
    EarningsMover,
    EarningsResponse,
    EarningsSeasonSummary,
    EarningsSummary,
    EarningsSurprise,
    EarningsWeekCalendar,
    EarningsWeekDay,
    Event,
    EventsResponse,
    MarketQuote,
    MarketsOverviewResponse,
    ResponseMeta,
)

__all__ = [
    "__version__",
    # Clients
    "QuantGistClient",
    "AsyncQuantGistClient",
    # Exceptions
    "QuantGistError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "PlanUpgradeRequired",
    # Macro event models
    "Event",
    "EventsResponse",
    "ResponseMeta",
    # Earnings models
    "EarningsEvent",
    "EarningsCursorMeta",
    "EarningsResponse",
    "EarningsSummary",
    "EarningsSurprise",
    "EarningsMover",
    "EarningsWeekCalendar",
    "EarningsWeekDay",
    "EarningsSeasonSummary",
    # Markets models
    "MarketQuote",
    "MarketsOverviewResponse",
    # Changelog models
    "ChangelogEntry",
    "ChangelogResponse",
]
