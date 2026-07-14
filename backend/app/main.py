"""RideVerse API — Application entry point.

This module creates and configures the FastAPI application, registers
middleware, sets up exception handlers, and wires lifecycle events.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import settings

logger = logging.getLogger(__name__)

# ── Application Factory ────────────────────────────────────────────────────────

app = FastAPI(
    title="RideVerse API",
    version="1.0.0",
    description="AAA Open World Multiplayer Life Simulation Game Backend",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=None,
)


# ── Exception-Handling ASGI Middleware ─────────────────────────────────────────
# Placed outermost so it catches raw exceptions *before* BaseHTTPMiddleware
# wraps them in ExceptionGroup.


class ExceptionHandlerMiddleware:
    """Pure ASGI middleware that converts RideVerseException into JSON responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            from app.core.exceptions import RideVerseException

            if isinstance(exc, RideVerseException):
                response = JSONResponse(
                    status_code=exc.status_code,
                    content={
                        "success": False,
                        "message": exc.message,
                        "error_code": exc.error_code,
                        "errors": exc.errors,
                    },
                )
            else:
                logger.exception("Unhandled exception")
                response = JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": "An unexpected error occurred",
                        "error_code": "INTERNAL_ERROR",
                    },
                )
            await response(scope, receive, send)


# ── CORS Middleware ────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request ID Middleware ──────────────────────────────────────────────────────

@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> JSONResponse:
    """Attach a unique request ID to every incoming request."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id  # type: ignore[attr-defined]
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Access Logging Middleware ──────────────────────────────────────────────────

@app.middleware("http")
async def access_logging_middleware(request: Request, call_next: Any) -> JSONResponse:
    """Log every request method, path, status code, and duration."""
    access_logger = logging.getLogger("app.access")
    access_logger.info(
        "request started",
        extra={
            "method": request.method,
            "path": request.url.path,
            "request_id": getattr(request.state, "request_id", None),
        },
    )
    response = await call_next(request)
    access_logger.info(
        "request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "request_id": getattr(request.state, "request_id", None),
        },
    )
    return response


# Add exception-handling middleware as the outermost layer (last = outermost).
app.add_middleware(ExceptionHandlerMiddleware)


# ── Lifecycle Events ───────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup() -> None:
    """Initialize database engine, verify connectivity, and connect to Redis."""
    from app.core.logging import setup_logging
    setup_logging()

    from app.core.events import on_startup as _on_startup
    await _on_startup(app)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Dispose database engine and close Redis connection."""
    from app.core.events import on_shutdown as _on_shutdown

    await _on_shutdown(app)


# ── Routers ────────────────────────────────────────────────────────────────────

from app.api.v1.router import api_v1_router  # noqa: E402

app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


# ── Root & Health (top-level) ──────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Return basic application information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Quick liveness check — does not verify downstream services."""
    return {"status": "healthy"}
