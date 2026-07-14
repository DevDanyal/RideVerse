"""Exception handler middleware."""

import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("rideverse.errors")


class RideVerseException(Exception):
    """Base exception for RideVerse application."""

    def __init__(self, message: str = "An error occurred", status_code: int = 500, detail: str | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch RideVerseException and return structured JSON error responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle exceptions and format error responses."""
        try:
            response = await call_next(request)
            return response
        except RideVerseException as exc:
            logger.warning(
                "rideverse_error path=%s message=%s status=%d",
                request.url.path,
                exc.message,
                exc.status_code,
            )
            import json

            body = json.dumps({
                "error": exc.message,
                "detail": exc.detail,
                "status_code": exc.status_code,
            })
            return Response(
                content=body,
                status_code=exc.status_code,
                media_type="application/json",
            )
        except Exception as exc:
            logger.exception("unhandled_error path=%s", request.url.path)
            import json

            body = json.dumps({
                "error": "Internal server error",
                "detail": None,
                "status_code": 500,
            })
            return Response(
                content=body,
                status_code=500,
                media_type="application/json",
            )
