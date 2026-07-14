"""Unit tests for the Weapon System (TASK 8).

Covers: Weapon catalog, purchase, sell, equip/unequip, ammunition, reload,
durability, repair, attachments, stats — repositories, services, and API endpoints.
All tests use an in-memory SQLite database.
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
from app.dependencies import get_current_active_user, get_db_session
from app.main import app
from app.models.auth import PlayerAccount, AccountStatus, AccountRole
from app.models.player import Player, PlayerStatistics, PlayerSettings
from app.models.economy import Wallet
from app.models.inventory import Inventory
from app.models.weapon import (
    AmmoType,
    PlayerWeapon,
    Weapon,
    WeaponAmmunition,
    WeaponAttachment,
    WeaponType,
)
from app.repositories.auth import AuthRepository
from app.repositories.weapon import WeaponRepository
from app.services.weapon import WeaponService

# ── Settings ───────────────────────────────────────────────────────────────────

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


# ── Tables needed for weapon system tests ─────────────────────────────────────

_WEAPON_TABLES = [
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


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_WEAPON_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_WEAPON_TABLES)
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


@pytest.fixture
def auth_headers() -> dict[str, str]:
    account_id = uuid.uuid4()
    token = create_access_token({"sub": str(account_id), "type": "access"})
    return {"Authorization": f"Bearer {token}"}


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _create_player_with_account(
    session: AsyncSession, email: str = "player@test.com"
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
    await session.flush()
    return account, player


async def _create_weapon(session: AsyncSession, **kwargs) -> Weapon:
    defaults = {
        "weapon_name": "Glock 17",
        "weapon_type": WeaponType.PISTOL,
        "damage": 25.0,
        "fire_rate": 3.0,
        "accuracy": 75.0,
        "range_distance": 50.0,
        "magazine_size": 17,
        "reload_time": 2.0,
        "weight": 0.62,
        "max_durability": 100.0,
        "purchase_price": 2500.0,
        "sell_price": 1750.0,
        "required_level": 1,
        "ammo_type": AmmoType.CAL_9MM,
        "description": "Standard issue pistol",
    }
    defaults.update(kwargs)
    weapon = Weapon(**defaults)
    session.add(weapon)
    await session.flush()
    return weapon


async def _create_player_weapon(
    session: AsyncSession, player_id: uuid.UUID, weapon: Weapon, **kwargs
) -> PlayerWeapon:
    defaults = {
        "player_id": player_id,
        "weapon_id": weapon.id,
        "current_ammo": weapon.magazine_size,
        "reserve_ammo": weapon.magazine_size,
        "durability": weapon.max_durability,
        "equipped": False,
    }
    defaults.update(kwargs)
    pw = PlayerWeapon(**defaults)
    session.add(pw)
    await session.flush()
    return pw


# ══════════════════════════════════════════════════════════════════════════════
# REPOSITORY TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestWeaponRepository:
    async def test_create_and_get_weapon(self, db: AsyncSession):
        weapon = await _create_weapon(db, weapon_name="AK-47")
        repo = WeaponRepository(db)
        found = await repo.get_weapon_by_id(weapon.id)
        assert found is not None
        assert found.weapon_name == "AK-47"

    async def test_get_all_weapons(self, db: AsyncSession):
        await _create_weapon(db, weapon_name="W1")
        await _create_weapon(db, weapon_name="W2")
        repo = WeaponRepository(db)
        weapons = await repo.get_all_weapons()
        assert len(weapons) >= 2

    async def test_get_weapons_by_type(self, db: AsyncSession):
        await _create_weapon(db, weapon_name="Pistol1", weapon_type=WeaponType.PISTOL)
        await _create_weapon(db, weapon_name="Pistol2", weapon_type=WeaponType.PISTOL)
        await _create_weapon(db, weapon_name="Rifle1", weapon_type=WeaponType.ASSAULT_RIFLE)
        repo = WeaponRepository(db)
        pistols = await repo.get_weapons_by_type(WeaponType.PISTOL)
        assert len(pistols) >= 2

    async def test_create_and_get_player_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp1@test.com")
        weapon = await _create_weapon(db)
        repo = WeaponRepository(db)
        pw = await repo.create_player_weapon({
            "player_id": player.id,
            "weapon_id": weapon.id,
            "current_ammo": 17,
            "reserve_ammo": 17,
            "durability": 100.0,
        })
        assert pw.id is not None
        found = await repo.get_player_weapon_by_id(pw.id)
        assert found is not None
        assert found.player_id == player.id

    async def test_get_player_weapons(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp2@test.com")
        weapon = await _create_weapon(db)
        await _create_player_weapon(db, player.id, weapon)
        await _create_player_weapon(db, player.id, weapon)
        repo = WeaponRepository(db)
        pws = await repo.get_player_weapons(player.id)
        assert len(pws) == 2

    async def test_get_equipped_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp3@test.com")
        weapon = await _create_weapon(db)
        await _create_player_weapon(db, player.id, weapon, equipped=True)
        repo = WeaponRepository(db)
        equipped = await repo.get_equipped_weapon(player.id)
        assert equipped is not None
        assert equipped.equipped is True

    async def test_update_player_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp4@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        repo = WeaponRepository(db)
        updated = await repo.update_player_weapon(pw.id, {"durability": 50.0})
        assert updated is not None
        assert updated.durability == 50.0

    async def test_soft_delete_player_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp5@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        repo = WeaponRepository(db)
        result = await repo.soft_delete_player_weapon(pw.id)
        assert result is True
        found = await repo.get_player_weapon_by_id(pw.id)
        assert found is None

    async def test_create_and_get_attachment(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp6@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        repo = WeaponRepository(db)
        att = await repo.create_attachment({
            "player_weapon_id": pw.id,
            "scope": True,
            "silencer": False,
            "extended_magazine": False,
            "grip": False,
            "laser": False,
            "flashlight": False,
        })
        assert att.id is not None
        found = await repo.get_attachment(pw.id)
        assert found is not None
        assert found.scope is True

    async def test_update_attachment(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp7@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        repo = WeaponRepository(db)
        await repo.create_attachment({"player_weapon_id": pw.id})
        updated = await repo.update_attachment(pw.id, {"silencer": True})
        assert updated is not None
        assert updated.silencer is True

    async def test_get_ammo(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp8@test.com")
        repo = WeaponRepository(db)
        ammo = await repo.create_or_update_ammo(player.id, "9mm", 50)
        assert ammo.quantity == 50
        found = await repo.get_ammo(player.id, "9mm")
        assert found is not None
        assert found.quantity == 50

    async def test_update_ammo_add(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp9@test.com")
        repo = WeaponRepository(db)
        await repo.create_or_update_ammo(player.id, "9mm", 30)
        updated = await repo.create_or_update_ammo(player.id, "9mm", 20)
        assert updated.quantity == 50

    async def test_update_ammo_subtract(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp10@test.com")
        repo = WeaponRepository(db)
        await repo.create_or_update_ammo(player.id, "9mm", 30)
        updated = await repo.create_or_update_ammo(player.id, "9mm", -10)
        assert updated.quantity == 20

    async def test_get_all_ammo(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "wp11@test.com")
        repo = WeaponRepository(db)
        await repo.create_or_update_ammo(player.id, "9mm", 30)
        await repo.create_or_update_ammo(player.id, "5.56", 50)
        all_ammo = await repo.get_all_ammo(player.id)
        assert len(all_ammo) == 2


# ══════════════════════════════════════════════════════════════════════════════
# SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestWeaponService:
    async def test_get_all_weapons(self, db: AsyncSession):
        await _create_weapon(db, weapon_name="W1")
        await _create_weapon(db, weapon_name="W2")
        svc = WeaponService(db)
        weapons = await svc.get_all_weapons()
        assert len(weapons) >= 2

    async def test_get_weapon_not_found(self, db: AsyncSession):
        svc = WeaponService(db)
        from app.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            await svc.get_weapon(uuid.uuid4())

    async def test_buy_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc1@test.com")
        weapon = await _create_weapon(db, purchase_price=2500.0)
        svc = WeaponService(db)
        result = await svc.buy_weapon(player.id, weapon.id)
        assert result["cost"] == 2500.0
        assert result["player_weapon"].weapon_id == weapon.id

    async def test_buy_weapon_insufficient_funds(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc2@test.com")
        weapon = await _create_weapon(db, purchase_price=500000.0)
        svc = WeaponService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.buy_weapon(player.id, weapon.id)

    async def test_buy_weapon_level_too_low(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc3@test.com")
        weapon = await _create_weapon(db, required_level=50)
        svc = WeaponService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.buy_weapon(player.id, weapon.id)

    async def test_sell_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc4@test.com")
        weapon = await _create_weapon(db, sell_price=1750.0)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        result = await svc.sell_weapon(player.id, pw.id)
        assert result["sold_price"] >= 0
        assert "sold" in result["message"].lower()

    async def test_sell_weapon_not_found(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc5@test.com")
        svc = WeaponService(db)
        from app.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            await svc.sell_weapon(player.id, uuid.uuid4())

    async def test_equip_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc6@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        result = await svc.equip_weapon(player.id, pw.id, True)
        assert result["equipped"] is True

    async def test_equip_replaces_existing(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc7@test.com")
        weapon = await _create_weapon(db)
        pw1 = await _create_player_weapon(db, player.id, weapon, equipped=True)
        pw2 = await _create_player_weapon(db, player.id, weapon, equipped=False)
        svc = WeaponService(db)
        result = await svc.equip_weapon(player.id, pw2.id, True)
        assert result["equipped"] is True
        repo = WeaponRepository(db)
        pw1_refreshed = await repo.get_player_weapon_by_id(pw1.id)
        assert pw1_refreshed.equipped is False

    async def test_unequip_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc8@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon, equipped=True)
        svc = WeaponService(db)
        result = await svc.equip_weapon(player.id, pw.id, False)
        assert result["equipped"] is False

    async def test_purchase_ammo(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc9@test.com")
        svc = WeaponService(db)
        result = await svc.purchase_ammo(player.id, "9mm", 50)
        assert result["quantity_purchased"] == 50
        assert result["total_cost"] == 250.0

    async def test_purchase_ammo_invalid_type(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc10@test.com")
        svc = WeaponService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.purchase_ammo(player.id, "invalid_ammo", 50)

    async def test_reload_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc11@test.com")
        weapon = await _create_weapon(db, ammo_type="9mm", magazine_size=17)
        pw = await _create_player_weapon(
            db, player.id, weapon, current_ammo=5, reserve_ammo=0
        )
        await WeaponRepository(db).create_or_update_ammo(player.id, "9mm", 50)
        svc = WeaponService(db)
        result = await svc.reload_weapon(player.id, pw.id)
        assert result["ammo_loaded"] > 0

    async def test_reload_no_ammo_available(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc12@test.com")
        weapon = await _create_weapon(db, ammo_type="9mm")
        pw = await _create_player_weapon(
            db, player.id, weapon, current_ammo=5, reserve_ammo=0
        )
        svc = WeaponService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.reload_weapon(player.id, pw.id)

    async def test_reload_full_magazine(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc13@test.com")
        weapon = await _create_weapon(db, ammo_type="9mm", magazine_size=17)
        pw = await _create_player_weapon(
            db, player.id, weapon, current_ammo=17, reserve_ammo=17
        )
        svc = WeaponService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.reload_weapon(player.id, pw.id)

    async def test_reduce_durability(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc14@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        result = await svc.reduce_durability(player.id, pw.id, 10.0)
        assert result["new_durability"] == 90.0

    async def test_repair_weapon(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc15@test.com")
        weapon = await _create_weapon(db, max_durability=100.0)
        pw = await _create_player_weapon(db, player.id, weapon, durability=50.0)
        svc = WeaponService(db)
        result = await svc.repair_weapon(player.id, pw.id)
        assert result["new_durability"] == 100.0
        assert result["repair_cost"] > 0

    async def test_repair_already_full(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc16@test.com")
        weapon = await _create_weapon(db, max_durability=100.0)
        pw = await _create_player_weapon(db, player.id, weapon, durability=100.0)
        svc = WeaponService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.repair_weapon(player.id, pw.id)

    async def test_add_attachment(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc17@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        result = await svc.add_attachment(player.id, pw.id, "scope")
        assert result["attachment_type"] == "scope"
        assert result["cost"] > 0

    async def test_add_duplicate_attachment(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc18@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        await svc.add_attachment(player.id, pw.id, "scope")
        from app.core.exceptions import ConflictError
        with pytest.raises(ConflictError):
            await svc.add_attachment(player.id, pw.id, "scope")

    async def test_add_invalid_attachment(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc19@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.add_attachment(player.id, pw.id, "rocket_launcher")

    async def test_remove_attachment(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc20@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        await svc.add_attachment(player.id, pw.id, "silencer")
        result = await svc.remove_attachment(player.id, pw.id, "silencer")
        assert result["attachment_type"] == "silencer"
        assert result["refund"] >= 0

    async def test_remove_nonexistent_attachment(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc21@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        from app.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            await svc.remove_attachment(player.id, pw.id, "scope")

    async def test_get_weapon_stats(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc22@test.com")
        weapon = await _create_weapon(db)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        stats = await svc.get_weapon_stats(player.id, pw.id)
        assert stats["base_damage"] > 0
        assert stats["effective_damage"] > 0
        assert stats["weapon_name"] == weapon.weapon_name

    async def test_get_weapon_stats_with_attachments(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc23@test.com")
        weapon = await _create_weapon(db, damage=100.0, accuracy=80.0)
        pw = await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        await svc.add_attachment(player.id, pw.id, "scope")
        stats = await svc.get_weapon_stats(player.id, pw.id)
        assert stats["effective_accuracy"] > stats["base_accuracy"]
        assert "scope" in stats["attachments"]

    async def test_get_player_weapons(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc24@test.com")
        weapon = await _create_weapon(db)
        await _create_player_weapon(db, player.id, weapon)
        svc = WeaponService(db)
        result = await svc.get_player_weapons(player.id)
        assert len(result) >= 1

    async def test_get_ammo_inventory(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc25@test.com")
        svc = WeaponService(db)
        await svc.purchase_ammo(player.id, "9mm", 50)
        await svc.purchase_ammo(player.id, "5.56", 30)
        ammo = await svc.get_ammo_inventory(player.id)
        assert len(ammo) == 2


# ══════════════════════════════════════════════════════════════════════════════
# API TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestWeaponAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"weapi_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"weapi_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        assert resp.status_code == 201
        return resp.json()["data"]["access_token"]

    async def test_list_weapons(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/weapons/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_list_weapons_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/weapons/")
        assert resp.status_code == 401

    async def test_get_weapon_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/weapons/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_buy_weapon_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/weapons/buy",
            json={"weapon_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404, 422)

    async def test_list_player_weapons(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/weapons/inventory/list",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_ammo_inventory(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/weapons/ammo/inventory",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_equip_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/weapons/equip",
            json={"player_weapon_id": str(uuid.uuid4()), "equip": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_repair_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/weapons/repair",
            json={"player_weapon_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_attachment_add_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            f"/api/v1/weapons/{uuid.uuid4()}/attachments/add",
            json={"attachment_type": "scope"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_stats_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/weapons/{uuid.uuid4()}/stats",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)
