from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.database.base import Base
from app.database.session import get_session
from app.main import app

# ── Test Settings ──────────────────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


def get_test_settings() -> Settings:
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        REDIS_URL="redis://localhost:6379/15",
        SECRET_KEY="test-secret-key",
        JWT_SECRET_KEY="test-jwt-secret",
        ENVIRONMENT="testing",
        DEBUG=True,
    )


# ── Database Fixtures ─────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


# ── Redis Mock ─────────────────────────────────────────────────────────────────
@pytest_asyncio.fixture
def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.close = AsyncMock()
    return redis_mock


# ── HTTP Client Fixtures ──────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthenticated_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Sample Data Fixtures ──────────────────────────────────────────────────────
@pytest.fixture
def sample_register_payload() -> dict[str, str]:
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
    }


@pytest.fixture
def sample_login_payload() -> dict[str, str]:
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture
def mock_settings() -> Settings:
    return get_test_settings()
