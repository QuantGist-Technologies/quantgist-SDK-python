class QuantGistError(Exception):
    """Base exception for all QuantGist SDK errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(QuantGistError):
    """Invalid or missing API key."""


class RateLimitError(QuantGistError):
    """Rate limit exceeded. Upgrade plan or wait."""


class NotFoundError(QuantGistError):
    """Requested resource not found."""


class PlanUpgradeRequired(QuantGistError):
    """Feature requires a higher plan tier."""
