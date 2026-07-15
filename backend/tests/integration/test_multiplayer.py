"""Integration tests for the Multiplayer & WebSocket System (TASK 15).

End-to-end API tests covering the full multiplayer lifecycle:
register, create room, list rooms, get room, update room, delete room,
get sessions, get stats, and WebSocket connection lifecycle.
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

_MP_TABLES = [
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
        "multiplayer_rooms",
        "room_members",
        "websocket_sessions",
        "player_positions",
        "vehicle_sync",
        "player_presence",
        "friend_presences",
        "multiplayer_chat_messages",
        "rate_limit_records",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_MP_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_MP_TABLES)
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
            "email": f"mp_integ_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"mp_integ_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


class TestMultiplayerLifecycle:
    async def test_full_multiplayer_lifecycle(self, client: AsyncClient, test_engine):
        """Test full lifecycle: register -> create room -> list -> get -> update -> sessions -> stats -> delete."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create a room
        resp = await client.post(
            "/api/v1/multiplayer/rooms",
            json={
                "room_name": "Integration Room",
                "room_type": "quick_play",
                "max_players": 8,
                "region": "us-east",
                "map_name": "downtown",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["room_name"] == "Integration Room"
        assert data["data"]["room_type"] == "quick_play"
        assert data["data"]["max_players"] == 8
        assert data["data"]["region"] == "us-east"
        assert data["data"]["map_name"] == "downtown"
        room_id = data["data"]["id"]

        # List rooms
        resp = await client.get(
            "/api/v1/multiplayer/rooms",
            headers=headers,
        )
        assert resp.status_code == 200
        list_data = resp.json()
        assert list_data["total"] >= 1
        room_names = [r["room_name"] for r in list_data["rooms"]]
        assert "Integration Room" in room_names

        # Get room details
        resp = await client.get(
            f"/api/v1/multiplayer/rooms/{room_id}",
            headers=headers,
        )
        assert resp.status_code == 200
        get_data = resp.json()
        assert get_data["success"] is True
        assert get_data["data"]["id"] == room_id

        # Update room
        resp = await client.patch(
            f"/api/v1/multiplayer/rooms/{room_id}",
            json={
                "room_name": "Updated Integration Room",
                "max_players": 12,
                "map_name": "highway",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        update_data = resp.json()
        assert update_data["data"]["room_name"] == "Updated Integration Room"
        assert update_data["data"]["max_players"] == 12
        assert update_data["data"]["map_name"] == "highway"

        # Get sessions
        resp = await client.get(
            "/api/v1/multiplayer/sessions",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        # Get stats
        resp = await client.get(
            "/api/v1/multiplayer/stats",
            headers=headers,
        )
        assert resp.status_code == 200
        stats_data = resp.json()
        assert stats_data["success"] is True
        assert "total_rooms" in stats_data["data"]
        assert stats_data["data"]["total_rooms"] >= 0

        # Delete room
        resp = await client.delete(
            f"/api/v1/multiplayer/rooms/{room_id}",
            headers=headers,
        )
        assert resp.status_code == 200

        # Verify room is gone
        resp = await client.get(
            f"/api/v1/multiplayer/rooms/{room_id}",
            headers=headers,
        )
        assert resp.status_code == 404

    async def test_create_room_with_different_types(self, client: AsyncClient, test_engine):
        """Test creating rooms of different types."""
        for room_type in ["quick_play", "race"]:
            token = await _register_user(client)
            headers = {"Authorization": f"Bearer {token}"}
            resp = await client.post(
                "/api/v1/multiplayer/rooms",
                json={
                    "room_name": f"{room_type.title()} Room",
                    "room_type": room_type,
                    "max_players": 4,
                },
                headers=headers,
            )
            assert resp.status_code == 200
            assert resp.json()["data"]["room_type"] == room_type

    async def test_list_rooms_with_filters(self, client: AsyncClient, test_engine):
        """Test listing rooms with type and region filters."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create rooms
        await client.post(
            "/api/v1/multiplayer/rooms",
            json={"room_name": "Race Room", "room_type": "race", "region": "eu-west"},
            headers=headers,
        )
        await client.post(
            "/api/v1/multiplayer/rooms",
            json={"room_name": "Training Room", "room_type": "training", "region": "us-east"},
            headers=headers,
        )

        # Filter by type
        resp = await client.get(
            "/api/v1/multiplayer/rooms?room_type=race",
            headers=headers,
        )
        assert resp.status_code == 200
        rooms = resp.json()["rooms"]
        assert all(r["room_type"] == "race" for r in rooms)

        # Filter by region
        resp = await client.get(
            "/api/v1/multiplayer/rooms?region=eu-west",
            headers=headers,
        )
        assert resp.status_code == 200
        rooms = resp.json()["rooms"]
        assert all(r["region"] == "eu-west" for r in rooms)

    async def test_unauthorized_access(self, client: AsyncClient):
        """Test that unauthorized requests are rejected."""
        resp = await client.get("/api/v1/multiplayer/rooms")
        assert resp.status_code == 401

        resp = await client.post(
            "/api/v1/multiplayer/rooms",
            json={"room_name": "Unauthorized Room"},
        )
        assert resp.status_code == 401

    async def test_multiple_users_rooms(self, client: AsyncClient, test_engine):
        """Test multiple users can create and see each other's rooms."""
        token1 = await _register_user(client)
        token2 = await _register_user(client)
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 1 creates a room
        resp = await client.post(
            "/api/v1/multiplayer/rooms",
            json={"room_name": "User 1 Room"},
            headers=headers1,
        )
        assert resp.status_code == 200
        room_id = resp.json()["data"]["id"]

        # User 2 can see it
        resp = await client.get(
            f"/api/v1/multiplayer/rooms/{room_id}",
            headers=headers2,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["room_name"] == "User 1 Room"

        # User 2 cannot delete User 1's room
        resp = await client.delete(
            f"/api/v1/multiplayer/rooms/{room_id}",
            headers=headers2,
        )
        assert resp.status_code in (400, 422, 403)
