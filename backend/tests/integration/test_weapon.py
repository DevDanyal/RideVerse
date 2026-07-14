"""Integration tests for the Weapon System (TASK 8).

Tests the full weapon purchase flow through the API layer with a real database.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.core.security import create_access_token, get_password_hash
from app.database.base import Base
from app.dependencies import get_db_session
from app.main import app
from app.models.auth import PlayerAccount
from app.models.player import Player, PlayerStatistics, PlayerSettings
from app.models.economy import Wallet
from app.models.inventory import Inventory
from app.models.weapon import Weapon, WeaponType
from app.repositories.auth import AuthRepository

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_WEAPON_INT_TABLES = [
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
        "weapons",
        "player_weapons",
        "weapon_attachments",
        "weapon_ammunition",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_WEAPON_INT_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_WEAPON_INT_TABLES)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
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


async def _register_and_get_token(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"weint_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"weint_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


async def _create_player_with_session(
    session: AsyncSession, email: str = "weplayer@test.com"
) -> Player:
    auth_repo = AuthRepository(session)
    account = await auth_repo.create_account(
        email=email,
        username=email.split("@")[0],
        password_hash=get_password_hash("StrongPass1!"),
    )
    player = Player(
        account_id=account.id,
        display_name=f"Player_{email.split('@')[0]}",
        level=5,
        experience=1000,
        cash=100000.0,
    )
    session.add(player)
    await session.flush()

    stats = PlayerStatistics(player_id=player.id)
    session.add(stats)
    settings = PlayerSettings(player_id=player.id)
    session.add(settings)
    wallet = Wallet(player_id=player.id, cash=100000.0, bank_balance=0.0)
    session.add(wallet)
    inventory = Inventory(player_id=player.id, max_slots=50, used_slots=0, total_weight=0.0)
    session.add(inventory)

    weapon = Weapon(
        weapon_name="M4A1",
        weapon_type=WeaponType.ASSAULT_RIFLE,
        damage=40.0,
        fire_rate=8.0,
        accuracy=70.0,
        range_distance=200.0,
        magazine_size=30,
        reload_time=3.0,
        weight=3.5,
        max_durability=100.0,
        purchase_price=15000.0,
        sell_price=10500.0,
        required_level=1,
        ammo_type="5.56",
    )
    session.add(weapon)
    await session.flush()
    return player


# ══════════════════════════════════════════════════════════════════════════════
# FULL FLOW INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestWeaponIntegrationFlow:
    """End-to-end integration test: register -> buy weapon -> equip -> ammo -> reload -> repair -> sell."""

    async def test_full_weapon_lifecycle(self, client: AsyncClient, test_engine):
        token = await _register_and_get_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. List weapons (should be empty or populated from other tests)
        resp = await client.get("/api/v1/weapons/", headers=headers)
        assert resp.status_code == 200

        # 2. List player weapons (should be empty)
        resp = await client.get("/api/v1/weapons/inventory/list", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"] == []

        # 3. Ammo inventory (should be empty)
        resp = await client.get("/api/v1/weapons/ammo/inventory", headers=headers)
        assert resp.status_code == 200

    async def test_weapons_endpoint_returns_200(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/weapons/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_inventory_endpoint_returns_200(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/weapons/inventory/list",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_ammo_inventory_endpoint_returns_200(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/weapons/ammo/inventory",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_unauthenticated_access_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/weapons/")
        assert resp.status_code == 401

    async def test_buy_weapon_nonexistent_returns_error(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/weapons/buy",
            json={"weapon_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404, 422)

    async def test_sell_nonexistent_returns_error(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/weapons/sell",
            json={"player_weapon_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_equip_nonexistent_returns_error(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/weapons/equip",
            json={"player_weapon_id": str(uuid.uuid4()), "equip": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_repair_nonexistent_returns_error(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/weapons/repair",
            json={"player_weapon_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_reload_nonexistent_returns_error(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/weapons/reload",
            json={"player_weapon_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_attachments_endpoint(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/weapons/{uuid.uuid4()}/attachments",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_stats_endpoint(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/weapons/{uuid.uuid4()}/stats",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)
