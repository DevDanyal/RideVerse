"""Request/response logging middleware."""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("rideverse.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests and outgoing responses with timing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request method, path, status code, and duration."""
        start_time = time.time()

        logger.info(
            "request started method=%s path=%s client=%s",
            request.method,
            request.url.path,
            request.client.host if request.client else "unknown",
        )

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "request completed method=%s path=%s status=%d duration=%.2fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Process-Time"] = f"{duration_ms:.2f}"
        return response
