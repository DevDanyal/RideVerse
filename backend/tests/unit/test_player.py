"""Unit tests for the Core Player System (TASK 4).

Covers: Player profile, statistics, settings, characters, inventory, wallet,
achievements, bank accounts — repositories, services, and API endpoints.
All tests use an in-memory SQLite database.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.core.security import create_access_token, get_password_hash
from app.database.base import Base
from app.dependencies import get_current_active_user, get_db_session
from app.main import app
from app.models.auth import PlayerAccount, AccountRole, AccountStatus
from app.models.player import Player, PlayerStatistics, PlayerSettings
from app.models.character import Character, CharacterAppearance
from app.models.inventory import Inventory, InventoryItem
from app.models.economy import Wallet
from app.models.achievement import Achievement, PlayerAchievement
from app.models.bank import BankAccount, AccountType
from app.repositories.auth import AuthRepository
from app.repositories.player import PlayerRepository
from app.repositories.character import CharacterRepository
from app.repositories.inventory import InventoryRepository
from app.repositories.economy import EconomyRepository
from app.repositories.achievement import AchievementRepository
from app.repositories.bank import BankAccountRepository

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


# ── Tables needed for player system tests ─────────────────────────────────────

_PLAYER_TABLES = [
    Base.metadata.tables[name]
    for name in (
        "player_accounts",
        "player_sessions",
        "refresh_tokens",
        "players",
        "player_statistics",
        "player_settings",
        "characters",
        "character_appearances",
        "inventories",
        "inventory_items",
        "wallets",
        "achievements",
        "player_achievements",
        "bank_accounts",
        "garages",
        "garage_slots",
    )
    if name in Base.metadata.tables
]


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_PLAYER_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_PLAYER_TABLES)
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
    """Return valid Bearer headers for a test user."""
    account_id = uuid.uuid4()
    token = create_access_token({"sub": str(account_id), "type": "access"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers() -> dict[str, str]:
    """Return valid Bearer headers for a different test user."""
    account_id = uuid.uuid4()
    token = create_access_token({"sub": str(account_id), "type": "access"})
    return {"Authorization": f"Bearer {token}"}


async def _create_player_with_account(
    session: AsyncSession, email: str = "player@test.com"
) -> tuple[PlayerAccount, Player]:
    """Helper: create an account + player, stats, settings, wallet."""
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
        cash=1000.0,
    )
    session.add(player)
    await session.flush()

    stats = PlayerStatistics(player_id=player.id)
    session.add(stats)

    settings = PlayerSettings(player_id=player.id)
    session.add(settings)

    wallet = Wallet(player_id=player.id, cash=1000.0, bank_balance=0.0)
    session.add(wallet)

    inventory = Inventory(player_id=player.id, max_slots=50, used_slots=0, total_weight=0.0)
    session.add(inventory)

    await session.flush()

    return account, player


# ── Repository Tests ──────────────────────────────────────────────────────────


class TestPlayerRepository:
    async def test_get_by_account_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        found = await repo.get_by_account_id(account.id)
        assert found is not None
        assert found.id == player.id
        assert found.display_name == player.display_name

    async def test_get_by_account_id_not_found(self, db: AsyncSession):
        repo = PlayerRepository(db)
        found = await repo.get_by_account_id(uuid.uuid4())
        assert found is None

    async def test_get_by_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        found = await repo.get_by_id(player.id)
        assert found is not None
        assert found.account_id == account.id

    async def test_update_player(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        updated = await repo.update(player.id, display_name="NewName")
        assert updated is not None
        assert updated.display_name == "NewName"

    async def test_get_statistics(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        stats = await repo.get_statistics(player.id)
        assert stats is not None
        assert stats.player_id == player.id
        assert stats.total_play_time == 0.0

    async def test_get_settings(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        settings = await repo.get_settings(player.id)
        assert settings is not None
        assert settings.language == "en"

    async def test_update_settings(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        updated = await repo.update_settings(player.id, language="es")
        assert updated is not None
        assert updated.language == "es"


class TestCharacterRepository:
    async def test_get_all_by_player_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        char = Character(
            player_id=player.id,
            first_name="John",
            last_name="Doe",
            gender="male",
            height=1.8,
            weight=80.0,
        )
        db.add(char)
        await db.flush()

        repo = CharacterRepository(db)
        chars = await repo.get_all_by_player_id(player.id)
        assert len(chars) == 1
        assert chars[0].first_name == "John"

    async def test_get_by_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        char = Character(
            player_id=player.id,
            first_name="Jane",
            last_name="Smith",
            gender="female",
            height=1.65,
            weight=60.0,
        )
        db.add(char)
        await db.flush()

        repo = CharacterRepository(db)
        found = await repo.get_by_id(char.id)
        assert found is not None
        assert found.first_name == "Jane"

    async def test_update_character(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        char = Character(
            player_id=player.id,
            first_name="Bob",
            last_name="Builder",
            gender="male",
            height=1.75,
            weight=85.0,
        )
        db.add(char)
        await db.flush()

        repo = CharacterRepository(db)
        updated = await repo.update(char.id, first_name="Bobby")
        assert updated is not None
        assert updated.first_name == "Bobby"

    async def test_update_appearance(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        char = Character(
            player_id=player.id,
            first_name="Alice",
            last_name="Wonder",
            gender="female",
            height=1.6,
            weight=55.0,
        )
        db.add(char)
        await db.flush()

        appearance = CharacterAppearance(
            character_id=char.id,
            hair_style="long",
            hair_color="blonde",
        )
        db.add(appearance)
        await db.flush()

        repo = CharacterRepository(db)
        updated = await repo.update_appearance(char.id, hair_color="red")
        assert updated is not None
        assert updated.hair_color == "red"


class TestInventoryRepository:
    async def test_get_by_player_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = InventoryRepository(db)
        inv = await repo.get_by_player_id(player.id)
        assert inv is not None
        assert inv.player_id == player.id

    async def test_get_items(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        inv_repo = InventoryRepository(db)
        inv = await inv_repo.get_by_player_id(player.id)

        from app.models.inventory import ItemType, ItemRarity
        item = InventoryItem(
            inventory_id=inv.id,
            item_id="sword_001",
            item_name="Iron Sword",
            item_type=ItemType.WEAPON,
            quantity=1,
            rarity=ItemRarity.COMMON,
            weight=3.5,
            stackable=False,
        )
        db.add(item)
        await db.flush()

        items = await inv_repo.get_items(inv.id)
        assert len(items) == 1
        assert items[0].item_name == "Iron Sword"


class TestEconomyRepository:
    async def test_get_wallet(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = EconomyRepository(db)
        wallet = await repo.get_wallet(player.id)
        assert wallet is not None
        assert wallet.cash == 1000.0

    async def test_get_wallet_not_found(self, db: AsyncSession):
        repo = EconomyRepository(db)
        wallet = await repo.get_wallet(uuid.uuid4())
        assert wallet is None


class TestAchievementRepository:
    async def test_get_player_achievements_empty(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = AchievementRepository(db)
        achievements = await repo.get_player_achievements(player.id)
        assert achievements == []

    async def test_get_player_achievements_with_data(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        ach = Achievement(
            achievement_name="First Blood",
            description="Get your first kill",
            reward={"cash": 500},
        )
        db.add(ach)
        await db.flush()

        pa = PlayerAchievement(
            player_id=player.id,
            achievement_id=ach.id,
            unlocked_at=datetime.now(timezone.utc),
        )
        db.add(pa)
        await db.flush()

        repo = AchievementRepository(db)
        achievements = await repo.get_player_achievements(player.id)
        assert len(achievements) == 1


class TestBankAccountRepository:
    async def test_get_by_player_id_empty(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        repo = BankAccountRepository(db)
        accounts = await repo.get_by_player_id(player.id)
        assert accounts == []

    async def test_get_by_player_id_with_accounts(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        ba = BankAccount(
            player_id=player.id,
            account_number="1234567890",
            account_type=AccountType.CHECKING,
            balance=5000.0,
        )
        db.add(ba)
        await db.flush()

        repo = BankAccountRepository(db)
        accounts = await repo.get_by_player_id(player.id)
        assert len(accounts) == 1
        assert accounts[0].balance == 5000.0


# ── Service Tests ──────────────────────────────────────────────────────────────


class TestPlayerService:
    async def test_get_profile(self, db: AsyncSession):
        from app.services.player import PlayerService

        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        svc = PlayerService(repo)

        profile = await svc.get_profile(account.id)
        assert profile["display_name"] == player.display_name
        assert profile["cash"] == 1000.0

    async def test_get_profile_not_found(self, db: AsyncSession):
        from app.services.player import PlayerService
        from app.core.exceptions import NotFoundError

        repo = PlayerRepository(db)
        svc = PlayerService(repo)

        with pytest.raises(NotFoundError):
            await svc.get_profile(uuid.uuid4())

    async def test_update_profile(self, db: AsyncSession):
        from app.services.player import PlayerService

        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        svc = PlayerService(repo)

        updated = await svc.update_profile(account.id, display_name="UpdatedName")
        assert updated["display_name"] == "UpdatedName"

    async def test_get_statistics(self, db: AsyncSession):
        from app.services.player import PlayerService

        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        svc = PlayerService(repo)

        stats = await svc.get_statistics(account.id)
        assert stats["total_play_time"] == 0.0

    async def test_get_settings(self, db: AsyncSession):
        from app.services.player import PlayerService

        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        svc = PlayerService(repo)

        settings = await svc.get_settings(account.id)
        assert settings["language"] == "en"

    async def test_update_settings(self, db: AsyncSession):
        from app.services.player import PlayerService

        account, player = await _create_player_with_account(db)
        repo = PlayerRepository(db)
        svc = PlayerService(repo)

        updated = await svc.update_settings(account.id, language="fr")
        assert updated["language"] == "fr"


class TestCharacterService:
    async def _setup(self, db):
        from app.services.character import CharacterService

        account, player = await _create_player_with_account(db)
        char_repo = CharacterRepository(db)
        player_repo = PlayerRepository(db)
        svc = CharacterService(player_repo, char_repo)
        return account, player, svc

    async def test_get_characters_empty(self, db: AsyncSession):
        account, player, svc = await self._setup(db)
        chars = await svc.get_characters(account.id)
        assert chars == []

    async def test_get_characters_with_data(self, db: AsyncSession):
        account, player, svc = await self._setup(db)

        char = Character(
            player_id=player.id,
            first_name="John",
            last_name="Doe",
            gender="male",
            height=1.8,
            weight=80.0,
        )
        db.add(char)
        await db.flush()

        chars = await svc.get_characters(account.id)
        assert len(chars) == 1
        assert chars[0]["first_name"] == "John"

    async def test_get_character_ownership_check(self, db: AsyncSession):
        from app.core.exceptions import NotFoundError

        account, player, svc = await self._setup(db)

        # Create a character for another player
        other_account, other_player = await _create_player_with_account(db, "other@test.com")
        other_char = Character(
            player_id=other_player.id,
            first_name="Other",
            last_name="Guy",
            gender="male",
            height=1.7,
            weight=70.0,
        )
        db.add(other_char)
        await db.flush()

        with pytest.raises(NotFoundError):
            await svc.get_character(account.id, other_char.id)

    async def test_update_character(self, db: AsyncSession):
        account, player, svc = await self._setup(db)

        char = Character(
            player_id=player.id,
            first_name="Bob",
            last_name="Builder",
            gender="male",
            height=1.75,
            weight=85.0,
        )
        db.add(char)
        await db.flush()

        updated = await svc.update_character(account.id, char.id, first_name="Bobby")
        assert updated["first_name"] == "Bobby"

    async def test_update_appearance(self, db: AsyncSession):
        account, player, svc = await self._setup(db)

        char = Character(
            player_id=player.id,
            first_name="Alice",
            last_name="Wonder",
            gender="female",
            height=1.6,
            weight=55.0,
        )
        db.add(char)
        await db.flush()

        appearance = CharacterAppearance(
            character_id=char.id,
            hair_style="long",
            hair_color="blonde",
        )
        db.add(appearance)
        await db.flush()

        updated = await svc.update_appearance(
            account.id, char.id, hair_color="red"
        )
        assert updated["hair_color"] == "red"


class TestInventoryService:
    async def test_get_inventory(self, db: AsyncSession):
        from app.services.inventory import InventoryService

        account, player = await _create_player_with_account(db)
        player_repo = PlayerRepository(db)
        inv_repo = InventoryRepository(db)
        svc = InventoryService(player_repo, inv_repo)

        inventory = await svc.get_inventory(account.id)
        assert inventory["player_id"] == player.id
        assert inventory["max_slots"] == 50

    async def test_get_inventory_not_found(self, db: AsyncSession):
        from app.services.inventory import InventoryService
        from app.core.exceptions import NotFoundError

        player_repo = PlayerRepository(db)
        inv_repo = InventoryRepository(db)
        svc = InventoryService(player_repo, inv_repo)

        with pytest.raises(NotFoundError):
            await svc.get_inventory(uuid.uuid4())


class TestEconomyService:
    async def test_get_wallet(self, db: AsyncSession):
        from app.services.economy import EconomyService

        account, player = await _create_player_with_account(db)
        svc = EconomyService(db)

        wallet = await svc.get_wallet(account.id)
        assert wallet["cash"] == 1000.0

    async def test_get_wallet_not_found(self, db: AsyncSession):
        from app.services.economy import EconomyService
        from app.core.exceptions import NotFoundError

        svc = EconomyService(db)

        with pytest.raises(NotFoundError):
            await svc.get_wallet(uuid.uuid4())


class TestAchievementService:
    async def test_get_achievements_empty(self, db: AsyncSession):
        from app.services.achievement import AchievementService

        account, player = await _create_player_with_account(db)
        player_repo = PlayerRepository(db)
        ach_repo = AchievementRepository(db)
        svc = AchievementService(player_repo, ach_repo)

        achievements = await svc.get_player_achievements(account.id)
        assert achievements == []


class TestBankAccountService:
    async def test_get_accounts_empty(self, db: AsyncSession):
        from app.services.bank import BankAccountService

        account, player = await _create_player_with_account(db)
        svc = BankAccountService(db)

        accounts = await svc.get_accounts(account.id)
        assert accounts == []


# ── API Endpoint Tests ─────────────────────────────────────────────────────────


class TestPlayerProfileAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"api_player_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"api_player_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_get_profile_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["display_name"] is not None
        assert data["data"]["level"] == 1
        assert data["data"]["cash"] == 1000.0

    async def test_get_profile_no_token_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/players/me")
        assert resp.status_code == 401

    async def test_update_profile_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.patch(
            "/api/v1/players/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"display_name": "UpdatedName"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["display_name"] == "UpdatedName"


class TestPlayerStatisticsAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"stats_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"stats_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_get_statistics_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/statistics",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["total_play_time"] == 0.0


class TestPlayerSettingsAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"settings_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"settings_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_get_settings_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/settings",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["language"] == "en"

    async def test_update_settings_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.patch(
            "/api/v1/players/me/settings",
            headers={"Authorization": f"Bearer {token}"},
            json={"language": "es", "theme": "light"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["language"] == "es"
        assert resp.json()["data"]["theme"] == "light"


class TestCharacterAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"char_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"char_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_list_characters_empty(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/characters",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"] == []


class TestInventoryAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"inv_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"inv_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_get_inventory_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/inventory",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["max_slots"] == 50


class TestEconomyAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"econ_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"econ_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_get_wallet_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/economy/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["cash"] == 1000.0


class TestAchievementAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"ach_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"ach_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_get_achievements_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/achievements",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"] == []


class TestBankAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"bank_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"bank_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_get_bank_accounts_returns_200(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/bank",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"] == []
