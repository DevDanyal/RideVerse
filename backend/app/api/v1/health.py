"""Health check endpoints.

Provides liveness (/), readiness (/ready), and component-level checks for
database and Redis connectivity.
"""
from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter

router = APIRouter()

_start_time = time.monotonic()


# ── Liveness ───────────────────────────────────────────────────────────────────

@router.get("/")
async def health_check() -> dict[str, Any]:
    """Basic liveness probe — confirms the process is running."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": round(time.monotonic() - _start_time, 2),
    }


# ── Database ───────────────────────────────────────────────────────────────────

@router.get("/database")
async def database_health_check() -> dict[str, Any]:
    """Verify PostgreSQL connectivity by executing a simple query."""
    from sqlalchemy import text

    from app.database.session import async_session_maker

    start = time.monotonic()
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {
            "status": "healthy",
            "service": "database",
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {
            "status": "unhealthy",
            "service": "database",
            "latency_ms": latency_ms,
            "error": str(exc),
        }


# ── Redis ──────────────────────────────────────────────────────────────────────

@router.get("/redis")
async def redis_health_check() -> dict[str, Any]:
    """Verify Redis connectivity by executing a PING."""
    import redis.asyncio as aioredis

    from app.config import settings

    start = time.monotonic()
    try:
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        await client.close()
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {
            "status": "healthy",
            "service": "redis",
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {
            "status": "unhealthy",
            "service": "redis",
            "latency_ms": latency_ms,
            "error": str(exc),
        }


# ── Readiness ──────────────────────────────────────────────────────────────────

@router.get("/ready")
async def readiness_check() -> dict[str, Any]:
    """Combined readiness probe — checks all critical downstream services."""
    results: dict[str, Any] = {
        "status": "ready",
        "services": {},
    }

    # Database
    db_result = await database_health_check()
    results["services"]["database"] = db_result["status"]
    if db_result["status"] == "unhealthy":
        results["status"] = "not_ready"

    # Redis
    redis_result = await redis_health_check()
    results["services"]["redis"] = redis_result["status"]
    if redis_result["status"] == "unhealthy":
        results["status"] = "not_ready"

    return results
