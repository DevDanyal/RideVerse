"""Unit tests for the Shop & Marketplace System (TASK 10).

Covers: Shop CRUD, buy/sell items, restock, discount, dynamic pricing,
marketplace listing CRUD, purchase, cancel, search/filter, transaction history.
All tests use an in-memory SQLite database.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.core.security import get_password_hash
from app.database.base import Base
from app.models.auth import PlayerAccount
from app.models.economy import Wallet
from app.models.marketplace import ListingStatus, MarketplaceItemType
from app.models.player import Player, PlayerSettings, PlayerStatistics
from app.models.shop import Shop, ShopCategory, ShopItem, ShopTransactionType
from app.repositories.auth import AuthRepository
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.services.shop import (
    MARKETPLACE_FEE_PERCENT,
    MAX_MARKETPLACE_LISTINGS,
    SELL_PRICE_FACTOR,
    MarketplaceService,
    ShopService,
)

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


def _test_settings() -> Settings:
    return Settings(
        DATABASE_URL=TEST_DB_URL,
        REDIS_URL="redis://localhost:6379/15",
        SECRET_KEY="test-secret",
        JWT_SECRET_KEY="test-jwt-secret",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30,
        JWT_REFRESH_TOKEN_EXPIRE_DAYS=7,
        ENVIRONMENT="testing",
        DEBUG=True,
    )


_SHOP_TABLES = [
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
        "shops",
        "shop_items",
        "shop_transactions",
        "marketplace_listings",
        "marketplace_sales",
    )
    if name in Base.metadata.tables
]


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_SHOP_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_SHOP_TABLES)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        yield session
        if session.is_active:
            await session.rollback()


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _create_player_with_account(
    session: AsyncSession, email: str = "shop@test.com", cash: float = 50000.0
) -> tuple[PlayerAccount, Player]:
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
        cash=cash,
    )
    session.add(player)
    await session.flush()

    stats = PlayerStatistics(player_id=player.id)
    session.add(stats)
    settings = PlayerSettings(player_id=player.id)
    session.add(settings)
    wallet = Wallet(
        player_id=player.id,
        cash=cash,
        bank_balance=10000.0,
        max_cash=500000.0,
        max_bank_balance=10000000.0,
        daily_salary=500.0,
        total_earned=cash,
        total_spent=0.0,
    )
    session.add(wallet)
    await session.flush()
    return account, player


async def _create_shop(session: AsyncSession, **kwargs) -> Shop:
    defaults = {
        "name": "Test Bike Dealer",
        "description": "A test bike shop",
        "location": "Downtown",
        "category": ShopCategory.BIKE_DEALER,
        "is_open": True,
        "tax_rate": 0.08,
        "discount_percent": 5.0,
        "min_player_level": 1,
    }
    defaults.update(kwargs)
    shop = Shop(**defaults)
    session.add(shop)
    await session.flush()
    return shop


async def _create_shop_item(session: AsyncSession, shop_id: uuid.UUID, **kwargs) -> ShopItem:
    defaults = {
        "shop_id": shop_id,
        "item_id": "bike_001",
        "item_name": "Dirt Bike",
        "item_type": "bike",
        "base_price": 5000.0,
        "current_price": 5000.0,
        "stock": 10,
        "max_stock": 50,
        "restock_amount": 5,
        "restock_interval_hours": 24,
        "is_available": True,
        "min_player_level": 1,
        "max_purchases_per_player": 0,
    }
    defaults.update(kwargs)
    item = ShopItem(**defaults)
    session.add(item)
    await session.flush()
    return item


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: ShopService — List & Get Shops
# ══════════════════════════════════════════════════════════════════════════════


class TestShopServiceListShops:
    """Test listing and retrieving shops."""

    @pytest.mark.asyncio
    async def test_get_shops_empty(self, db: AsyncSession):
        svc = ShopService(db)
        shops = await svc.get_shops()
        assert shops == []

    @pytest.mark.asyncio
    async def test_get_shops(self, db: AsyncSession):
        await _create_shop(db)
        svc = ShopService(db)
        shops = await svc.get_shops()
        assert len(shops) == 1
        assert shops[0]["name"] == "Test Bike Dealer"
        assert shops[0]["category"] == "bike_dealer"

    @pytest.mark.asyncio
    async def test_get_shops_by_category(self, db: AsyncSession):
        await _create_shop(db, name="Bike Shop", category=ShopCategory.BIKE_DEALER)
        await _create_shop(db, name="Car Shop", category=ShopCategory.CAR_DEALER)
        await db.flush()

        svc = ShopService(db)
        bike_shops = await svc.get_shops(category="bike_dealer")
        assert len(bike_shops) == 1
        assert bike_shops[0]["name"] == "Bike Shop"

        car_shops = await svc.get_shops(category="car_dealer")
        assert len(car_shops) == 1

    @pytest.mark.asyncio
    async def test_get_shop(self, db: AsyncSession):
        shop = await _create_shop(db)
        svc = ShopService(db)
        result = await svc.get_shop(shop.id)
        assert result["id"] == shop.id
        assert result["name"] == "Test Bike Dealer"

    @pytest.mark.asyncio
    async def test_get_shop_not_found(self, db: AsyncSession):
        svc = ShopService(db)
        with pytest.raises(NotFoundError):
            await svc.get_shop(uuid.uuid4())


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: ShopService — Buy Item
# ══════════════════════════════════════════════════════════════════════════════


class TestShopServiceBuyItem:
    """Test buying items from shops."""

    @pytest.mark.asyncio
    async def test_buy_item_success(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db, tax_rate=0.0, discount_percent=0.0)
        item = await _create_shop_item(db, shop.id, current_price=1000.0, stock=10)

        svc = ShopService(db)
        result = await svc.buy_item(account.id, shop.id, "bike_001", 1)

        assert result["item_name"] == "Dirt Bike"
        assert result["quantity"] == 1
        assert result["total_cost"] == 1000.0
        assert result["new_cash_balance"] == 49000.0

    @pytest.mark.asyncio
    async def test_buy_item_with_quantity(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db, tax_rate=0.0, discount_percent=0.0)
        item = await _create_shop_item(db, shop.id, current_price=1000.0, stock=10)

        svc = ShopService(db)
        result = await svc.buy_item(account.id, shop.id, "bike_001", 3)

        assert result["quantity"] == 3
        assert result["total_cost"] == 3000.0
        assert result["new_cash_balance"] == 47000.0

    @pytest.mark.asyncio
    async def test_buy_item_with_discount(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db, tax_rate=0.0, discount_percent=10.0)
        item = await _create_shop_item(db, shop.id, current_price=1000.0, stock=10)

        svc = ShopService(db)
        result = await svc.buy_item(account.id, shop.id, "bike_001", 1)

        assert result["discount_applied"] == 100.0
        assert result["total_cost"] == 900.0

    @pytest.mark.asyncio
    async def test_buy_item_with_tax(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db, tax_rate=0.10, discount_percent=0.0)
        item = await _create_shop_item(db, shop.id, current_price=1000.0, stock=10)

        svc = ShopService(db)
        result = await svc.buy_item(account.id, shop.id, "bike_001", 1)

        assert result["tax"] == 100.0
        assert result["total_cost"] == 1100.0

    @pytest.mark.asyncio
    async def test_buy_item_with_discount_and_tax(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db, tax_rate=0.10, discount_percent=10.0)
        item = await _create_shop_item(db, shop.id, current_price=1000.0, stock=10)

        svc = ShopService(db)
        result = await svc.buy_item(account.id, shop.id, "bike_001", 1)

        # price = 1000, discount = 10% => 900, tax = 10% => 90, total = 990
        assert result["total_cost"] == 990.0

    @pytest.mark.asyncio
    async def test_buy_item_quantity_zero_fails(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Quantity must be at least 1"):
            await svc.buy_item(account.id, shop.id, "bike_001", 0)

    @pytest.mark.asyncio
    async def test_buy_item_shop_not_found(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        svc = ShopService(db)
        with pytest.raises(NotFoundError, match="Shop not found"):
            await svc.buy_item(account.id, uuid.uuid4(), "bike_001", 1)

    @pytest.mark.asyncio
    async def test_buy_item_shop_closed(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db, is_open=False)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Shop is currently closed"):
            await svc.buy_item(account.id, shop.id, "bike_001", 1)

    @pytest.mark.asyncio
    async def test_buy_item_insufficient_level(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        player.level = 1
        await db.flush()
        shop = await _create_shop(db, min_player_level=10)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="does not meet shop minimum level"):
            await svc.buy_item(account.id, shop.id, "bike_001", 1)

    @pytest.mark.asyncio
    async def test_buy_item_insufficient_stock(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, stock=2)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Insufficient stock"):
            await svc.buy_item(account.id, shop.id, "bike_001", 5)

    @pytest.mark.asyncio
    async def test_buy_item_insufficient_cash(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=100.0)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, current_price=1000.0)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Insufficient cash"):
            await svc.buy_item(account.id, shop.id, "bike_001", 1)

    @pytest.mark.asyncio
    async def test_buy_item_unavailable(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, is_available=False)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Item is currently unavailable"):
            await svc.buy_item(account.id, shop.id, "bike_001", 1)

    @pytest.mark.asyncio
    async def test_buy_item_not_in_shop(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db)
        svc = ShopService(db)
        with pytest.raises(NotFoundError, match="Item not found in this shop"):
            await svc.buy_item(account.id, shop.id, "nonexistent", 1)

    @pytest.mark.asyncio
    async def test_buy_item_player_not_found(self, db: AsyncSession):
        shop = await _create_shop(db)
        svc = ShopService(db)
        with pytest.raises(NotFoundError, match="Player profile not found"):
            await svc.buy_item(uuid.uuid4(), shop.id, "bike_001", 1)

    @pytest.mark.asyncio
    async def test_buy_item_decrements_stock(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, current_price=100.0, stock=10)

        svc = ShopService(db)
        await svc.buy_item(account.id, shop.id, "bike_001", 3)

        # Reload item
        item = await db.get(ShopItem, item.id)
        assert item.stock == 7

    @pytest.mark.asyncio
    async def test_buy_item_unlimited_stock(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=500000.0)
        shop = await _create_shop(db, tax_rate=0.0, discount_percent=0.0)
        item = await _create_shop_item(db, shop.id, current_price=100.0, stock=-1)

        svc = ShopService(db)
        result = await svc.buy_item(account.id, shop.id, "bike_001", 999)
        assert result["quantity"] == 999

    @pytest.mark.asyncio
    async def test_buy_item_idempotency(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, current_price=100.0)

        svc = ShopService(db)
        await svc.buy_item(account.id, shop.id, "bike_001", 1, idempotency_key="key-123")

        with pytest.raises(ConflictError, match="already been processed"):
            await svc.buy_item(account.id, shop.id, "bike_001", 1, idempotency_key="key-123")

    @pytest.mark.asyncio
    async def test_buy_item_purchase_limit(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db)
        item = await _create_shop_item(
            db, shop.id, current_price=100.0, stock=10, max_purchases_per_player=2
        )

        svc = ShopService(db)
        await svc.buy_item(account.id, shop.id, "bike_001", 1)
        await svc.buy_item(account.id, shop.id, "bike_001", 1)

        with pytest.raises(ValidationError, match="Purchase limit exceeded"):
            await svc.buy_item(account.id, shop.id, "bike_001", 1)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: ShopService — Sell Item
# ══════════════════════════════════════════════════════════════════════════════


class TestShopServiceSellItem:
    """Test selling items to shops."""

    @pytest.mark.asyncio
    async def test_sell_item_success(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=1000.0)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, base_price=5000.0)

        svc = ShopService(db)
        result = await svc.sell_item(account.id, shop.id, "bike_001", 1)

        assert result["item_name"] == "Dirt Bike"
        assert result["quantity"] == 1
        assert result["price_per_unit"] == 5000.0 * SELL_PRICE_FACTOR
        assert result["total_earnings"] == 5000.0 * SELL_PRICE_FACTOR
        assert result["new_cash_balance"] == 1000.0 + (5000.0 * SELL_PRICE_FACTOR)

    @pytest.mark.asyncio
    async def test_sell_item_quantity(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=1000.0)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, base_price=1000.0)

        svc = ShopService(db)
        result = await svc.sell_item(account.id, shop.id, "bike_001", 3)

        assert result["total_earnings"] == 3 * 1000.0 * SELL_PRICE_FACTOR

    @pytest.mark.asyncio
    async def test_sell_item_increments_stock(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, base_price=1000.0, stock=5)

        svc = ShopService(db)
        await svc.sell_item(account.id, shop.id, "bike_001", 2)

        item = await db.get(ShopItem, item.id)
        assert item.stock == 7

    @pytest.mark.asyncio
    async def test_sell_item_quantity_zero_fails(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Quantity must be at least 1"):
            await svc.sell_item(account.id, shop.id, "bike_001", 0)

    @pytest.mark.asyncio
    async def test_sell_item_shop_closed_fails(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db, is_open=False)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Shop is currently closed"):
            await svc.sell_item(account.id, shop.id, "bike_001", 1)

    @pytest.mark.asyncio
    async def test_sell_item_not_in_shop(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        shop = await _create_shop(db)
        svc = ShopService(db)
        with pytest.raises(NotFoundError):
            await svc.sell_item(account.id, shop.id, "nonexistent", 1)

    @pytest.mark.asyncio
    async def test_sell_item_cash_limit_exceeded(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=499999.0)
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, base_price=1000000.0)

        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Cash limit would be exceeded"):
            await svc.sell_item(account.id, shop.id, "bike_001", 1)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: ShopService — Transaction History
# ══════════════════════════════════════════════════════════════════════════════


class TestShopServiceTransactionHistory:
    """Test getting player shop transaction history."""

    @pytest.mark.asyncio
    async def test_get_transactions_empty(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        svc = ShopService(db)
        txs = await svc.get_player_transactions(account.id)
        assert txs == []

    @pytest.mark.asyncio
    async def test_get_transactions_after_buy(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)
        shop = await _create_shop(db, tax_rate=0.0, discount_percent=0.0)
        item = await _create_shop_item(db, shop.id, current_price=100.0)

        svc = ShopService(db)
        await svc.buy_item(account.id, shop.id, "bike_001", 2)

        txs = await svc.get_player_transactions(account.id)
        assert len(txs) == 1
        assert txs[0]["transaction_type"] == "buy"
        assert txs[0]["quantity"] == 2


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: ShopService — Restock
# ══════════════════════════════════════════════════════════════════════════════


class TestShopServiceRestock:
    """Test restocking items."""

    @pytest.mark.asyncio
    async def test_restock_success(self, db: AsyncSession):
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, stock=5, max_stock=20)

        svc = ShopService(db)
        result = await svc.restock_item(shop.id, "bike_001", 10)

        assert result["old_stock"] == 5
        assert result["new_stock"] == 15

    @pytest.mark.asyncio
    async def test_restock_negative_amount_fails(self, db: AsyncSession):
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Restock amount must be positive"):
            await svc.restock_item(shop.id, "bike_001", -1)

    @pytest.mark.asyncio
    async def test_restock_exceeds_max_stock_fails(self, db: AsyncSession):
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, stock=18, max_stock=20)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Restock would exceed max stock"):
            await svc.restock_item(shop.id, "bike_001", 5)

    @pytest.mark.asyncio
    async def test_restock_unlimited_stock(self, db: AsyncSession):
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, stock=100, max_stock=-1)

        svc = ShopService(db)
        result = await svc.restock_item(shop.id, "bike_001", 999)
        assert result["new_stock"] == 1099


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6: ShopService — Discount
# ══════════════════════════════════════════════════════════════════════════════


class TestShopServiceDiscount:
    """Test applying discounts."""

    @pytest.mark.asyncio
    async def test_apply_shop_discount(self, db: AsyncSession):
        shop = await _create_shop(db)
        svc = ShopService(db)
        result = await svc.apply_discount(shop.id, 20.0)
        assert result["discount_percent"] == 20.0
        assert result["shop_name"] == "Test Bike Dealer"

    @pytest.mark.asyncio
    async def test_apply_item_discount(self, db: AsyncSession):
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, base_price=1000.0)

        svc = ShopService(db)
        result = await svc.apply_discount(shop.id, 25.0, item_id="bike_001")
        assert result["discount_percent"] == 25.0
        assert result["new_price"] == 750.0

    @pytest.mark.asyncio
    async def test_discount_out_of_range_fails(self, db: AsyncSession):
        shop = await _create_shop(db)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Discount percent must be between 0 and 100"):
            await svc.apply_discount(shop.id, 150.0)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7: ShopService — Dynamic Pricing
# ══════════════════════════════════════════════════════════════════════════════


class TestShopServiceDynamicPricing:
    """Test dynamic pricing updates."""

    @pytest.mark.asyncio
    async def test_update_price(self, db: AsyncSession):
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id, current_price=5000.0)

        svc = ShopService(db)
        result = await svc.update_price(shop.id, "bike_001", 4500.0)
        assert result["old_price"] == 5000.0
        assert result["new_price"] == 4500.0

    @pytest.mark.asyncio
    async def test_update_price_negative_fails(self, db: AsyncSession):
        shop = await _create_shop(db)
        item = await _create_shop_item(db, shop.id)
        svc = ShopService(db)
        with pytest.raises(ValidationError, match="Price cannot be negative"):
            await svc.update_price(shop.id, "bike_001", -100.0)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8: ShopService — Shop Items Listing
# ══════════════════════════════════════════════════════════════════════════════


class TestShopServiceShopItems:
    """Test listing shop items."""

    @pytest.mark.asyncio
    async def test_get_shop_items(self, db: AsyncSession):
        shop = await _create_shop(db)
        await _create_shop_item(db, shop.id, item_id="bike_001", item_name="Dirt Bike")
        await _create_shop_item(db, shop.id, item_id="bike_002", item_name="Sports Bike")

        svc = ShopService(db)
        items = await svc.get_shop_items(shop.id)
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_get_shop_items_excludes_unavailable(self, db: AsyncSession):
        shop = await _create_shop(db)
        await _create_shop_item(db, shop.id, item_id="bike_001", is_available=True)
        await _create_shop_item(db, shop.id, item_id="bike_002", is_available=False)

        svc = ShopService(db)
        items = await svc.get_shop_items(shop.id)
        assert len(items) == 1
        assert items[0]["item_id"] == "bike_001"

    @pytest.mark.asyncio
    async def test_get_shop_items_shop_not_found(self, db: AsyncSession):
        svc = ShopService(db)
        with pytest.raises(NotFoundError):
            await svc.get_shop_items(uuid.uuid4())


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9: MarketplaceService — Create Listing
# ══════════════════════════════════════════════════════════════════════════════


class TestMarketplaceServiceCreateListing:
    """Test creating marketplace listings."""

    @pytest.mark.asyncio
    async def test_create_listing(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        svc = MarketplaceService(db)
        listing = await svc.create_listing(account.id, "vehicle", "car_001", 10000.0)

        assert listing["item_type"] == "vehicle"
        assert listing["item_id"] == "car_001"
        assert listing["price"] == 10000.0
        assert listing["listing_status"] == "active"

    @pytest.mark.asyncio
    async def test_create_listing_invalid_item_type(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        with pytest.raises(ValidationError, match="Invalid item type"):
            await svc.create_listing(account.id, "invalid_type", "item_1", 100.0)

    @pytest.mark.asyncio
    async def test_create_listing_negative_price(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        with pytest.raises(ValidationError, match="Listing price must be positive"):
            await svc.create_listing(account.id, "vehicle", "car_001", -100.0)

    @pytest.mark.asyncio
    async def test_create_listing_zero_price(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        with pytest.raises(ValidationError, match="Listing price must be positive"):
            await svc.create_listing(account.id, "vehicle", "car_001", 0.0)

    @pytest.mark.asyncio
    async def test_create_listing_max_limit(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        svc = MarketplaceService(db)

        for i in range(MAX_MARKETPLACE_LISTINGS):
            await svc.create_listing(account.id, "vehicle", f"car_{i}", 1000.0 + i)

        with pytest.raises(ValidationError, match="Maximum active listings"):
            await svc.create_listing(account.id, "vehicle", "car_extra", 1000.0)

    @pytest.mark.asyncio
    async def test_create_listing_player_not_found(self, db: AsyncSession):
        svc = MarketplaceService(db)
        with pytest.raises(NotFoundError, match="Player profile not found"):
            await svc.create_listing(uuid.uuid4(), "vehicle", "car_001", 10000.0)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10: MarketplaceService — Purchase Listing
# ══════════════════════════════════════════════════════════════════════════════


class TestMarketplaceServicePurchaseListing:
    """Test purchasing marketplace listings."""

    @pytest.mark.asyncio
    async def test_purchase_listing(self, db: AsyncSession):
        seller_acct, seller = await _create_player_with_account(
            db, email="seller@test.com", cash=5000.0
        )
        buyer_acct, buyer = await _create_player_with_account(
            db, email="buyer@test.com", cash=50000.0
        )

        svc = MarketplaceService(db)
        listing = await svc.create_listing(seller_acct.id, "vehicle", "car_001", 10000.0)

        result = await svc.purchase_listing(buyer_acct.id, listing["id"])

        assert result["sale_price"] == 10000.0
        assert result["marketplace_fee"] == round(10000.0 * MARKETPLACE_FEE_PERCENT, 2)
        assert result["seller_proceeds"] == round(10000.0 * (1 - MARKETPLACE_FEE_PERCENT), 2)
        assert result["message"] == "Purchase successful"

    @pytest.mark.asyncio
    async def test_purchase_listing_fee_calculation(self, db: AsyncSession):
        seller_acct, seller = await _create_player_with_account(
            db, email="seller@test.com", cash=5000.0
        )
        buyer_acct, buyer = await _create_player_with_account(
            db, email="buyer@test.com", cash=50000.0
        )

        svc = MarketplaceService(db)
        listing = await svc.create_listing(seller_acct.id, "vehicle", "car_001", 1000.0)

        result = await svc.purchase_listing(buyer_acct.id, listing["id"])

        fee = round(1000.0 * 0.05, 2)  # 5%
        assert result["marketplace_fee"] == fee
        assert result["seller_proceeds"] == round(1000.0 - fee, 2)

    @pytest.mark.asyncio
    async def test_purchase_own_listing_fails(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=50000.0)

        svc = MarketplaceService(db)
        listing = await svc.create_listing(account.id, "vehicle", "car_001", 10000.0)

        with pytest.raises(ValidationError, match="Cannot purchase your own listing"):
            await svc.purchase_listing(account.id, listing["id"])

    @pytest.mark.asyncio
    async def test_purchase_insufficient_cash(self, db: AsyncSession):
        seller_acct, _ = await _create_player_with_account(
            db, email="seller@test.com", cash=5000.0
        )
        buyer_acct, _ = await _create_player_with_account(
            db, email="buyer@test.com", cash=100.0
        )

        svc = MarketplaceService(db)
        listing = await svc.create_listing(seller_acct.id, "vehicle", "car_001", 10000.0)

        with pytest.raises(ValidationError, match="Insufficient cash"):
            await svc.purchase_listing(buyer_acct.id, listing["id"])

    @pytest.mark.asyncio
    async def test_purchase_sold_listing_fails(self, db: AsyncSession):
        seller_acct, _ = await _create_player_with_account(
            db, email="seller@test.com", cash=5000.0
        )
        buyer_acct, _ = await _create_player_with_account(
            db, email="buyer@test.com", cash=50000.0
        )
        buyer2_acct, _ = await _create_player_with_account(
            db, email="buyer2@test.com", cash=50000.0
        )

        svc = MarketplaceService(db)
        listing = await svc.create_listing(seller_acct.id, "vehicle", "car_001", 5000.0)
        await svc.purchase_listing(buyer_acct.id, listing["id"])

        with pytest.raises(ValidationError, match="Listing is no longer available"):
            await svc.purchase_listing(buyer2_acct.id, listing["id"])

    @pytest.mark.asyncio
    async def test_purchase_listing_not_found(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        with pytest.raises(NotFoundError, match="Listing not found"):
            await svc.purchase_listing(account.id, uuid.uuid4())


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11: MarketplaceService — Cancel Listing
# ══════════════════════════════════════════════════════════════════════════════


class TestMarketplaceServiceCancelListing:
    """Test cancelling marketplace listings."""

    @pytest.mark.asyncio
    async def test_cancel_listing(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        listing = await svc.create_listing(account.id, "vehicle", "car_001", 10000.0)

        result = await svc.cancel_listing(account.id, listing["id"])
        assert result["listing_status"] == "cancelled"
        assert result["message"] == "Listing cancelled successfully"

    @pytest.mark.asyncio
    async def test_cancel别人的_listing_fails(self, db: AsyncSession):
        seller_acct, _ = await _create_player_with_account(
            db, email="seller@test.com"
        )
        other_acct, _ = await _create_player_with_account(
            db, email="other@test.com"
        )

        svc = MarketplaceService(db)
        listing = await svc.create_listing(seller_acct.id, "vehicle", "car_001", 10000.0)

        with pytest.raises(ConflictError, match="only cancel your own"):
            await svc.cancel_listing(other_acct.id, listing["id"])

    @pytest.mark.asyncio
    async def test_cancel_sold_listing_fails(self, db: AsyncSession):
        seller_acct, _ = await _create_player_with_account(
            db, email="seller@test.com", cash=5000.0
        )
        buyer_acct, _ = await _create_player_with_account(
            db, email="buyer@test.com", cash=50000.0
        )

        svc = MarketplaceService(db)
        listing = await svc.create_listing(seller_acct.id, "vehicle", "car_001", 5000.0)
        await svc.purchase_listing(buyer_acct.id, listing["id"])

        with pytest.raises(ValidationError, match="Only active listings can be cancelled"):
            await svc.cancel_listing(seller_acct.id, listing["id"])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 12: MarketplaceService — Search & Filter
# ══════════════════════════════════════════════════════════════════════════════


class TestMarketplaceServiceSearch:
    """Test marketplace search and filtering."""

    @pytest.mark.asyncio
    async def test_get_active_listings(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        await svc.create_listing(account.id, "vehicle", "car_001", 5000.0)
        await svc.create_listing(account.id, "bike", "bike_001", 2000.0)

        listings = await svc.get_active_listings()
        assert len(listings) == 2

    @pytest.mark.asyncio
    async def test_get_active_listings_by_type(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        await svc.create_listing(account.id, "vehicle", "car_001", 5000.0)
        await svc.create_listing(account.id, "bike", "bike_001", 2000.0)
        await svc.create_listing(account.id, "vehicle", "car_002", 8000.0)

        vehicle_listings = await svc.get_active_listings(item_type="vehicle")
        assert len(vehicle_listings) == 2

        bike_listings = await svc.get_active_listings(item_type="bike")
        assert len(bike_listings) == 1

    @pytest.mark.asyncio
    async def test_get_active_listings_price_filter(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        await svc.create_listing(account.id, "vehicle", "car_001", 5000.0)
        await svc.create_listing(account.id, "vehicle", "car_002", 15000.0)
        await svc.create_listing(account.id, "vehicle", "car_003", 50000.0)

        cheap = await svc.get_active_listings(max_price=10000.0)
        assert len(cheap) == 1

        mid = await svc.get_active_listings(min_price=5000.0, max_price=20000.0)
        assert len(mid) == 2

    @pytest.mark.asyncio
    async def test_get_my_listings(self, db: AsyncSession):
        account1, _ = await _create_player_with_account(db, email="p1@test.com")
        account2, _ = await _create_player_with_account(db, email="p2@test.com")

        svc = MarketplaceService(db)
        await svc.create_listing(account1.id, "vehicle", "car_001", 5000.0)
        await svc.create_listing(account1.id, "vehicle", "car_002", 8000.0)
        await svc.create_listing(account2.id, "vehicle", "car_003", 3000.0)

        my_listings = await svc.get_my_listings(account1.id)
        assert len(my_listings) == 2

    @pytest.mark.asyncio
    async def test_get_listing(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        listing = await svc.create_listing(account.id, "vehicle", "car_001", 5000.0)

        result = await svc.get_listing(listing["id"])
        assert result["item_id"] == "car_001"

    @pytest.mark.asyncio
    async def test_get_listing_not_found(self, db: AsyncSession):
        svc = MarketplaceService(db)
        with pytest.raises(NotFoundError):
            await svc.get_listing(uuid.uuid4())


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 13: MarketplaceService — Cancelled Listing Not Shown
# ══════════════════════════════════════════════════════════════════════════════


class TestMarketplaceServiceListingLifecycle:
    """Test full listing lifecycle: create, buy/sell, cancel."""

    @pytest.mark.asyncio
    async def test_cancelled_listing_not_in_active(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = MarketplaceService(db)
        listing = await svc.create_listing(account.id, "vehicle", "car_001", 5000.0)
        await svc.cancel_listing(account.id, listing["id"])

        active = await svc.get_active_listings()
        assert len(active) == 0

    @pytest.mark.asyncio
    async def test_sold_listing_not_in_active(self, db: AsyncSession):
        seller_acct, _ = await _create_player_with_account(
            db, email="seller@test.com"
        )
        buyer_acct, _ = await _create_player_with_account(
            db, email="buyer@test.com", cash=50000.0
        )

        svc = MarketplaceService(db)
        listing = await svc.create_listing(seller_acct.id, "vehicle", "car_001", 5000.0)
        await svc.purchase_listing(buyer_acct.id, listing["id"])

        active = await svc.get_active_listings()
        assert len(active) == 0


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 14: Schema Validation Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestShopSchemas:
    """Test Pydantic schema validation."""

    def test_shop_buy_request_valid(self):
        from app.schemas.shop import ShopBuyRequest
        req = ShopBuyRequest(item_id="bike_001", quantity=1)
        assert req.item_id == "bike_001"
        assert req.quantity == 1

    def test_shop_buy_request_defaults(self):
        from app.schemas.shop import ShopBuyRequest
        req = ShopBuyRequest(item_id="bike_001")
        assert req.quantity == 1
        assert req.idempotency_key is None

    def test_shop_sell_request_valid(self):
        from app.schemas.shop import ShopSellRequest
        req = ShopSellRequest(item_id="bike_001", quantity=3)
        assert req.quantity == 3

    def test_marketplace_listing_create(self):
        from app.schemas.shop import MarketplaceListingCreate
        listing = MarketplaceListingCreate(
            item_type="vehicle", item_id="car_001", price=10000.0
        )
        assert listing.item_type == "vehicle"

    def test_marketplace_search_request_defaults(self):
        from app.schemas.shop import MarketplaceSearchRequest
        req = MarketplaceSearchRequest()
        assert req.sort_by == "created_at"
        assert req.sort_order == "desc"
        assert req.skip == 0
        assert req.limit == 50
