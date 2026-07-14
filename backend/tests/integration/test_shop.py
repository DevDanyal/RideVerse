"""Integration tests for the Shop & Marketplace System (TASK 10).

Tests the full shop and marketplace API flows with a real database.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.database.base import Base
from app.dependencies import get_db_session
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_SHOP_INT_TABLES = [
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
        "transactions",
        "daily_rewards",
        "shops",
        "shop_items",
        "shop_transactions",
        "marketplace_listings",
        "marketplace_sales",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_SHOP_INT_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_SHOP_INT_TABLES)
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


async def _register_and_get_token(client: AsyncClient, role: str = "player") -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"shop_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"shop_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 1: Shop API — List & Get
# ══════════════════════════════════════════════════════════════════════════════


class TestShopListAPI:
    """Test listing shops via API."""

    @pytest.mark.asyncio
    async def test_list_shops_empty(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get("/api/v1/shops", headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_shops_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/shops")
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 2: Marketplace API — List
# ══════════════════════════════════════════════════════════════════════════════


class TestMarketplaceListAPI:
    """Test listing marketplace via API."""

    @pytest.mark.asyncio
    async def test_list_marketplace_empty(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get("/api/v1/marketplace", headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_marketplace_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/marketplace")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_my_listings_empty(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get("/api/v1/marketplace/my", headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 0


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 3: Marketplace API — Create & Get Listing
# ══════════════════════════════════════════════════════════════════════════════


class TestMarketplaceCreateAPI:
    """Test creating and retrieving marketplace listings."""

    @pytest.mark.asyncio
    async def test_create_listing(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/marketplace",
            json={"item_type": "vehicle", "item_id": "car_001", "price": 10000.0},
            headers=_auth(token),
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["item_type"] == "vehicle"
        assert data["item_id"] == "car_001"
        assert data["price"] == 10000.0

    @pytest.mark.asyncio
    async def test_create_and_retrieve_listing(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        create_resp = await client.post(
            "/api/v1/marketplace",
            json={"item_type": "bike", "item_id": "bike_001", "price": 5000.0},
            headers=_auth(token),
        )
        listing_id = create_resp.json()["data"]["id"]

        get_resp = await client.get(
            f"/api/v1/marketplace/{listing_id}", headers=_auth(token)
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["item_id"] == "bike_001"

    @pytest.mark.asyncio
    async def test_create_listing_invalid_type(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/marketplace",
            json={"item_type": "invalid", "item_id": "x", "price": 100.0},
            headers=_auth(token),
        )
        assert resp.status_code == 422 or resp.status_code == 400

    @pytest.mark.asyncio
    async def test_create_listing_negative_price(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/marketplace",
            json={"item_type": "vehicle", "item_id": "x", "price": -100.0},
            headers=_auth(token),
        )
        assert resp.status_code == 422 or resp.status_code == 400


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 4: Marketplace API — Cancel Listing
# ══════════════════════════════════════════════════════════════════════════════


class TestMarketplaceCancelAPI:
    """Test cancelling marketplace listings via API."""

    @pytest.mark.asyncio
    async def test_cancel_listing(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        create_resp = await client.post(
            "/api/v1/marketplace",
            json={"item_type": "vehicle", "item_id": "car_001", "price": 10000.0},
            headers=_auth(token),
        )
        listing_id = create_resp.json()["data"]["id"]

        del_resp = await client.delete(
            f"/api/v1/marketplace/{listing_id}", headers=_auth(token)
        )
        assert del_resp.status_code == 200
        assert del_resp.json()["success"] is True


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 5: Shop Buy/Sell API
# ══════════════════════════════════════════════════════════════════════════════


class TestShopBuySellAPI:
    """Test buying and selling via shop API."""

    @pytest.mark.asyncio
    async def test_buy_item_shop_not_found(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/shops/{fake_id}/buy",
            json={"item_id": "bike_001", "quantity": 1},
            headers=_auth(token),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_sell_item_shop_not_found(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/shops/{fake_id}/sell",
            json={"item_id": "bike_001", "quantity": 1},
            headers=_auth(token),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_buy_item_unauthenticated(self, client: AsyncClient):
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/shops/{fake_id}/buy",
            json={"item_id": "bike_001", "quantity": 1},
        )
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 6: Shop Item Listing API
# ══════════════════════════════════════════════════════════════════════════════


class TestShopItemsAPI:
    """Test listing shop items via API."""

    @pytest.mark.asyncio
    async def test_list_shop_items_not_found(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        fake_id = uuid.uuid4()
        resp = await client.get(
            f"/api/v1/shops/{fake_id}/items", headers=_auth(token)
        )
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 7: Shop Restock API
# ══════════════════════════════════════════════════════════════════════════════


class TestShopRestockAPI:
    """Test restocking via API."""

    @pytest.mark.asyncio
    async def test_restock_shop_not_found(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/shops/{fake_id}/restock",
            json={"item_id": "bike_001", "amount": 10},
            headers=_auth(token),
        )
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 8: Shop Discount API
# ══════════════════════════════════════════════════════════════════════════════


class TestShopDiscountAPI:
    """Test applying discount via API."""

    @pytest.mark.asyncio
    async def test_discount_shop_not_found(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/shops/{fake_id}/discount",
            json={"discount_percent": 10.0},
            headers=_auth(token),
        )
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 9: Shop Price Update API
# ══════════════════════════════════════════════════════════════════════════════


class TestShopPriceUpdateAPI:
    """Test updating price via API."""

    @pytest.mark.asyncio
    async def test_price_update_shop_not_found(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/shops/{fake_id}/price",
            json={"item_id": "bike_001", "new_price": 1000.0},
            headers=_auth(token),
        )
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 10: Shop Transactions API
# ══════════════════════════════════════════════════════════════════════════════


class TestShopTransactionsAPI:
    """Test retrieving transactions via API."""

    @pytest.mark.asyncio
    async def test_get_transactions(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/shops/{uuid.uuid4()}/transactions", headers=_auth(token)
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_transactions_unauthenticated(self, client: AsyncClient):
        resp = await client.get(f"/api/v1/shops/{uuid.uuid4()}/transactions")
        assert resp.status_code == 401
