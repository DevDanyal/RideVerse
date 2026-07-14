"""Authentication middleware."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate JWT tokens on protected routes."""

    def __init__(self, app, excluded_paths: list[str] | None = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/api/v1/auth/login", "/api/v1/auth/register"]

    async def dispatch(self, request: Request, call_next) -> Response:
        """Check Authorization header and validate token."""
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response(
                content='{"detail":"Authorization header required"}',
                status_code=401,
                media_type="application/json",
            )

        token = auth_header.replace("Bearer ", "")
        # TODO: Validate JWT token and attach player to request state
        request.state.token = token

        response = await call_next(request)
        return response
