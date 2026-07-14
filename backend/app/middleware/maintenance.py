"""Maintenance mode middleware."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MaintenanceMiddleware(BaseHTTPMiddleware):
    """Block non-admin requests when maintenance mode is enabled."""

    def __init__(self, app, enabled: bool = False):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next) -> Response:
        """Reject requests when maintenance mode is active."""
        if not self.enabled:
            return await call_next(request)

        # Allow admin and health check endpoints through
        allowed_paths = ["/api/v1/admin", "/health", "/docs", "/openapi.json"]
        if any(request.url.path.startswith(p) for p in allowed_paths):
            return await call_next(request)

        return Response(
            content='{"error":"Server is in maintenance mode. Please try again later."}',
            status_code=503,
            media_type="application/json",
            headers={"Retry-After": "3600"},
        )

    def enable(self) -> None:
        """Enable maintenance mode."""
        self.enabled = True

    def disable(self) -> None:
        """Disable maintenance mode."""
        self.enabled = False
