"""Domain error classes and structured exception definitions."""

from typing import Any, Optional


class AppException(Exception):
    """Base class for all domain-specific application exceptions."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class InvalidUrlException(AppException):
    """Raised when the supplied URL is not a valid LinkedIn profile URL or fails SSRF checks."""

    def __init__(self, message: str = "Invalid LinkedIn profile URL provided.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="INVALID_URL",
            status_code=400,
            details=details,
        )


class ProfileNotFoundException(AppException):
    """Raised when the requested LinkedIn profile does not exist."""

    def __init__(self, message: str = "The requested LinkedIn profile was not found.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="PROFILE_NOT_FOUND",
            status_code=404,
            details=details,
        )


class RateLimitedException(AppException):
    """Raised when request rate limits are encountered."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="RATE_LIMITED",
            status_code=429,
            details=details,
        )


class ProviderUnavailableException(AppException):
    """Raised when upstream data provider is unavailable or returns an upstream error."""

    def __init__(self, message: str = "Upstream profile provider is currently unavailable.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="PROVIDER_UNAVAILABLE",
            status_code=502,
            details=details,
        )
