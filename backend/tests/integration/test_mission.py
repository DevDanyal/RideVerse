"""Integration tests for the Mission System (TASK 11).

End-to-end API tests covering the full mission lifecycle:
register → accept → start → progress → complete → claim → history → statistics.
Uses in-memory SQLite database.
"""
from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.database.base import Base
from app.dependencies import get_db_session
from app.main import app
from app.models.mission import (
    Mission,
    MissionObjective,
)

# ── Settings ───────────────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


# ── Tables needed for mission integration tests ───────────────────────────────

_MISSION_TABLES = [
    Base.metadata.tables[name]
    for name in (
        "player_accounts",
        "player_sessions",
        "refresh_tokens",
        "players",
        "player_statistics",
        "player_settings",
        "inventories",
        "wallets",
        "missions",
        "mission_objectives",
        "player_missions",
        "player_objective_progress",
        "mission_history",
        "mission_cooldowns",
        "mission_statistics",
    )
    if name in Base.metadata.tables
]


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_MISSION_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_MISSION_TABLES)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncClient:
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _override():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _register_user(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"integ_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"integ_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


async def _create_mission_via_api(
    client: AsyncClient, token: str, **kwargs
) -> dict:
    """Create a mission directly via the repository (test helper)."""
    from app.core.security import get_password_hash
    from app.models.auth import PlayerAccount
    from app.models.player import Player, PlayerStatistics, PlayerSettings
    from app.models.economy import Wallet
    from app.models.inventory import Inventory
    from app.repositories.auth import AuthRepository

    factory = async_sessionmaker(
        bind=client._transport.app.router, class_=AsyncSession, expire_on_commit=False
    )


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS — Full Lifecycle
# ══════════════════════════════════════════════════════════════════════════════


class TestMissionLifecycle:
    async def test_full_mission_lifecycle(self, client: AsyncClient, test_engine):
        """Accept → Start → Complete → Claim → History → Statistics."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create a mission directly in the test DB
        factory = async_sessionmaker(
            bind=test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with factory() as session:
            mission = Mission(
                mission_name="Integration Mission",
                mission_description="A mission for integration testing",
                category="story",
                difficulty="normal",
                minimum_level=1,
                reward_money=5000.0,
                reward_xp=250,
                reward_reputation=10.0,
            )
            session.add(mission)
            await session.commit()
            mission_id = str(mission.id)

        # Accept mission
        resp = await client.post(
            "/api/v1/missions/accept",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["success"] is True

        # Start mission
        resp = await client.post(
            "/api/v1/missions/start",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["status"] == "in_progress"

        # Complete mission
        resp = await client.post(
            "/api/v1/missions/complete",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["player_mission"]["status"] == "completed"

        # Claim rewards
        resp = await client.post(
            "/api/v1/missions/claim-rewards",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["money_earned"] == 5000.0

        # Check history
        resp = await client.get(
            "/api/v1/missions/history/list",
            headers=headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

        # Check statistics
        resp = await client.get(
            "/api/v1/missions/player/statistics",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["total_completed"] >= 1

    async def test_mission_failure_lifecycle(self, client: AsyncClient, test_engine):
        """Accept → Start → Fail → History."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        factory = async_sessionmaker(
            bind=test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with factory() as session:
            mission = Mission(
                mission_name="Fail Mission",
                mission_description="Mission that will fail",
                category="racing",
                difficulty="hard",
                minimum_level=1,
                reward_money=1000.0,
                reward_xp=100,
                reward_reputation=5.0,
            )
            session.add(mission)
            await session.commit()
            mission_id = str(mission.id)

        # Accept
        resp = await client.post(
            "/api/v1/missions/accept",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 201

        # Start
        resp = await client.post(
            "/api/v1/missions/start",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 201

        # Fail
        resp = await client.post(
            "/api/v1/missions/fail",
            json={"mission_id": mission_id, "failure_reason": "vehicle_destroyed"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["player_mission"]["status"] == "failed"

        # Check history has failure
        resp = await client.get(
            "/api/v1/missions/history/list",
            headers=headers,
        )
        assert resp.status_code == 200
        failures = [h for h in resp.json()["data"] if h["outcome"] == "failed"]
        assert len(failures) >= 1

    async def test_mission_cancel_lifecycle(self, client: AsyncClient, test_engine):
        """Accept → Cancel → History."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        factory = async_sessionmaker(
            bind=test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with factory() as session:
            mission = Mission(
                mission_name="Cancel Mission",
                mission_description="Mission that will be cancelled",
                category="taxi",
                difficulty="easy",
                minimum_level=1,
                reward_money=500.0,
                reward_xp=50,
                reward_reputation=2.0,
            )
            session.add(mission)
            await session.commit()
            mission_id = str(mission.id)

        # Accept
        resp = await client.post(
            "/api/v1/missions/accept",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 201

        # Cancel
        resp = await client.post(
            "/api/v1/missions/cancel",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "cancelled"

    async def test_list_and_details(self, client: AsyncClient, test_engine):
        """List missions and get details."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        factory = async_sessionmaker(
            bind=test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with factory() as session:
            for name in ["List Mission 1", "List Mission 2"]:
                m = Mission(
                    mission_name=name,
                    mission_description="Test",
                    category="delivery",
                    difficulty="easy",
                    minimum_level=1,
                    reward_money=100.0,
                    reward_xp=10,
                    reward_reputation=1.0,
                )
                session.add(m)
            await session.commit()

        # List
        resp = await client.get(
            "/api/v1/missions/",
            headers=headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 2

        # Get first mission ID
        mission_id = resp.json()["data"][0]["id"]

        # Get details
        resp = await client.get(
            f"/api/v1/missions/{mission_id}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["mission_name"] is not None

    async def test_active_missions(self, client: AsyncClient, test_engine):
        """Track active and accepted missions."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        factory = async_sessionmaker(
            bind=test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with factory() as session:
            mission = Mission(
                mission_name="Active Mission",
                mission_description="Active test",
                category="police",
                difficulty="normal",
                minimum_level=1,
                reward_money=2000.0,
                reward_xp=150,
                reward_reputation=8.0,
            )
            session.add(mission)
            await session.commit()
            mission_id = str(mission.id)

        # Accept
        resp = await client.post(
            "/api/v1/missions/accept",
            json={"mission_id": mission_id},
            headers=headers,
        )
        assert resp.status_code == 201

        # Get active
        resp = await client.get(
            "/api/v1/missions/player/active",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["accepted"]) >= 1

    async def test_unauthenticated_access_denied(self, client: AsyncClient):
        """All endpoints require auth."""
        endpoints = [
            ("GET", "/api/v1/missions/"),
            ("POST", "/api/v1/missions/accept"),
            ("POST", "/api/v1/missions/start"),
            ("POST", "/api/v1/missions/complete"),
            ("GET", "/api/v1/missions/history/list"),
            ("GET", "/api/v1/missions/player/statistics"),
        ]
        for method, url in endpoints:
            if method == "GET":
                resp = await client.get(url)
            else:
                resp = await client.post(url, json={"mission_id": str(uuid.uuid4())})
            assert resp.status_code == 401, f"{method} {url} should require auth"
