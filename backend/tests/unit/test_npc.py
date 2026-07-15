"""Unit tests for the NPC System (TASK 12).

Covers: NPC CRUD, schedules, dialogues, professions, relationships,
interactions, statistics, spawn points — repositories, services, and
API endpoints. All tests use an in-memory SQLite database.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import create_access_token, get_password_hash
from app.database.base import Base
from app.dependencies import get_current_active_user, get_db_session
from app.main import app
from app.models.npc import (
    Npc,
    NpcCategory,
    NpcDialogue,
    NpcInteraction,
    NpcProfession,
    NpcRelationship,
    NpcSchedule,
    NpcSpawn,
    NpcStatistics,
    NpcStatus,
    RelationshipLevel,
    SpawnCondition,
)
from app.models.auth import PlayerAccount, AccountStatus, AccountRole
from app.models.player import Player, PlayerStatistics, PlayerSettings
from app.models.economy import Wallet
from app.models.inventory import Inventory
from app.repositories.auth import AuthRepository
from app.repositories.npc import NpcRepository
from app.services.npc import NpcService

# ── Settings ───────────────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


# ── Tables needed for NPC system tests ────────────────────────────────────────

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


# ── Fixtures ──────────────────────────────────────────────────────────────────


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


@pytest_asyncio.fixture
async def auth_headers(db: AsyncSession) -> dict:
    email = f"npc_test_{uuid.uuid4().hex[:8]}@test.com"
    username = f"npc_tester_{uuid.uuid4().hex[:8]}"
    repo = AuthRepository(db)
    account = await repo.create_account(email, username, get_password_hash("StrongPass1!"))
    await db.flush()

    player = Player(
        account_id=account.id,
        display_name=f"Player_{username}",
        level=1,
    )
    db.add(player)
    await db.flush()

    token = create_access_token({"sub": str(account.id), "type": "access"})
    return {"Authorization": f"Bearer {token}"}


async def _create_player_with_account(db: AsyncSession) -> tuple[PlayerAccount, Player]:
    email = f"npc_player_{uuid.uuid4().hex[:8]}@test.com"
    username = f"npc_player_{uuid.uuid4().hex[:8]}"
    repo = AuthRepository(db)
    account = await repo.create_account(email, username, get_password_hash("StrongPass1!"))
    await db.flush()

    player = Player(
        account_id=account.id,
        display_name=f"Player_{username}",
        level=5,
        experience=1000,
        cash=100000.0,
    )
    db.add(player)
    await db.flush()

    stats = PlayerStatistics(player_id=player.id)
    db.add(stats)
    settings = PlayerSettings(player_id=player.id)
    db.add(settings)
    wallet = Wallet(player_id=player.id, cash=10000.0, bank_balance=50000.0)
    db.add(wallet)
    inventory = Inventory(player_id=player.id, max_slots=50, used_slots=0, total_weight=0.0)
    db.add(inventory)
    await db.flush()

    return account, player


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


# ══════════════════════════════════════════════════════════════════════════════
# REPOSITORY TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestNpcRepository:
    async def test_create_and_get_npc(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "John",
            "npc_category": NpcCategory.CITIZEN,
            "description": "A friendly citizen",
        })
        await db.flush()

        fetched = await repo.get_npc_by_id(npc.id)
        assert fetched is not None
        assert fetched.npc_name == "John"
        assert fetched.npc_category == NpcCategory.CITIZEN

    async def test_get_all_npcs(self, db: AsyncSession):
        repo = NpcRepository(db)
        for name in ["Alice", "Bob", "Charlie"]:
            await repo.create_npc({
                "npc_name": name,
                "npc_category": NpcCategory.CITIZEN,
            })
        await db.flush()

        npcs = await repo.get_all_npcs()
        assert len(npcs) >= 3

    async def test_count_npcs(self, db: AsyncSession):
        repo = NpcRepository(db)
        for name in ["NPC1", "NPC2"]:
            await repo.create_npc({
                "npc_name": name,
                "npc_category": NpcCategory.SHOPKEEPER,
            })
        await db.flush()

        count = await repo.count_npcs(category="shopkeeper")
        assert count >= 2

    async def test_soft_delete_npc(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "ToDelete",
            "npc_category": NpcCategory.CITIZEN,
        })
        await db.flush()

        deleted = await repo.soft_delete_npc(npc.id)
        assert deleted is True

        fetched = await repo.get_npc_by_id(npc.id)
        assert fetched is None

    async def test_update_npc(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Original",
            "npc_category": NpcCategory.CITIZEN,
        })
        await db.flush()

        updated = await repo.update_npc(npc.id, {"npc_name": "Updated"})
        assert updated is not None
        assert updated.npc_name == "Updated"

    async def test_create_and_get_schedule(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Scheduled",
            "npc_category": NpcCategory.CITIZEN,
        })
        await db.flush()

        schedule = await repo.create_schedule({
            "npc_id": npc.id,
            "period": "morning",
            "activity": "Work at shop",
            "location_name": "Downtown",
        })
        await db.flush()

        schedules = await repo.get_schedules_for_npc(npc.id)
        assert len(schedules) >= 1
        assert schedules[0].activity == "Work at shop"

    async def test_create_and_get_dialogue(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Talkative",
            "npc_category": NpcCategory.SHOPKEEPER,
        })
        await db.flush()

        dialogue = await repo.create_dialogue({
            "npc_id": npc.id,
            "dialogue_key": "greeting",
            "dialogue_text": "Hello there!",
            "is_greeting": True,
        })
        await db.flush()

        dialogues = await repo.get_dialogues_for_npc(npc.id)
        assert len(dialogues) >= 1
        assert dialogues[0].dialogue_text == "Hello there!"

    async def test_create_and_get_profession(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Mechanic",
            "npc_category": NpcCategory.MECHANIC,
        })
        await db.flush()

        prof = await repo.create_profession({
            "npc_id": npc.id,
            "profession_type": NpcCategory.MECHANIC,
            "skill_level": 5,
            "specialty": "Engine repair",
        })
        await db.flush()

        fetched = await repo.get_profession_for_npc(npc.id)
        assert fetched is not None
        assert fetched.skill_level == 5

    async def test_create_and_get_relationship(self, db: AsyncSession):
        from app.models.npc import NpcRelationship
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Friendly NPC",
            "npc_category": NpcCategory.CITIZEN,
        })
        await db.flush()

        player_id = uuid.uuid4()
        rel = await repo.create_relationship({
            "player_id": player_id,
            "npc_id": npc.id,
            "level": RelationshipLevel.NEUTRAL,
            "reputation_score": 0.0,
        })
        await db.flush()

        fetched = await repo.get_relationship(player_id, npc.id)
        assert fetched is not None
        assert fetched.level == RelationshipLevel.NEUTRAL

    async def test_create_and_get_interaction(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Interactive",
            "npc_category": NpcCategory.CITIZEN,
        })
        await db.flush()

        interaction = await repo.create_interaction({
            "player_id": uuid.uuid4(),
            "npc_id": npc.id,
            "interaction_type": "greet",
            "reputation_change": 1.0,
            "was_positive": True,
        })
        await db.flush()

        interactions = await repo.get_interactions_for_npc(npc.id)
        assert len(interactions) >= 1

    async def test_create_and_get_statistics(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Popular",
            "npc_category": NpcCategory.SHOPKEEPER,
        })
        await db.flush()

        stats = await repo.create_statistics({
            "npc_id": npc.id,
            "total_interactions": 10,
        })
        await db.flush()

        fetched = await repo.get_statistics(npc.id)
        assert fetched is not None
        assert fetched.total_interactions == 10

    async def test_create_spawn_point(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Spawner",
            "npc_category": NpcCategory.CITIZEN,
        })
        await db.flush()

        spawn = await repo.create_spawn_point({
            "npc_id": npc.id,
            "zone_name": "Downtown",
            "location_x": 100.0,
            "location_y": 200.0,
            "location_z": 0.0,
        })
        await db.flush()

        spawns = await repo.get_spawn_points_for_npc(npc.id)
        assert len(spawns) >= 1
        assert spawns[0].zone_name == "Downtown"

    async def test_get_npcs_in_zone(self, db: AsyncSession):
        repo = NpcRepository(db)
        npc = await repo.create_npc({
            "npc_name": "Zone NPC",
            "npc_category": NpcCategory.CITIZEN,
        })
        await db.flush()

        await repo.create_spawn_point({
            "npc_id": npc.id,
            "zone_name": "Market",
            "location_x": 50.0,
            "location_y": 60.0,
            "location_z": 0.0,
        })
        await db.flush()

        npcs = await repo.get_npcs_in_zone("Market")
        assert len(npcs) >= 1

    async def test_get_npcs_by_category(self, db: AsyncSession):
        repo = NpcRepository(db)
        await repo.create_npc({
            "npc_name": "Mech1",
            "npc_category": NpcCategory.MECHANIC,
        })
        await repo.create_npc({
            "npc_name": "Mech2",
            "npc_category": NpcCategory.MECHANIC,
        })
        await db.flush()

        mechs = await repo.get_npcs_by_category("mechanic")
        assert len(mechs) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestNpcService:
    async def test_create_npc(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Service NPC",
            "npc_category": "citizen",
        })
        assert npc.npc_name == "Service NPC"
        assert npc.npc_category == "citizen"
        assert npc.statistics is not None

    async def test_create_npc_invalid_category(self, db: AsyncSession):
        svc = NpcService(db)
        with pytest.raises(ValidationError):
            await svc.create_npc({
                "npc_name": "Bad",
                "npc_category": "invalid_cat",
            })

    async def test_get_npc(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Get NPC",
            "npc_category": "doctor",
        })
        fetched = await svc.get_npc(npc.id)
        assert fetched.npc_name == "Get NPC"

    async def test_get_npc_not_found(self, db: AsyncSession):
        svc = NpcService(db)
        with pytest.raises(NotFoundError):
            await svc.get_npc(uuid.uuid4())

    async def test_list_npcs(self, db: AsyncSession):
        svc = NpcService(db)
        for name in ["List1", "List2"]:
            await svc.create_npc({
                "npc_name": name,
                "npc_category": "taxi_driver",
            })
        await db.flush()

        npcs, total = await svc.list_npcs(category="taxi_driver")
        assert len(npcs) >= 2
        assert total >= 2

    async def test_update_npc(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Old Name",
            "npc_category": "citizen",
        })
        updated = await svc.update_npc(npc.id, {"npc_name": "New Name"})
        assert updated.npc_name == "New Name"

    async def test_delete_npc(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Doomed",
            "npc_category": "citizen",
        })
        deleted = await svc.delete_npc(npc.id)
        assert deleted is True

    async def test_add_schedule(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Scheduled",
            "npc_category": "citizen",
        })
        schedule = await svc.add_schedule(npc.id, {
            "period": "morning",
            "activity": "Open shop",
        })
        assert schedule.activity == "Open shop"

    async def test_get_schedules(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Schedule NPC",
            "npc_category": "citizen",
        })
        await svc.add_schedule(npc.id, {"period": "afternoon", "activity": "Lunch"})
        schedules = await svc.get_schedules(npc.id)
        assert len(schedules) >= 1

    async def test_add_dialogue(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Talker",
            "npc_category": "shopkeeper",
        })
        dialogue = await svc.add_dialogue(npc.id, {
            "dialogue_key": "welcome",
            "dialogue_text": "Welcome to my shop!",
            "is_greeting": True,
        })
        assert dialogue.dialogue_text == "Welcome to my shop!"

    async def test_get_dialogues(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Dialogue NPC",
            "npc_category": "shopkeeper",
        })
        await svc.add_dialogue(npc.id, {"dialogue_key": "g1", "dialogue_text": "Hi"})
        await svc.add_dialogue(npc.id, {"dialogue_key": "g2", "dialogue_text": "Hello"})
        dialogues = await svc.get_dialogues(npc.id)
        assert len(dialogues) >= 2

    async def test_set_profession(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Worker",
            "npc_category": "mechanic",
        })
        prof = await svc.set_profession(npc.id, {
            "profession_type": "mechanic",
            "skill_level": 3,
            "specialty": "Tires",
        })
        assert prof.skill_level == 3

    async def test_get_profession(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Pro",
            "npc_category": "doctor",
        })
        await svc.set_profession(npc.id, {
            "profession_type": "doctor",
            "skill_level": 7,
        })
        prof = await svc.get_profession(npc.id)
        assert prof.skill_level == 7

    async def test_get_profession_not_found(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "NoPro",
            "npc_category": "citizen",
        })
        with pytest.raises(NotFoundError):
            await svc.get_profession(npc.id)

    async def test_get_relationship(self, db: AsyncSession):
        svc = NpcService(db)
        player_id = uuid.uuid4()
        npc = await svc.create_npc({
            "npc_name": "Rel NPC",
            "npc_category": "citizen",
        })
        rel = await svc.get_relationship(player_id, npc.id)
        assert rel.level == "neutral"
        assert rel.reputation_score == 0.0

    async def test_update_relationship(self, db: AsyncSession):
        svc = NpcService(db)
        player_id = uuid.uuid4()
        npc = await svc.create_npc({
            "npc_name": "UpdRel",
            "npc_category": "citizen",
        })
        await svc.get_relationship(player_id, npc.id)
        updated = await svc.update_relationship(player_id, npc.id, {
            "reputation_score": 25.0,
        })
        assert updated.reputation_score == 25.0
        assert updated.level == "friendly"

    async def test_interact(self, db: AsyncSession):
        svc = NpcService(db)
        account, player = await _create_player_with_account(db)
        npc = await svc.create_npc({
            "npc_name": "Interact NPC",
            "npc_category": "shopkeeper",
        })
        await svc.add_dialogue(npc.id, {
            "dialogue_key": "greeting",
            "dialogue_text": "Hi!",
            "is_greeting": True,
        })
        await db.flush()

        result = await svc.interact(
            player.id, npc.id, "greet", "greeting"
        )
        assert result["reputation_change"] == 1.0
        assert result["new_relationship_level"] == "neutral"

    async def test_interact_attack(self, db: AsyncSession):
        svc = NpcService(db)
        account, player = await _create_player_with_account(db)
        npc = await svc.create_npc({
            "npc_name": "Victim",
            "npc_category": "citizen",
        })
        await db.flush()

        result = await svc.interact(player.id, npc.id, "attack")
        assert result["reputation_change"] == -10.0
        assert result["new_relationship_level"] in ("unfriendly", "neutral")

    async def test_get_interactions(self, db: AsyncSession):
        svc = NpcService(db)
        account, player = await _create_player_with_account(db)
        npc = await svc.create_npc({
            "npc_name": "History NPC",
            "npc_category": "citizen",
        })
        await db.flush()

        await svc.interact(player.id, npc.id, "greet")
        await svc.interact(player.id, npc.id, "talk")
        interactions, total = await svc.get_interactions(npc.id)
        assert total >= 2

    async def test_get_statistics(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Stats NPC",
            "npc_category": "citizen",
        })
        stats = await svc.get_statistics(npc.id)
        assert stats.total_interactions == 0

    async def test_add_spawn_point(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Spawn NPC",
            "npc_category": "citizen",
        })
        spawn = await svc.add_spawn_point(npc.id, {
            "zone_name": "Downtown",
            "location_x": 100.0,
            "location_y": 200.0,
            "location_z": 0.0,
        })
        assert spawn.zone_name == "Downtown"

    async def test_get_spawn_points(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Multi Spawn",
            "npc_category": "citizen",
        })
        await svc.add_spawn_point(npc.id, {
            "zone_name": "ZoneA",
            "location_x": 1.0,
            "location_y": 2.0,
            "location_z": 0.0,
        })
        await svc.add_spawn_point(npc.id, {
            "zone_name": "ZoneB",
            "location_x": 3.0,
            "location_y": 4.0,
            "location_z": 0.0,
        })
        spawns = await svc.get_spawn_points(npc.id)
        assert len(spawns) >= 2

    async def test_get_npcs_in_zone(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Zone NPC",
            "npc_category": "police_officer",
        })
        await svc.add_spawn_point(npc.id, {
            "zone_name": "CityCenter",
            "location_x": 0.0,
            "location_y": 0.0,
            "location_z": 0.0,
        })
        npcs = await svc.get_npcs_in_zone("CityCenter")
        assert len(npcs) >= 1

    async def test_cooldown_after_complete(self, db: AsyncSession):
        svc = NpcService(db)
        npc = await svc.create_npc({
            "npc_name": "Reputation Test",
            "npc_category": "citizen",
        })
        account, player = await _create_player_with_account(db)
        await db.flush()

        # Multiple positive interactions to move relationship up
        for _ in range(10):
            await svc.interact(player.id, npc.id, "help")

        rel = await svc.get_relationship(player.id, npc.id)
        assert rel.reputation_score > 0
        assert rel.level in ("friendly", "trusted", "loved")


# ══════════════════════════════════════════════════════════════════════════════
# API TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestNpcAPI:
    async def test_create_npc(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/npcs/",
            json={
                "npc_name": "API NPC",
                "npc_category": "citizen",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["success"] is True
        assert resp.json()["data"]["npc_name"] == "API NPC"

    async def test_list_npcs(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/npcs/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_get_npc_not_found(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get(
            f"/api/v1/npcs/{uuid.uuid4()}", headers=auth_headers
        )
        assert resp.status_code == 404

    async def test_update_npc(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Update Me", "npc_category": "doctor"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.patch(
            f"/api/v1/npcs/{npc_id}",
            json={"npc_name": "Updated"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["npc_name"] == "Updated"

    async def test_delete_npc(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Delete Me", "npc_category": "citizen"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.delete(
            f"/api/v1/npcs/{npc_id}", headers=auth_headers
        )
        assert resp.status_code == 200

    async def test_add_schedule(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Schedule NPC", "npc_category": "citizen"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/schedules",
            json={"period": "morning", "activity": "Work"},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    async def test_add_dialogue(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Dialogue NPC", "npc_category": "shopkeeper"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/dialogues",
            json={"dialogue_key": "welcome", "dialogue_text": "Welcome!"},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    async def test_set_profession(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Prof NPC", "npc_category": "mechanic"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/profession",
            json={"profession_type": "mechanic", "skill_level": 5},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    async def test_get_profession_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "NoProf", "npc_category": "citizen"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.get(
            f"/api/v1/npcs/{npc_id}/profession", headers=auth_headers
        )
        assert resp.status_code == 404

    async def test_get_statistics(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Stats NPC", "npc_category": "citizen"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.get(
            f"/api/v1/npcs/{npc_id}/statistics", headers=auth_headers
        )
        assert resp.status_code == 200

    async def test_add_spawn_point(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Spawn NPC", "npc_category": "citizen"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/npcs/{npc_id}/spawns",
            json={
                "zone_name": "Downtown",
                "location_x": 100.0,
                "location_y": 200.0,
                "location_z": 0.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201

    async def test_get_relationship(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Rel NPC", "npc_category": "citizen"},
            headers=auth_headers,
        )
        npc_id = create_resp.json()["data"]["id"]

        resp = await client.get(
            f"/api/v1/npcs/{npc_id}/relationship", headers=auth_headers
        )
        assert resp.status_code == 200

    async def test_unauthenticated_access_denied(self, client: AsyncClient):
        endpoints = [
            ("GET", "/api/v1/npcs/"),
            ("POST", "/api/v1/npcs/"),
            ("POST", "/api/v1/npcs/interact"),
        ]
        for method, url in endpoints:
            if method == "GET":
                resp = await client.get(url)
            else:
                resp = await client.post(
                    url, json={"npc_name": "X", "npc_category": "citizen"}
                )
            assert resp.status_code == 401, f"{method} {url} should require auth"

    async def test_create_npc_invalid_category(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/v1/npcs/",
            json={"npc_name": "Bad", "npc_category": "nonexistent"},
            headers=auth_headers,
        )
        assert resp.status_code == 422
