"""Integration tests for the NPC System (TASK 12).

End-to-end API tests covering the full NPC lifecycle:
register, create NPC, schedule, dialogue, profession, interact,
relationship, statistics, spawn points.
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

_NPC_TABLES = [
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
        "npcs",
        "npc_schedules",
        "npc_dialogues",
        "npc_professions",
        "npc_relationships",
        "npc_interactions",
        "npc_statistics",
        "npc_spawns",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_NPC_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_NPC_TABLES)
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
            "email": f"npc_integ_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"npc_integ_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


class TestNpcLifecycle:
    async def test_full_npc_lifecycle(self, client: AsyncClient, test_engine):
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            "/api/v1/npcs/",
            json={
                "npc_name": "Integration NPC",
                "npc_category": "mechanic",
                "description": "A skilled mechanic",
                "level": 5,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        npc_id = resp.json()["data"]["id"]
        assert resp.json()["data"]["npc_name"] == "Integration NPC"

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/schedules",
            json={"period": "morning", "activity": "Open garage", "location_name": "Garage"},
            headers=headers,
        )
        assert resp.status_code == 201

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/schedules",
            json={"period": "evening", "activity": "Close garage", "location_name": "Home"},
            headers=headers,
        )
        assert resp.status_code == 201

        resp = await client.get(f"/api/v1/npcs/{npc_id}/schedules", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 2

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/dialogues",
            json={"dialogue_key": "greeting", "dialogue_text": "Need your car fixed?", "is_greeting": True},
            headers=headers,
        )
        assert resp.status_code == 201

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/dialogues",
            json={"dialogue_key": "repair_offer", "dialogue_text": "I can fix that for 500 coins.", "context": "repair"},
            headers=headers,
        )
        assert resp.status_code == 201

        resp = await client.get(f"/api/v1/npcs/{npc_id}/dialogues", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 2

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/profession",
            json={"profession_type": "mechanic", "skill_level": 8, "specialty": "Engine and transmission"},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["skill_level"] == 8

        resp = await client.get(f"/api/v1/npcs/{npc_id}/profession", headers=headers)
        assert resp.status_code == 200

        resp = await client.get(f"/api/v1/npcs/{npc_id}/statistics", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total_interactions"] == 0

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/spawns",
            json={"zone_name": "Garage District", "location_x": 150.0, "location_y": 250.0, "location_z": 0.0},
            headers=headers,
        )
        assert resp.status_code == 201

        resp = await client.get(f"/api/v1/npcs/{npc_id}/spawns", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

        resp = await client.get(f"/api/v1/npcs/{npc_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == npc_id

        resp = await client.patch(
            f"/api/v1/npcs/{npc_id}",
            json={"npc_name": "Updated NPC", "npc_status": "working"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["npc_name"] == "Updated NPC"

    async def test_npc_list_and_filter(self, client: AsyncClient, test_engine):
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        for name, cat in [("Shop1", "shopkeeper"), ("Shop2", "shopkeeper"), ("Doc1", "doctor")]:
            await client.post(
                "/api/v1/npcs/",
                json={"npc_name": name, "npc_category": cat},
                headers=headers,
            )

        resp = await client.get("/api/v1/npcs/", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 3

        resp = await client.get("/api/v1/npcs/?category=shopkeeper", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 2

        resp = await client.get("/api/v1/npcs/?category=doctor", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    async def test_npc_zone_spawning(self, client: AsyncClient, test_engine):
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Zone NPC", "npc_category": "police_officer"},
            headers=headers,
        )
        npc_id = resp.json()["data"]["id"]

        await client.post(
            f"/api/v1/npcs/{npc_id}/spawns",
            json={"zone_name": "CityCenter", "location_x": 0.0, "location_y": 0.0, "location_z": 0.0},
            headers=headers,
        )

        resp = await client.get("/api/v1/npcs/zone/CityCenter", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    async def test_npc_relationship_lifecycle(self, client: AsyncClient, test_engine):
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Rel NPC", "npc_category": "citizen"},
            headers=headers,
        )
        npc_id = resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/npcs/{npc_id}/relationship", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["level"] == "neutral"

        resp = await client.patch(
            f"/api/v1/npcs/{npc_id}/relationship",
            json={"reputation_score": 60.0},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["level"] == "trusted"

    async def test_unauthenticated_access_denied(self, client: AsyncClient):
        endpoints = [
            ("GET", "/api/v1/npcs/"),
            ("POST", "/api/v1/npcs/"),
        ]
        for method, url in endpoints:
            if method == "GET":
                resp = await client.get(url)
            else:
                resp = await client.post(url, json={"npc_name": "X", "npc_category": "citizen"})
            assert resp.status_code == 401, f"{method} {url} should require auth"
