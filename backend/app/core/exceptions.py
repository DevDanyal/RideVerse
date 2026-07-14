from __future__ import annotations

from typing import Any


class RideVerseException(Exception):
    """Base exception for all RideVerse application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)


class AuthenticationError(RideVerseException):
    """401 — The request lacks valid authentication credentials."""

    status_code = 401
    error_code = "AUTHENTICATION_ERROR"


class AuthorizationError(RideVerseException):
    """403 — The authenticated user lacks permission for this action."""

    status_code = 403
    error_code = "AUTHORIZATION_ERROR"


class NotFoundError(RideVerseException):
    """404 — The requested resource could not be found."""

    status_code = 404
    error_code = "NOT_FOUND"


class ValidationError(RideVerseException):
    """422 — The request body or parameters failed validation."""

    status_code = 422
    error_code = "VALIDATION_ERROR"


class ConflictError(RideVerseException):
    """409 — The request conflicts with the current state of the resource."""

    status_code = 409
    error_code = "CONFLICT"


class RateLimitError(RideVerseException):
    """429 — Too many requests; slow down."""

    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
