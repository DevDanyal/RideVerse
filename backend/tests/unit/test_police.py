"""Unit tests for the Police System (TASK 13).

Covers: Officer CRUD, Station CRUD, Crime CRUD, Wanted Levels, Arrests,
Fines, Jail, Crime Reports, Dispatch, Police Records, Equipment, Vehicles.
Repository, Service, and API tests using in-memory SQLite.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import create_access_token, get_password_hash
from app.database.base import Base
from app.dependencies import get_current_active_user, get_db_session
from app.main import app
from app.models.auth import PlayerAccount, AccountStatus, AccountRole
from app.models.player import Player, PlayerStatistics, PlayerSettings
from app.models.economy import Wallet
from app.models.inventory import Inventory
from app.models.police import (
    Arrest,
    ArrestStatus,
    Crime,
    CrimeReport,
    CrimeHistory,
    CrimeType,
    DepartmentType,
    Dispatch,
    DispatchPriority,
    DispatchStatus,
    EquipmentType,
    Fine,
    FineStatus,
    Jail,
    JailStatus,
    OfficerRank,
    OfficerStatus,
    PoliceEquipment,
    PoliceOfficer,
    PoliceRecord,
    PoliceStation,
    PoliceVehicle,
    PoliceVehicleType,
    ReportStatus,
    WantedLevel,
    WantedLevelValue,
)
from app.repositories.auth import AuthRepository
from app.repositories.police import PoliceRepository
from app.services.police import PoliceService

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_POLICE_TABLES = [
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
        "police_officers",
        "police_stations",
        "police_crimes",
        "police_wanted_levels",
        "police_arrests",
        "police_fines",
        "police_jail",
        "police_crime_reports",
        "police_dispatches",
        "police_records",
        "police_equipment",
        "police_vehicles",
        "crime_history",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_POLICE_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_POLICE_TABLES)
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
    email = f"police_test_{uuid.uuid4().hex[:8]}@test.com"
    username = f"police_tester_{uuid.uuid4().hex[:8]}"
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
    email = f"police_player_{uuid.uuid4().hex[:8]}@test.com"
    username = f"police_player_{uuid.uuid4().hex[:8]}"
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
    return account, player


# ── Repository Tests ───────────────────────────────────────────────────────────


class TestPoliceRepository:
    async def test_create_and_get_officer(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        officer = await repo.create_officer({
            "player_id": player.id,
            "badge_number": "BADGE-001",
            "rank": "patrol_officer",
            "department": "city_police",
        })
        await db.flush()
        assert officer.badge_number == "BADGE-001"

        fetched = await repo.get_officer_by_id(officer.id)
        assert fetched is not None
        assert fetched.badge_number == "BADGE-001"

    async def test_get_officer_by_player_id(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        await repo.create_officer({
            "player_id": player.id,
            "badge_number": "BADGE-002",
        })
        await db.flush()

        found = await repo.get_officer_by_player_id(player.id)
        assert found is not None
        assert found.player_id == player.id

    async def test_create_and_get_station(self, db: AsyncSession):
        repo = PoliceRepository(db)

        station = await repo.create_station({
            "station_name": "Central Station",
            "department": "city_police",
            "max_officers": 100,
        })
        await db.flush()

        fetched = await repo.get_station_by_id(station.id)
        assert fetched is not None
        assert fetched.station_name == "Central Station"

    async def test_create_and_get_crime(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        crime = await repo.create_crime({
            "player_id": player.id,
            "crime_type": "speeding",
            "wanted_level": 1,
            "fine_amount": 500.0,
        })
        await db.flush()

        fetched = await repo.get_crime_by_id(crime.id)
        assert fetched is not None
        assert fetched.crime_type == "speeding"

    async def test_create_and_get_wanted_level(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        wl = await repo.create_wanted_level({
            "player_id": player.id,
            "current_level": 3,
            "reason": "Robbery",
        })
        await db.flush()

        fetched = await repo.get_wanted_level(player.id)
        assert fetched is not None
        assert fetched.current_level == 3

    async def test_update_wanted_level(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        await repo.create_wanted_level({
            "player_id": player.id,
            "current_level": 2,
        })
        await db.flush()

        updated = await repo.update_wanted_level(player.id, {"current_level": 5})
        assert updated is not None
        assert updated.current_level == 5

    async def test_create_and_get_arrest(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account1, player1 = await _create_player_with_account(db)
        account2, player2 = await _create_player_with_account(db)

        officer = await repo.create_officer({
            "player_id": player2.id,
            "badge_number": "BADGE-003",
        })
        await db.flush()

        crime = await repo.create_crime({
            "player_id": player1.id,
            "crime_type": "robbery",
            "wanted_level": 4,
        })
        await db.flush()

        arrest = await repo.create_arrest({
            "player_id": player1.id,
            "officer_id": officer.id,
            "crime_id": crime.id,
            "wanted_level_at_arrest": 4,
            "fine_amount": 15000.0,
        })
        await db.flush()

        fetched = await repo.get_arrest_by_id(arrest.id)
        assert fetched is not None
        assert fetched.player_id == player1.id

    async def test_create_and_get_fine(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        fine = await repo.create_fine({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "amount": 5000.0,
            "reason": "Vehicle theft",
            "status": "pending",
        })
        await db.flush()

        fetched = await repo.get_fine_by_id(fine.id)
        assert fetched is not None
        assert fetched.amount == 5000.0

    async def test_create_and_get_jail(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        jail = await repo.create_jail({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "sentence_seconds": 300,
            "status": "serving",
        })
        await db.flush()

        fetched = await repo.get_jail_by_id(jail.id)
        assert fetched is not None
        assert fetched.sentence_seconds == 300

    async def test_create_and_get_report(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        report = await repo.create_report({
            "crime_id": uuid.uuid4(),
            "reporter_player_id": player.id,
            "description": "Saw a robbery",
            "status": "filed",
        })
        await db.flush()

        fetched = await repo.get_report_by_id(report.id)
        assert fetched is not None
        assert fetched.description == "Saw a robbery"

    async def test_create_and_get_dispatch(self, db: AsyncSession):
        repo = PoliceRepository(db)

        dispatch = await repo.create_dispatch({
            "crime_id": uuid.uuid4(),
            "priority": "high",
            "status": "pending",
            "message": "Armed robbery in progress",
        })
        await db.flush()

        fetched = await repo.get_dispatch_by_id(dispatch.id)
        assert fetched is not None
        assert fetched.priority == "high"

    async def test_create_and_get_equipment(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        officer = await repo.create_officer({
            "player_id": player.id,
            "badge_number": "BADGE-004",
        })
        await db.flush()

        equip = await repo.create_equipment({
            "officer_id": officer.id,
            "equipment_type": "pistol",
            "name": "Glock 19",
            "serial_number": "SN-001",
        })
        await db.flush()

        fetched = await repo.get_equipment_by_id(equip.id)
        assert fetched is not None
        assert fetched.name == "Glock 19"

    async def test_create_and_get_vehicle(self, db: AsyncSession):
        repo = PoliceRepository(db)

        vehicle = await repo.create_vehicle({
            "vehicle_type": "police_car",
            "model_name": "Crown Victoria",
            "call_sign": "Unit-101",
            "department": "city_police",
        })
        await db.flush()

        fetched = await repo.get_vehicle_by_id(vehicle.id)
        assert fetched is not None
        assert fetched.model_name == "Crown Victoria"

    async def test_get_record_for_player(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        record = await repo.create_record({
            "player_id": player.id,
            "wanted_level": 0,
            "total_arrests": 2,
            "total_fines": 1000.0,
        })
        await db.flush()

        fetched = await repo.get_record_for_player(player.id)
        assert fetched is not None
        assert fetched.total_arrests == 2

    async def test_soft_delete_officer(self, db: AsyncSession):
        repo = PoliceRepository(db)
        account, player = await _create_player_with_account(db)

        officer = await repo.create_officer({
            "player_id": player.id,
            "badge_number": "BADGE-DEL",
        })
        await db.flush()

        result = await repo.soft_delete_officer(officer.id)
        assert result is True
        assert await repo.get_officer_by_id(officer.id) is None


# ── Service Tests ──────────────────────────────────────────────────────────────


class TestPoliceService:
    async def test_create_officer(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        officer = await svc.create_officer({
            "player_id": player.id,
            "badge_number": f"B-{uuid.uuid4().hex[:6]}",
            "rank": "cadet",
            "department": "city_police",
        })
        assert officer is not None
        assert officer.badge_number is not None

    async def test_create_officer_duplicate_player(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)
        badge = f"B-{uuid.uuid4().hex[:6]}"

        await svc.create_officer({
            "player_id": player.id,
            "badge_number": badge,
        })
        await db.flush()

        with pytest.raises(ConflictError):
            await svc.create_officer({
                "player_id": player.id,
                "badge_number": f"B-{uuid.uuid4().hex[:6]}",
            })

    async def test_create_station(self, db: AsyncSession):
        svc = PoliceService(db)

        station = await svc.create_station({
            "station_name": "Test Station",
            "department": "city_police",
            "max_officers": 30,
        })
        assert station.station_name == "Test Station"

    async def test_create_crime(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        crime = await svc.create_crime({
            "player_id": player.id,
            "crime_type": "speeding",
            "wanted_level": 1,
            "fine_amount": 500.0,
        })
        assert crime.crime_type == "speeding"

    async def test_create_crime_invalid_type(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        with pytest.raises(ValidationError):
            await svc.create_crime({
                "player_id": player.id,
                "crime_type": "invalid_crime",
            })

    async def test_set_wanted_level(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        wl = await svc.set_wanted_level(player.id, 3, reason="Armed robbery")
        assert wl.current_level == 3
        assert wl.reason == "Armed robbery"

    async def test_set_wanted_level_invalid(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        with pytest.raises(ValidationError):
            await svc.set_wanted_level(player.id, 7)

    async def test_escalate_wanted_level(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        wl = await svc.escalate_wanted_level(player.id, "murder")
        assert wl.current_level == 6

    async def test_arrest_resets_wanted_level(self, db: AsyncSession):
        svc = PoliceService(db)
        account1, player1 = await _create_player_with_account(db)
        account2, player2 = await _create_player_with_account(db)

        officer = await svc.create_officer({
            "player_id": player2.id,
            "badge_number": f"B-{uuid.uuid4().hex[:6]}",
        })
        await db.flush()

        crime = await svc.create_crime({
            "player_id": player1.id,
            "crime_type": "robbery",
            "wanted_level": 4,
        })
        await db.flush()

        await svc.set_wanted_level(player1.id, 4)

        arrest = await svc.create_arrest({
            "player_id": player1.id,
            "officer_id": officer.id,
            "crime_id": crime.id,
            "wanted_level_at_arrest": 4,
        })
        await db.flush()

        wl = await svc.get_wanted_level(player1.id)
        assert wl.current_level == 0

    async def test_create_fine(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        fine = await svc.create_fine({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "amount": 2500.0,
            "reason": "Property damage",
        })
        assert fine.amount == 2500.0

    async def test_pay_fine(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        fine = await svc.create_fine({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "amount": 1000.0,
            "reason": "Speeding",
        })

        paid = await svc.pay_fine(fine.id)
        assert paid.status == "paid"
        assert paid.paid_at is not None

    async def test_pay_fine_already_paid(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        fine = await svc.create_fine({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "amount": 1000.0,
            "reason": "Speeding",
        })
        await svc.pay_fine(fine.id)

        with pytest.raises(ConflictError):
            await svc.pay_fine(fine.id)

    async def test_waive_fine(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        fine = await svc.create_fine({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "amount": 500.0,
            "reason": "Minor infraction",
        })

        waived = await svc.waive_fine(fine.id, "First offense warning")
        assert waived.status == "waived"
        assert waived.waived_reason == "First offense warning"

    async def test_create_jail(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        jail = await svc.create_jail({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "sentence_seconds": 600,
        })
        assert jail.sentence_seconds == 600
        assert jail.status == "serving"
        assert jail.sentence_start is not None

    async def test_release_prisoner(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        jail = await svc.create_jail({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "sentence_seconds": 300,
        })

        released = await svc.release_prisoner(jail.id, "Good behavior")
        assert released.status == "released"
        assert released.release_reason == "Good behavior"

    async def test_release_already_released(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        jail = await svc.create_jail({
            "arrest_id": uuid.uuid4(),
            "player_id": player.id,
            "sentence_seconds": 100,
        })
        await svc.release_prisoner(jail.id)

        with pytest.raises(ConflictError):
            await svc.release_prisoner(jail.id)

    async def test_create_report(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)
        crime = await svc.create_crime({
            "player_id": player.id,
            "crime_type": "assault",
            "wanted_level": 3,
        })

        report = await svc.create_report({
            "crime_id": crime.id,
            "reporter_player_id": player.id,
            "description": "Witnessed assault near downtown",
        })
        assert report.description == "Witnessed assault near downtown"

    async def test_create_dispatch(self, db: AsyncSession):
        svc = PoliceService(db)

        dispatch = await svc.create_dispatch({
            "crime_id": uuid.uuid4(),
            "priority": "critical",
            "message": "Active shooter reported",
        })
        assert dispatch.priority == "critical"

    async def test_accept_dispatch(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        officer = await svc.create_officer({
            "player_id": player.id,
            "badge_number": f"B-{uuid.uuid4().hex[:6]}",
        })
        await db.flush()

        dispatch = await svc.create_dispatch({
            "crime_id": uuid.uuid4(),
            "priority": "high",
        })

        accepted = await svc.accept_dispatch(dispatch.id, officer.id)
        assert accepted.status == "dispatched"
        assert accepted.officer_id == officer.id

    async def test_complete_dispatch(self, db: AsyncSession):
        svc = PoliceService(db)

        dispatch = await svc.create_dispatch({
            "crime_id": uuid.uuid4(),
            "priority": "medium",
        })

        completed = await svc.complete_dispatch(dispatch.id)
        assert completed.status == "completed"

    async def test_create_equipment(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        officer = await svc.create_officer({
            "player_id": player.id,
            "badge_number": f"B-{uuid.uuid4().hex[:6]}",
        })
        await db.flush()

        equip = await svc.create_equipment(officer.id, {
            "equipment_type": "taser",
            "name": "Taser X26",
            "serial_number": f"TSR-{uuid.uuid4().hex[:6]}",
        })
        assert equip.name == "Taser X26"

    async def test_create_vehicle(self, db: AsyncSession):
        svc = PoliceService(db)

        vehicle = await svc.create_vehicle({
            "vehicle_type": "police_car",
            "model_name": "Interceptor",
            "call_sign": f"Unit-{uuid.uuid4().hex[:4]}",
            "department": "highway_patrol",
        })
        assert vehicle.model_name == "Interceptor"
        assert vehicle.department == "highway_patrol"

    async def test_assign_vehicle_to_officer(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        officer = await svc.create_officer({
            "player_id": player.id,
            "badge_number": f"B-{uuid.uuid4().hex[:6]}",
        })
        await db.flush()

        vehicle = await svc.create_vehicle({
            "vehicle_type": "police_car",
            "model_name": "Cruiser",
        })

        assigned = await svc.assign_vehicle_to_officer(vehicle.id, officer.id)
        assert assigned.officer_id == officer.id

    async def test_get_police_record(self, db: AsyncSession):
        svc = PoliceService(db)
        account, player = await _create_player_with_account(db)

        record = await svc.get_police_record(player.id)
        assert record.total_arrests == 0
        assert record.wanted_level == 0

    async def test_confirm_arrest(self, db: AsyncSession):
        svc = PoliceService(db)
        account1, player1 = await _create_player_with_account(db)
        account2, player2 = await _create_player_with_account(db)

        officer = await svc.create_officer({
            "player_id": player2.id,
            "badge_number": f"B-{uuid.uuid4().hex[:6]}",
        })
        await db.flush()

        crime = await svc.create_crime({
            "player_id": player1.id,
            "crime_type": "assault",
            "wanted_level": 3,
        })
        await db.flush()

        arrest = await svc.create_arrest({
            "player_id": player1.id,
            "officer_id": officer.id,
            "crime_id": crime.id,
            "wanted_level_at_arrest": 3,
        })

        confirmed = await svc.confirm_arrest(arrest.id)
        assert confirmed.status == "confirmed"

    async def test_dismiss_arrest(self, db: AsyncSession):
        svc = PoliceService(db)
        account1, player1 = await _create_player_with_account(db)
        account2, player2 = await _create_player_with_account(db)

        officer = await svc.create_officer({
            "player_id": player2.id,
            "badge_number": f"B-{uuid.uuid4().hex[:6]}",
        })
        await db.flush()

        crime = await svc.create_crime({
            "player_id": player1.id,
            "crime_type": "assault",
            "wanted_level": 3,
        })
        await db.flush()

        arrest = await svc.create_arrest({
            "player_id": player1.id,
            "officer_id": officer.id,
            "crime_id": crime.id,
            "wanted_level_at_arrest": 3,
        })

        dismissed = await svc.dismiss_arrest(arrest.id)
        assert dismissed.status == "dismissed"

    async def test_assign_report(self, db: AsyncSession):
        svc = PoliceService(db)
        account1, player1 = await _create_player_with_account(db)
        account2, player2 = await _create_player_with_account(db)

        officer = await svc.create_officer({
            "player_id": player2.id,
            "badge_number": f"B-{uuid.uuid4().hex[:6]}",
        })
        await db.flush()

        crime = await svc.create_crime({
            "player_id": player1.id,
            "crime_type": "robbery",
            "wanted_level": 4,
        })

        report = await svc.create_report({
            "crime_id": crime.id,
            "reporter_player_id": player1.id,
            "description": "Robbery at bank",
        })

        assigned = await svc.assign_report(report.id, officer.id)
        assert assigned.assigned_officer_id == officer.id
        assert assigned.status == "under_investigation"


# ── API Tests ──────────────────────────────────────────────────────────────────


class TestPoliceAPI:
    async def test_create_station_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/police/stations",
            json={
                "station_name": "API Station",
                "department": "city_police",
                "max_officers": 25,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["station_name"] == "API Station"

    async def test_list_stations_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get(
            "/api/v1/police/stations",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    async def test_create_officer_api(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        resp = await client.post(
            "/api/v1/police/officers",
            json={
                "player_id": str(player.id),
                "badge_number": f"API-{uuid.uuid4().hex[:6]}",
                "rank": "cadet",
                "department": "city_police",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True

    async def test_create_crime_api(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        resp = await client.post(
            "/api/v1/police/crimes",
            json={
                "player_id": str(player.id),
                "crime_type": "speeding",
                "wanted_level": 1,
                "fine_amount": 500.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["data"]["crime_type"] == "speeding"

    async def test_set_wanted_level_api(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        resp = await client.post(
            "/api/v1/police/wanted/set",
            json={
                "player_id": str(player.id),
                "current_level": 3,
                "reason": "Armed robbery",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["current_level"] == 3

    async def test_get_wanted_level_api(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        resp = await client.get(
            f"/api/v1/police/wanted/{player.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    async def test_create_vehicle_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/police/vehicles",
            json={
                "vehicle_type": "suv",
                "model_name": "Tahoe",
                "call_sign": f"API-{uuid.uuid4().hex[:4]}",
                "department": "city_police",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["data"]["model_name"] == "Tahoe"

    async def test_create_fine_api(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        resp = await client.post(
            "/api/v1/police/fines",
            json={
                "arrest_id": str(uuid.uuid4()),
                "player_id": str(player.id),
                "amount": 750.0,
                "reason": "Reckless driving",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["data"]["amount"] == 750.0

    async def test_get_police_record_api(self, client: AsyncClient, auth_headers: dict, db: AsyncSession):
        account, player = await _create_player_with_account(db)

        resp = await client.get(
            f"/api/v1/police/record/{player.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total_arrests"] == 0
