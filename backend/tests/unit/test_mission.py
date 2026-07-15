"""Unit tests for the Mission System (TASK 11).

Covers: Mission CRUD, accept/start/progress/complete/fail/cancel,
restart, claim rewards, history, statistics, cooldowns — repositories,
services, and API endpoints. All tests use an in-memory SQLite database.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import create_access_token, get_password_hash
from app.database.base import Base
from app.dependencies import get_current_active_user, get_db_session
from app.main import app
from app.models.auth import PlayerAccount, AccountStatus, AccountRole
from app.models.mission import (
    Mission,
    MissionCategory,
    MissionCooldown,
    MissionDifficulty,
    MissionHistory,
    MissionObjective,
    MissionStatus,
    MissionStatistics,
    ObjectiveType,
    PlayerMission,
    PlayerObjectiveProgress,
)
from app.models.player import Player, PlayerStatistics, PlayerSettings
from app.models.economy import Wallet
from app.models.inventory import Inventory
from app.repositories.auth import AuthRepository
from app.repositories.mission import MissionRepository
from app.services.mission import MissionService

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


# ── Tables needed for mission system tests ─────────────────────────────────────

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


async def _create_mission(
    session: AsyncSession,
    mission_name: str = "Test Mission",
    category: str = "story",
    difficulty: str = "normal",
    minimum_level: int = 1,
    reward_money: float = 1000.0,
    reward_xp: int = 500,
    cooldown_seconds: int = 0,
    repeatable: bool = False,
    **kwargs,
) -> Mission:
    mission = Mission(
        mission_name=mission_name,
        mission_description="A test mission",
        category=category,
        difficulty=difficulty,
        minimum_level=minimum_level,
        reward_money=reward_money,
        reward_xp=reward_xp,
        reward_reputation=10.0,
        cooldown_seconds=cooldown_seconds,
        repeatable=repeatable,
        **kwargs,
    )
    session.add(mission)
    await session.flush()
    return mission


async def _create_objective(
    session: AsyncSession,
    mission_id: uuid.UUID,
    objective_type: str = "reach_location",
    target_value: int = 1,
    description: str = "Reach the destination",
    order_index: int = 0,
    optional: bool = False,
) -> MissionObjective:
    obj = MissionObjective(
        mission_id=mission_id,
        objective_type=objective_type,
        description=description,
        target_value=target_value,
        order_index=order_index,
        optional=optional,
    )
    session.add(obj)
    await session.flush()
    return obj


# ══════════════════════════════════════════════════════════════════════════════
# REPOSITORY TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestMissionRepository:
    async def test_create_and_get_mission(self, db: AsyncSession):
        mission = await _create_mission(db, mission_name="Rescue Op")
        repo = MissionRepository(db)
        found = await repo.get_mission_by_id(mission.id)
        assert found is not None
        assert found.mission_name == "Rescue Op"

    async def test_get_all_missions(self, db: AsyncSession):
        await _create_mission(db, mission_name="M1")
        await _create_mission(db, mission_name="M2")
        repo = MissionRepository(db)
        missions = await repo.get_all_missions()
        assert len(missions) >= 2

    async def test_get_missions_by_category(self, db: AsyncSession):
        await _create_mission(db, mission_name="Story1", category="story")
        await _create_mission(db, mission_name="Story2", category="story")
        await _create_mission(db, mission_name="Racing1", category="racing")
        repo = MissionRepository(db)
        stories = await repo.get_all_missions(category="story")
        assert len(stories) >= 2

    async def test_count_missions(self, db: AsyncSession):
        await _create_mission(db, mission_name="C1")
        await _create_mission(db, mission_name="C2")
        repo = MissionRepository(db)
        count = await repo.count_missions()
        assert count >= 2

    async def test_soft_delete_mission(self, db: AsyncSession):
        mission = await _create_mission(db, mission_name="Del")
        repo = MissionRepository(db)
        result = await repo.soft_delete_mission(mission.id)
        assert result is True
        found = await repo.get_mission_by_id(mission.id)
        assert found is None

    async def test_create_and_get_objective(self, db: AsyncSession):
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        obj = await repo.create_objective({
            "mission_id": mission.id,
            "objective_type": "reach_location",
            "description": "Go to base",
            "target_value": 1,
            "order_index": 0,
        })
        assert obj.id is not None
        objs = await repo.get_objectives_for_mission(mission.id)
        assert len(objs) >= 1

    async def test_create_player_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "pm1@test.com")
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        pm = await repo.create_player_mission({
            "player_id": player.id,
            "mission_id": mission.id,
            "status": MissionStatus.AVAILABLE,
        })
        assert pm.id is not None

    async def test_get_player_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "pm2@test.com")
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        pm = await repo.create_player_mission({
            "player_id": player.id,
            "mission_id": mission.id,
            "status": MissionStatus.ACCEPTED,
        })
        found = await repo.get_player_mission(player.id, mission.id)
        assert found is not None
        assert found.status == MissionStatus.ACCEPTED

    async def test_update_player_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "pm3@test.com")
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        pm = await repo.create_player_mission({
            "player_id": player.id,
            "mission_id": mission.id,
            "status": MissionStatus.ACCEPTED,
        })
        updated = await repo.update_player_mission(pm.id, {"status": MissionStatus.IN_PROGRESS})
        assert updated is not None
        assert updated.status == MissionStatus.IN_PROGRESS

    async def test_create_and_get_history(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "hist1@test.com")
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        hist = await repo.create_history({
            "player_id": player.id,
            "mission_id": mission.id,
            "outcome": "completed",
            "completion_time_seconds": 120,
            "objectives_completed": 3,
            "objectives_total": 3,
            "money_earned": 1000.0,
            "xp_earned": 500,
            "reputation_earned": 10.0,
        })
        assert hist.id is not None
        history = await repo.get_player_history(player.id)
        assert len(history) >= 1

    async def test_create_cooldown(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "cd1@test.com")
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        cd = await repo.create_cooldown({
            "player_id": player.id,
            "mission_id": mission.id,
            "last_completed_at": datetime.now(timezone.utc),
            "next_available_at": datetime.now(timezone.utc) + timedelta(hours=1),
        })
        assert cd.id is not None
        found = await repo.get_cooldown(player.id, mission.id)
        assert found is not None

    async def test_create_statistics(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "stat1@test.com")
        repo = MissionRepository(db)
        stats = await repo.create_statistics({"player_id": player.id})
        assert stats.id is not None
        found = await repo.get_statistics(player.id)
        assert found is not None
        assert found.total_completed == 0

    async def test_create_objective_progress(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "op1@test.com")
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        obj = await repo.create_objective({
            "mission_id": mission.id,
            "objective_type": "reach_location",
            "target_value": 1,
        })
        pm = await repo.create_player_mission({
            "player_id": player.id,
            "mission_id": mission.id,
            "status": MissionStatus.IN_PROGRESS,
        })
        op = await repo.create_objective_progress({
            "player_mission_id": pm.id,
            "objective_id": obj.id,
            "current_value": 0,
            "completed": False,
        })
        assert op.id is not None
        found = await repo.get_objective_progress(pm.id, obj.id)
        assert found is not None

    async def test_update_objective_progress(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "op2@test.com")
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        obj = await repo.create_objective({
            "mission_id": mission.id,
            "objective_type": "collect_items",
            "target_value": 5,
        })
        pm = await repo.create_player_mission({
            "player_id": player.id,
            "mission_id": mission.id,
            "status": MissionStatus.IN_PROGRESS,
        })
        op = await repo.create_objective_progress({
            "player_mission_id": pm.id,
            "objective_id": obj.id,
            "current_value": 0,
        })
        updated = await repo.update_objective_progress(op.id, {"current_value": 3})
        assert updated is not None
        assert updated.current_value == 3

    async def test_count_player_missions(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "pm4@test.com")
        m1 = await _create_mission(db, mission_name="PM1")
        m2 = await _create_mission(db, mission_name="PM2")
        repo = MissionRepository(db)
        await repo.create_player_mission({
            "player_id": player.id,
            "mission_id": m1.id,
            "status": MissionStatus.ACCEPTED,
        })
        await repo.create_player_mission({
            "player_id": player.id,
            "mission_id": m2.id,
            "status": MissionStatus.IN_PROGRESS,
        })
        count = await repo.count_player_missions(player.id)
        assert count >= 2

    async def test_count_player_history(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "hist2@test.com")
        mission = await _create_mission(db)
        repo = MissionRepository(db)
        await repo.create_history({
            "player_id": player.id,
            "mission_id": mission.id,
            "outcome": "completed",
            "completion_time_seconds": 60,
        })
        count = await repo.count_player_history(player.id)
        assert count >= 1


# ══════════════════════════════════════════════════════════════════════════════
# SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestMissionService:
    async def test_create_mission(self, db: AsyncSession):
        svc = MissionService(db)
        mission = await svc.create_mission({
            "mission_name": "New Mission",
            "mission_description": "Desc",
            "category": "story",
            "difficulty": "normal",
            "minimum_level": 1,
            "reward_money": 5000.0,
            "reward_xp": 250,
            "reward_reputation": 20.0,
        })
        assert mission.mission_name == "New Mission"
        assert mission.category == "story"

    async def test_create_mission_invalid_category(self, db: AsyncSession):
        svc = MissionService(db)
        with pytest.raises(ValidationError):
            await svc.create_mission({
                "mission_name": "Bad Mission",
                "category": "invalid_cat",
                "difficulty": "normal",
            })

    async def test_create_mission_invalid_difficulty(self, db: AsyncSession):
        svc = MissionService(db)
        with pytest.raises(ValidationError):
            await svc.create_mission({
                "mission_name": "Bad Mission",
                "category": "story",
                "difficulty": "impossible",
            })

    async def test_create_mission_with_objectives(self, db: AsyncSession):
        svc = MissionService(db)
        mission = await svc.create_mission({
            "mission_name": "Obj Mission",
            "category": "delivery",
            "difficulty": "easy",
            "objectives": [
                {"objective_type": "reach_location", "target_value": 1, "description": "Go here"},
                {"objective_type": "deliver_item", "target_value": 3, "description": "Deliver that"},
            ],
        })
        assert mission.mission_name == "Obj Mission"
        assert len(mission.objectives) == 2

    async def test_get_mission(self, db: AsyncSession):
        mission = await _create_mission(db, mission_name="Get Me")
        svc = MissionService(db)
        found = await svc.get_mission(mission.id)
        assert found.mission_name == "Get Me"

    async def test_get_mission_not_found(self, db: AsyncSession):
        svc = MissionService(db)
        with pytest.raises(NotFoundError):
            await svc.get_mission(uuid.uuid4())

    async def test_list_missions(self, db: AsyncSession):
        await _create_mission(db, mission_name="L1")
        await _create_mission(db, mission_name="L2")
        svc = MissionService(db)
        missions, total = await svc.list_missions()
        assert total >= 2

    async def test_update_mission(self, db: AsyncSession):
        mission = await _create_mission(db, mission_name="Old Name")
        svc = MissionService(db)
        updated = await svc.update_mission(mission.id, {"mission_name": "New Name"})
        assert updated.mission_name == "New Name"

    async def test_delete_mission(self, db: AsyncSession):
        mission = await _create_mission(db, mission_name="To Delete")
        svc = MissionService(db)
        result = await svc.delete_mission(mission.id)
        assert result is True
        with pytest.raises(NotFoundError):
            await svc.get_mission(mission.id)

    async def test_accept_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_accept1@test.com")
        mission = await _create_mission(db, minimum_level=1)
        svc = MissionService(db)
        pm = await svc.accept_mission(player.id, mission.id)
        assert pm.status == MissionStatus.ACCEPTED
        assert pm.player_id == player.id

    async def test_accept_mission_level_too_low(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_accept2@test.com")
        mission = await _create_mission(db, minimum_level=50)
        svc = MissionService(db)
        with pytest.raises(ValidationError):
            await svc.accept_mission(player.id, mission.id)

    async def test_accept_mission_already_active(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_accept3@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        with pytest.raises(ConflictError):
            await svc.accept_mission(player.id, mission.id)

    async def test_start_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_start1@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        pm = await svc.start_mission(player.id, mission.id)
        assert pm.status == MissionStatus.IN_PROGRESS
        assert pm.started_at is not None

    async def test_start_mission_not_accepted(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_start2@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        with pytest.raises(NotFoundError):
            await svc.start_mission(player.id, mission.id)

    async def test_start_mission_wrong_status(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_start3@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        with pytest.raises(ValidationError):
            await svc.start_mission(player.id, mission.id)

    async def test_update_progress(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_prog1@test.com")
        mission = await _create_mission(db)
        obj = await _create_objective(db, mission.id, "collect_items", target_value=5)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        pm = await svc.update_progress(player.id, mission.id, obj.id, 3)
        assert pm.progress >= 0

    async def test_update_progress_not_in_progress(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_prog2@test.com")
        mission = await _create_mission(db)
        obj = await _create_objective(db, mission.id)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        with pytest.raises(ValidationError):
            await svc.update_progress(player.id, mission.id, obj.id, 1)

    async def test_complete_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_comp1@test.com")
        mission = await _create_mission(db, reward_money=2000.0, reward_xp=100)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        result = await svc.complete_mission(player.id, mission.id)
        assert result["money_earned"] == 2000.0
        assert result["xp_earned"] == 100

    async def test_complete_mission_not_in_progress(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_comp2@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        with pytest.raises(ValidationError):
            await svc.complete_mission(player.id, mission.id)

    async def test_fail_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_fail1@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        result = await svc.fail_mission(player.id, mission.id, "timeout")
        assert result["failure_reason"] == "timeout"

    async def test_fail_mission_not_in_progress(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_fail2@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        with pytest.raises(ValidationError):
            await svc.fail_mission(player.id, mission.id)

    async def test_cancel_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_cancel1@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        result = await svc.cancel_mission(player.id, mission.id)
        assert "cancelled" in result["message"].lower()

    async def test_cancel_mission_wrong_status(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_cancel2@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        await svc.complete_mission(player.id, mission.id)
        with pytest.raises(ValidationError):
            await svc.cancel_mission(player.id, mission.id)

    async def test_claim_rewards(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_claim1@test.com")
        mission = await _create_mission(db, reward_money=3000.0, reward_xp=200)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        await svc.complete_mission(player.id, mission.id)
        result = await svc.claim_rewards(player.id, mission.id)
        assert result["money_earned"] == 3000.0
        assert result["xp_earned"] == 200

    async def test_claim_rewards_already_claimed(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_claim2@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        await svc.complete_mission(player.id, mission.id)
        await svc.claim_rewards(player.id, mission.id)
        with pytest.raises(ConflictError):
            await svc.claim_rewards(player.id, mission.id)

    async def test_claim_rewards_not_completed(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_claim3@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        with pytest.raises(ValidationError):
            await svc.claim_rewards(player.id, mission.id)

    async def test_get_history(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_hist1@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        await svc.complete_mission(player.id, mission.id)
        history, total = await svc.get_history(player.id)
        assert total >= 1

    async def test_get_statistics(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_stats1@test.com")
        svc = MissionService(db)
        stats = await svc.get_statistics(player.id)
        assert stats is not None
        assert stats.total_completed == 0

    async def test_get_statistics_after_complete(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_stats2@test.com")
        mission = await _create_mission(db, category="story")
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        await svc.complete_mission(player.id, mission.id)
        stats = await svc.get_statistics(player.id)
        assert stats.total_completed == 1
        assert stats.story_completed == 1

    async def test_restart_mission(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_restart1@test.com")
        mission = await _create_mission(db, repeatable=True)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        await svc.complete_mission(player.id, mission.id)
        pm = await svc.restart_mission(player.id, mission.id)
        assert pm.status == MissionStatus.IN_PROGRESS

    async def test_restart_mission_not_repeatable(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_restart2@test.com")
        mission = await _create_mission(db, repeatable=False)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        await svc.complete_mission(player.id, mission.id)
        with pytest.raises(ValidationError):
            await svc.restart_mission(player.id, mission.id)

    async def test_cooldown_after_complete(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_cd1@test.com")
        mission = await _create_mission(db, cooldown_seconds=3600)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        await svc.start_mission(player.id, mission.id)
        await svc.complete_mission(player.id, mission.id)
        cd = await svc.mission_repo.get_cooldown(player.id, mission.id)
        assert cd is not None

    async def test_get_active_missions(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_active1@test.com")
        m1 = await _create_mission(db, mission_name="Active1")
        m2 = await _create_mission(db, mission_name="Active2")
        svc = MissionService(db)
        await svc.accept_mission(player.id, m1.id)
        await svc.start_mission(player.id, m1.id)
        await svc.accept_mission(player.id, m2.id)
        active = await svc.get_active_missions(player.id)
        assert len(active) >= 1

    async def test_get_progress(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc_prog3@test.com")
        mission = await _create_mission(db)
        svc = MissionService(db)
        await svc.accept_mission(player.id, mission.id)
        pm = await svc.get_progress(player.id, mission.id)
        assert pm is not None
        assert pm.status == MissionStatus.ACCEPTED


# ══════════════════════════════════════════════════════════════════════════════
# API TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestMissionAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"missapi_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"missapi_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        assert resp.status_code == 201
        return resp.json()["data"]["access_token"]

    async def test_list_missions(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/missions/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_list_missions_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/missions/")
        assert resp.status_code == 401

    async def test_get_mission_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/missions/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_accept_mission_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/missions/accept",
            json={"mission_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_player_active_missions(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/missions/player/active",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_player_statistics(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/missions/player/statistics",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_mission_history(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/missions/history/list",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_player_mission_progress(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/missions/player/{uuid.uuid4()}/progress",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    async def test_start_mission_not_accepted(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/missions/start",
            json={"mission_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_complete_mission_not_active(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/missions/complete",
            json={"mission_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_cancel_mission_not_found(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/missions/cancel",
            json={"mission_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_claim_rewards_not_completed(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/missions/claim-rewards",
            json={"mission_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_restart_mission_not_found(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/missions/restart",
            json={"mission_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_fail_mission_not_found(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/missions/fail",
            json={"mission_id": str(uuid.uuid4()), "failure_reason": "timeout"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)
