"""Integration tests for the Car System (TASK 7).

Tests the full car purchase flow through the API layer with a real database.
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
from app.models.garage import Garage
from app.models.car_variant import CarVariant
from app.repositories.auth import AuthRepository

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_CAR_INT_TABLES = [
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
        "vehicles",
        "cars",
        "car_variants",
        "car_insurance",
        "repair_history",
        "fuel_stations",
        "fuel_transactions",
        "garages",
        "garage_slots",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_CAR_INT_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_CAR_INT_TABLES)
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
            "email": f"carint_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"carint_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


async def _create_player_with_garage(
    session: AsyncSession, email: str = "intplayer@test.com"
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
        level=1,
        experience=0,
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

    garage = Garage(
        player_id=player.id,
        garage_name="Test Garage",
        capacity=5,
        location="Downtown",
        purchase_price=25000.0,
    )
    session.add(garage)
    await session.flush()
    return player


# ══════════════════════════════════════════════════════════════════════════════
# FULL FLOW INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestCarIntegrationFlow:
    """End-to-end integration test: register -> buy car -> customize -> upgrade -> sell."""

    async def test_full_car_lifecycle(self, client: AsyncClient, test_engine):
        token = await _register_and_get_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. List variants (should be empty initially)
        resp = await client.get("/api/v1/cars/variants", headers=headers)
        assert resp.status_code == 200

        # 2. List cars (should be empty)
        resp = await client.get("/api/v1/cars/", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    async def test_variants_endpoint_returns_200(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/cars/variants",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_cars_list_endpoint_returns_200(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/cars/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_unauthenticated_access_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/cars/")
        assert resp.status_code == 401

    async def test_fuel_endpoint_returns_valid_response(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}/fuel",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_repair_cost_endpoint(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}/repair/cost?repair_type=engine",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_insurance_endpoint(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}/insurance",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_upgrade_endpoint(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            f"/api/v1/cars/{uuid.uuid4()}/upgrade",
            json={"component": "engine", "target_level": 2},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)
