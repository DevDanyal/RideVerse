"""Application lifecycle events — startup and shutdown hooks."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI

logger = logging.getLogger(__name__)


async def on_startup(app: FastAPI) -> None:
    """Initialize database engine, verify connectivity, and connect to Redis."""
    logger.info("Starting RideVerse API …")

    # ── PostgreSQL (SQLAlchemy Async) ───────────────────────────────────────
    from app.database.session import engine, async_session_maker
    from sqlalchemy import text

    app.state.db_engine = engine  # type: ignore[attr-defined]
    app.state.db_session_maker = async_session_maker  # type: ignore[attr-defined]

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL connection verified")
    except Exception:
        from app.config import settings
        if settings.ENVIRONMENT == "production":
            logger.exception("PostgreSQL connection failed at startup")
            raise
        logger.warning("PostgreSQL unavailable — running in degraded mode (env=%s)", settings.ENVIRONMENT)
        app.state.db_session_maker = None  # type: ignore[attr-defined]

    # ── Redis ───────────────────────────────────────────────────────────────
    import redis.asyncio as aioredis
    from app.config import settings

    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True, socket_connect_timeout=3
        )
        await redis_client.ping()
        app.state.redis_client = redis_client  # type: ignore[attr-defined]
        logger.info("Redis connection verified")
    except Exception:
        logger.warning("Redis unavailable — running without cache")
        app.state.redis_client = None  # type: ignore[attr-defined]

    # ── Celery (optional) ───────────────────────────────────────────────────
    try:
        from app.workers.celery_app import app as celery_app
        inspect = celery_app.control.inspect(timeout=2.0)
        active = inspect.ping()
        if active:
            logger.info("Celery workers reachable: %s", list(active.keys()))
        else:
            logger.warning("No Celery workers active — background tasks will not run")
    except ImportError:
        logger.warning("Celery not installed — background tasks disabled")
    except Exception:
        logger.warning("Celery broker unavailable — background tasks will not run")

    logger.info("RideVerse API startup complete")


async def on_shutdown(app: FastAPI) -> None:
    """Dispose database engine and close Redis connection."""
    logger.info("Shutting down RideVerse API …")

    # ── PostgreSQL ──────────────────────────────────────────────────────────
    engine = getattr(app.state, "db_engine", None)
    if engine:
        await engine.dispose()
        logger.info("PostgreSQL connection pool disposed")

    # ── Redis ───────────────────────────────────────────────────────────────
    redis_client = getattr(app.state, "redis_client", None)
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

    logger.info("RideVerse API shutdown complete")
