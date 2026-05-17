"""Internal HTTP helpers shared by resource modules."""

from __future__ import annotations

from typing import Any, Dict

import httpx

from quantgist._version import __version__
from quantgist.exceptions import (
    AuthenticationError,
    NotFoundError,
    PlanUpgradeRequired,
    QuantGistError,
    RateLimitError,
)

_DEFAULT_BASE_URL = "https://api.quantgist.com/v1"
_DEFAULT_TIMEOUT = 30.0


def _build_headers(api_key: str) -> Dict[str, str]:
    return {
        "X-API-Key": api_key,
        "Accept": "application/json",
        "User-Agent": f"quantgist-python/{__version__}",
    }


def _raise_for_status(response: httpx.Response) -> None:
    """Inspect *response* and raise the appropriate SDK exception when needed."""
    if response.is_success:
        return

    try:
        body = response.text
    except Exception:
        body = None

    try:
        payload = response.json() if response.content else {}
        detail = (
            payload.get("detail")
            or payload.get("message")
            or payload.get("error")
            or str(response.status_code)
        )
    except Exception:
        detail = body or str(response.status_code)

    status = response.status_code

    if status == 401:
        raise AuthenticationError(detail, status_code=status)
    if status == 402:
        raise PlanUpgradeRequired(detail, status_code=status)
    if status == 404:
        raise NotFoundError(detail, status_code=status)
    if status == 429:
        raise RateLimitError(detail, status_code=status)
    raise QuantGistError(detail, status_code=status)


def _clean_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values and normalise booleans/lists for query-string use."""
    cleaned: Dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            cleaned[key] = str(value).lower()
        elif isinstance(value, list):
            cleaned[key] = value
        else:
            cleaned[key] = value
    return cleaned
