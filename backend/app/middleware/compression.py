"""GZip compression middleware (placeholder)."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CompressionMiddleware(BaseHTTPMiddleware):
    """GZip compression middleware for response bodies."""

    def __init__(self, app, minimum_size: int = 500):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply gzip compression if client accepts it."""
        response = await call_next(request)

        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding:
            return response

        # TODO: Implement actual gzip compression for large responses
        # For now, pass through unchanged
        return response
