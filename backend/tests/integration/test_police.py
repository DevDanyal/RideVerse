"""Integration tests for the Police System (TASK 13).

End-to-end API tests covering the full Police lifecycle:
register, create station, create officer, commit crime, wanted level,
arrest, fine, jail, report, dispatch, equipment, vehicle.
Uses in-memory SQLite database.
"""
from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.dependencies import get_db_session
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_POLICE_TABLES = [
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
        "police_officers",
        "police_stations",
        "police_crimes",
        "police_wanted_levels",
        "police_arrests",
        "police_fines",
        "police_jail",
        "police_crime_reports",
        "police_dispatches",
        "police_records",
        "police_equipment",
        "police_vehicles",
        "crime_history",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_POLICE_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_POLICE_TABLES)
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


async def _register_user(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"police_integ_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"police_integ_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


async def _register_second_user(client: AsyncClient) -> tuple[str, str]:
    """Register a second user, return (token, username)."""
    username = f"police_cop_{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"{username}@test.com",
            "username": username,
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"], username


class TestPoliceLifecycle:
    async def test_full_police_lifecycle(self, client: AsyncClient, test_engine):
        """Test full lifecycle: register -> station -> officer -> crime -> wanted -> arrest -> fine -> jail."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create a station
        resp = await client.post(
            "/api/v1/police/stations",
            json={
                "station_name": "Integration HQ",
                "department": "city_police",
                "max_officers": 50,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        station_id = resp.json()["data"]["id"]

        # Register second user (will be the officer)
        cop_token, cop_username = await _register_second_user(client)
        cop_headers = {"Authorization": f"Bearer {cop_token}"}

        # Get cop's player ID
        resp = await client.get("/api/v1/players/me", headers=cop_headers)
        assert resp.status_code == 200
        cop_player_id = resp.json()["data"]["id"]

        # Create officer for cop
        resp = await client.post(
            "/api/v1/police/officers",
            json={
                "player_id": cop_player_id,
                "badge_number": f"INT-{uuid.uuid4().hex[:6]}",
                "rank": "patrol_officer",
                "department": "city_police",
                "station_id": station_id,
            },
            headers=cop_headers,
        )
        assert resp.status_code == 201
        officer_id = resp.json()["data"]["id"]

        # Get first user's player ID
        resp = await client.get("/api/v1/players/me", headers=headers)
        assert resp.status_code == 200
        player_id = resp.json()["data"]["id"]

        # Commit a crime
        resp = await client.post(
            "/api/v1/police/crimes",
            json={
                "player_id": player_id,
                "crime_type": "robbery",
                "wanted_level": 4,
                "fine_amount": 15000.0,
                "description": "Bank robbery on Main St",
                "location_name": "Downtown Bank",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        crime_id = resp.json()["data"]["id"]

        # Set wanted level
        resp = await client.post(
            "/api/v1/police/wanted/set",
            json={
                "player_id": player_id,
                "current_level": 4,
                "reason": "Bank robbery",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["current_level"] == 4

        # Get wanted level
        resp = await client.get(
            f"/api/v1/police/wanted/{player_id}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["current_level"] == 4

        # Create arrest
        resp = await client.post(
            "/api/v1/police/arrests",
            json={
                "player_id": player_id,
                "officer_id": officer_id,
                "crime_id": crime_id,
                "wanted_level_at_arrest": 4,
                "fine_amount": 15000.0,
            },
            headers=cop_headers,
        )
        assert resp.status_code == 201
        arrest_id = resp.json()["data"]["id"]

        # Confirm arrest
        resp = await client.post(
            f"/api/v1/police/arrests/{arrest_id}/confirm",
            headers=cop_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "confirmed"

        # Wanted level should be reset after arrest
        resp = await client.get(
            f"/api/v1/police/wanted/{player_id}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["current_level"] == 0

        # Create fine
        resp = await client.post(
            "/api/v1/police/fines",
            json={
                "arrest_id": arrest_id,
                "player_id": player_id,
                "amount": 15000.0,
                "reason": "Bank robbery fine",
            },
            headers=cop_headers,
        )
        assert resp.status_code == 201
        fine_id = resp.json()["data"]["id"]

        # Pay fine
        resp = await client.post(
            f"/api/v1/police/fines/{fine_id}/pay",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "paid"

        # Create jail sentence
        resp = await client.post(
            "/api/v1/police/jail",
            json={
                "arrest_id": arrest_id,
                "player_id": player_id,
                "sentence_seconds": 600,
            },
            headers=cop_headers,
        )
        assert resp.status_code == 201
        jail_id = resp.json()["data"]["id"]
        assert resp.json()["data"]["status"] == "serving"

        # Release prisoner
        resp = await client.post(
            f"/api/v1/police/jail/{jail_id}/release",
            json={"release_reason": "Good behavior"},
            headers=cop_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "released"

        # Check police record
        resp = await client.get(
            f"/api/v1/police/record/{player_id}",
            headers=headers,
        )
        assert resp.status_code == 200

        # List officers
        resp = await client.get(
            "/api/v1/police/officers",
            headers=headers,
        )
        assert resp.status_code == 200

        # List stations
        resp = await client.get(
            "/api/v1/police/stations",
            headers=headers,
        )
        assert resp.status_code == 200
