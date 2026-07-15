"""Unit tests for the Traffic System (TASK 14).

Covers: Zone CRUD, Route CRUD, Lane CRUD, Signal CRUD + emergency override,
Spawn Point CRUD, Density CRUD, Spawn Rule CRUD, Despawn Rule CRUD,
Vehicle spawn/despawn, Emergency vehicle siren, Statistics, Speed Limit,
Violation with auto-fine, Event CRUD.
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
from app.models.traffic import (
    DespawnRuleType,
    EmergencyVehicleType,
    SpawnRuleType,
    TrafficDensity,
    TrafficDensityLevel,
    TrafficDespawnRule,
    TrafficEmergencyVehicle,
    TrafficEvent,
    TrafficEventType,
    TrafficLane,
    TrafficRoute,
    TrafficRouteType,
    TrafficSignal,
    TrafficSignalState,
    TrafficSpawnPoint,
    TrafficSpawnRule,
    TrafficSpeedLimit,
    TrafficStatistics,
    TrafficVehicle,
    TrafficVehicleType,
    TrafficViolation,
    TrafficViolationType,
    TrafficZone,
    TrafficZoneType,
)
from app.repositories.auth import AuthRepository
from app.repositories.traffic import TrafficRepository
from app.services.traffic import TrafficService, VIOLATION_FINE_AMOUNTS

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_TRAFFIC_TABLES = [
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
        "traffic_zones",
        "traffic_routes",
        "traffic_lanes",
        "traffic_signals",
        "traffic_spawn_points",
        "traffic_densities",
        "traffic_spawn_rules",
        "traffic_despawn_rules",
        "traffic_vehicles",
        "traffic_emergency_vehicles",
        "traffic_statistics",
        "traffic_speed_limits",
        "traffic_violations",
        "traffic_events",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_TRAFFIC_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_TRAFFIC_TABLES)
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
    email = f"traffic_test_{uuid.uuid4().hex[:8]}@test.com"
    username = f"traffic_tester_{uuid.uuid4().hex[:8]}"
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
    email = f"traffic_player_{uuid.uuid4().hex[:8]}@test.com"
    username = f"traffic_player_{uuid.uuid4().hex[:8]}"
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


class TestTrafficRepository:
    async def test_create_and_get_zone(self, db: AsyncSession):
        repo = TrafficRepository(db)

        zone = await repo.create_zone({
            "zone_name": "Downtown",
            "zone_type": "city_center",
            "center_x": 0.0,
            "center_y": 0.0,
            "center_z": 0.0,
            "radius": 500.0,
            "speed_limit_kmh": 50.0,
            "max_vehicles": 20,
        })
        await db.flush()
        assert zone.zone_name == "Downtown"

        fetched = await repo.get_zone_by_id(zone.id)
        assert fetched is not None
        assert fetched.zone_name == "Downtown"
        assert fetched.zone_type == TrafficZoneType.CITY_CENTER

    async def test_get_all_zones(self, db: AsyncSession):
        repo = TrafficRepository(db)

        await repo.create_zone({
            "zone_name": "Zone A",
            "zone_type": "highway",
            "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
            "radius": 1000.0,
        })
        await repo.create_zone({
            "zone_name": "Zone B",
            "zone_type": "residential",
            "center_x": 10.0, "center_y": 10.0, "center_z": 0.0,
            "radius": 300.0,
        })
        await db.flush()

        all_zones = await repo.get_all_zones()
        assert len(all_zones) >= 2

        filtered = await repo.get_all_zones(zone_type="highway")
        assert all(z.zone_type == TrafficZoneType.HIGHWAY for z in filtered)

    async def test_soft_delete_zone(self, db: AsyncSession):
        repo = TrafficRepository(db)

        zone = await repo.create_zone({
            "zone_name": "Del Zone",
            "zone_type": "parking_zone",
            "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
            "radius": 100.0,
        })
        await db.flush()

        result = await repo.soft_delete_zone(zone.id)
        assert result is True
        assert await repo.get_zone_by_id(zone.id) is None

    async def test_create_and_get_route(self, db: AsyncSession):
        repo = TrafficRepository(db)

        route = await repo.create_route({
            "route_name": "Main St",
            "route_type": "city",
            "start_x": 0.0, "start_y": 0.0, "start_z": 0.0,
            "end_x": 100.0, "end_y": 0.0, "end_z": 0.0,
            "distance_km": 1.0,
        })
        await db.flush()

        fetched = await repo.get_route_by_id(route.id)
        assert fetched is not None
        assert fetched.route_name == "Main St"

    async def test_create_and_get_lane(self, db: AsyncSession):
        repo = TrafficRepository(db)

        route = await repo.create_route({
            "route_name": "Lane Route",
            "route_type": "highway",
            "start_x": 0.0, "start_y": 0.0, "start_z": 0.0,
            "end_x": 100.0, "end_y": 0.0, "end_z": 0.0,
        })
        await db.flush()

        lane = await repo.create_lane({
            "route_id": route.id,
            "lane_number": 1,
            "direction": "forward",
            "speed_limit_kmh": 60.0,
        })
        await db.flush()

        fetched = await repo.get_lane_by_id(lane.id)
        assert fetched is not None
        assert fetched.lane_number == 1

        lanes = await repo.get_lanes_for_route(route.id)
        assert len(lanes) == 1

    async def test_create_and_get_signal(self, db: AsyncSession):
        repo = TrafficRepository(db)

        signal = await repo.create_signal({
            "signal_name": "Signal 1",
            "location_x": 10.0,
            "location_y": 20.0,
            "location_z": 0.0,
            "state": "green",
            "cycle_duration_seconds": 30,
        })
        await db.flush()

        fetched = await repo.get_signal_by_id(signal.id)
        assert fetched is not None
        assert fetched.signal_name == "Signal 1"
        assert fetched.state == TrafficSignalState.GREEN

    async def test_create_and_get_spawn_point(self, db: AsyncSession):
        repo = TrafficRepository(db)

        sp = await repo.create_spawn_point({
            "spawn_name": "SP North",
            "location_x": 0.0,
            "location_y": 100.0,
            "location_z": 0.0,
            "spawn_type": "spawn",
            "max_vehicles": 5,
        })
        await db.flush()

        fetched = await repo.get_spawn_point_by_id(sp.id)
        assert fetched is not None
        assert fetched.spawn_name == "SP North"

    async def test_create_and_get_density(self, db: AsyncSession):
        repo = TrafficRepository(db)

        density = await repo.create_density({
            "density_level": "rush_hour_morning",
            "vehicle_limit": 50,
            "spawn_rate": 2.5,
        })
        await db.flush()

        fetched = await repo.get_density_by_id(density.id)
        assert fetched is not None
        assert fetched.density_level == TrafficDensityLevel.RUSH_HOUR_MORNING

    async def test_create_and_get_spawn_rule(self, db: AsyncSession):
        repo = TrafficRepository(db)

        rule = await repo.create_spawn_rule({
            "rule_name": "Continuous Spawn",
            "rule_type": "continuous",
            "max_spawn_count": 10,
        })
        await db.flush()

        fetched = await repo.get_spawn_rule_by_id(rule.id)
        assert fetched is not None
        assert fetched.rule_type == SpawnRuleType.CONTINUOUS

    async def test_create_and_get_despawn_rule(self, db: AsyncSession):
        repo = TrafficRepository(db)

        rule = await repo.create_despawn_rule({
            "rule_name": "Distance Despawn",
            "rule_type": "distance",
            "max_distance_from_player": 800.0,
        })
        await db.flush()

        fetched = await repo.get_despawn_rule_by_id(rule.id)
        assert fetched is not None
        assert fetched.rule_type == DespawnRuleType.DISTANCE

    async def test_create_and_get_vehicle(self, db: AsyncSession):
        repo = TrafficRepository(db)

        vehicle = await repo.create_vehicle({
            "vehicle_type": "sedan",
            "model_name": "Toyota Camry",
            "location_x": 50.0,
            "location_y": 50.0,
            "location_z": 0.0,
            "license_plate": "ABC-1234",
        })
        await db.flush()

        fetched = await repo.get_vehicle_by_id(vehicle.id)
        assert fetched is not None
        assert fetched.model_name == "Toyota Camry"

        by_plate = await repo.get_vehicle_by_plate("ABC-1234")
        assert by_plate is not None
        assert by_plate.id == vehicle.id

    async def test_create_and_get_emergency_vehicle(self, db: AsyncSession):
        repo = TrafficRepository(db)

        vehicle = await repo.create_vehicle({
            "vehicle_type": "sedan",
            "model_name": "Police Cruiser",
            "location_x": 0.0,
            "location_y": 0.0,
            "location_z": 0.0,
        })
        await db.flush()

        ev = await repo.create_emergency_vehicle({
            "vehicle_id": vehicle.id,
            "emergency_type": "police",
        })
        await db.flush()

        fetched = await repo.get_emergency_by_id(ev.id)
        assert fetched is not None
        assert fetched.emergency_type == EmergencyVehicleType.POLICE

        by_vid = await repo.get_emergency_by_vehicle_id(vehicle.id)
        assert by_vid is not None

    async def test_create_and_get_statistics(self, db: AsyncSession):
        repo = TrafficRepository(db)

        stats = await repo.create_statistics({
            "total_vehicles_spawned": 100,
            "total_vehicles_despawned": 90,
            "average_speed_kmh": 45.0,
            "peak_density": 30,
            "date_recorded": "2026-01-15",
        })
        await db.flush()

        fetched = await repo.get_statistics_by_id(stats.id)
        assert fetched is not None
        assert fetched.total_vehicles_spawned == 100

        by_date = await repo.get_statistics_by_date("2026-01-15")
        assert len(by_date) >= 1

    async def test_create_and_get_speed_limit(self, db: AsyncSession):
        repo = TrafficRepository(db)

        sl = await repo.create_speed_limit({
            "road_name": "Highway 1",
            "speed_limit_kmh": 120.0,
        })
        await db.flush()

        fetched = await repo.get_speed_limit_by_id(sl.id)
        assert fetched is not None
        assert fetched.speed_limit_kmh == 120.0

    async def test_create_and_get_violation(self, db: AsyncSession):
        repo = TrafficRepository(db)

        v = await repo.create_violation({
            "violation_type": "speeding",
            "speed_kmh": 120.0,
            "speed_limit_kmh": 60.0,
            "fine_amount": 500.0,
        })
        await db.flush()

        fetched = await repo.get_violation_by_id(v.id)
        assert fetched is not None
        assert fetched.violation_type == TrafficViolationType.SPEEDING

    async def test_create_and_get_event(self, db: AsyncSession):
        repo = TrafficRepository(db)

        event = await repo.create_event({
            "event_type": "accident",
            "location_x": 100.0,
            "location_y": 200.0,
            "location_z": 0.0,
            "severity": "high",
            "description": "Multi-car pileup",
        })
        await db.flush()

        fetched = await repo.get_event_by_id(event.id)
        assert fetched is not None
        assert fetched.event_type == TrafficEventType.ACCIDENT
        assert fetched.description == "Multi-car pileup"

    async def test_soft_delete_vehicle(self, db: AsyncSession):
        repo = TrafficRepository(db)

        vehicle = await repo.create_vehicle({
            "vehicle_type": "suv",
            "model_name": "Honda CRV",
            "location_x": 0.0,
            "location_y": 0.0,
            "location_z": 0.0,
        })
        await db.flush()

        result = await repo.soft_delete_vehicle(vehicle.id)
        assert result is True
        assert await repo.get_vehicle_by_id(vehicle.id) is None


# ── Service Tests ──────────────────────────────────────────────────────────────


class TestTrafficService:
    async def test_create_zone(self, db: AsyncSession):
        svc = TrafficService(db)

        zone = await svc.create_zone({
            "zone_name": "Service Zone",
            "zone_type": "city_center",
            "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
            "radius": 500.0,
        })
        assert zone.zone_name == "Service Zone"
        assert zone.zone_type == TrafficZoneType.CITY_CENTER

    async def test_create_zone_invalid_type(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(ValidationError):
            await svc.create_zone({
                "zone_name": "Bad Zone",
                "zone_type": "invalid_type",
                "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
                "radius": 100.0,
            })

    async def test_get_zone_not_found(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(NotFoundError):
            await svc.get_zone(uuid.uuid4())

    async def test_update_zone(self, db: AsyncSession):
        svc = TrafficService(db)

        zone = await svc.create_zone({
            "zone_name": "Old Name",
            "zone_type": "residential",
            "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
            "radius": 200.0,
        })

        updated = await svc.update_zone(zone.id, {"zone_name": "New Name"})
        assert updated.zone_name == "New Name"

    async def test_delete_zone(self, db: AsyncSession):
        svc = TrafficService(db)

        zone = await svc.create_zone({
            "zone_name": "Delete Me",
            "zone_type": "toll_zone",
            "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
            "radius": 100.0,
        })

        result = await svc.delete_zone(zone.id)
        assert result is True

        with pytest.raises(NotFoundError):
            await svc.get_zone(zone.id)

    async def test_create_route(self, db: AsyncSession):
        svc = TrafficService(db)

        route = await svc.create_route({
            "route_name": "Service Route",
            "route_type": "highway",
            "start_x": 0.0, "start_y": 0.0, "start_z": 0.0,
            "end_x": 500.0, "end_y": 0.0, "end_z": 0.0,
            "distance_km": 5.0,
        })
        assert route.route_type == TrafficRouteType.HIGHWAY

    async def test_create_route_invalid_type(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(ValidationError):
            await svc.create_route({
                "route_name": "Bad Route",
                "route_type": "invalid",
                "start_x": 0.0, "start_y": 0.0, "start_z": 0.0,
                "end_x": 100.0, "end_y": 0.0, "end_z": 0.0,
            })

    async def test_create_lane(self, db: AsyncSession):
        svc = TrafficService(db)

        route = await svc.create_route({
            "route_name": "Lane Route",
            "route_type": "city",
            "start_x": 0.0, "start_y": 0.0, "start_z": 0.0,
            "end_x": 100.0, "end_y": 0.0, "end_z": 0.0,
        })

        lane = await svc.create_lane({
            "route_id": route.id,
            "lane_number": 1,
            "direction": "forward",
            "speed_limit_kmh": 60.0,
        })
        assert lane.lane_number == 1

    async def test_create_lane_route_not_found(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(NotFoundError):
            await svc.create_lane({
                "route_id": uuid.uuid4(),
                "lane_number": 1,
            })

    async def test_create_signal(self, db: AsyncSession):
        svc = TrafficService(db)

        signal = await svc.create_signal({
            "signal_name": "Main Signal",
            "location_x": 10.0, "location_y": 20.0, "location_z": 0.0,
            "state": "red",
        })
        assert signal.state == TrafficSignalState.RED

    async def test_change_signal_state(self, db: AsyncSession):
        svc = TrafficService(db)

        signal = await svc.create_signal({
            "signal_name": "Change Me",
            "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
            "state": "green",
        })

        updated = await svc.change_signal_state(signal.id, "red")
        assert updated.state == TrafficSignalState.RED

    async def test_activate_emergency_override(self, db: AsyncSession):
        svc = TrafficService(db)

        signal = await svc.create_signal({
            "signal_name": "Override Signal",
            "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
            "state": "green",
        })

        overridden = await svc.activate_emergency_override(signal.id)
        assert overridden.state == TrafficSignalState.EMERGENCY_OVERRIDE
        assert overridden.is_emergency_override is True

    async def test_deactivate_emergency_override(self, db: AsyncSession):
        svc = TrafficService(db)

        signal = await svc.create_signal({
            "signal_name": "Override Off",
            "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
            "state": "emergency_override",
            "is_emergency_override": True,
        })

        restored = await svc.deactivate_emergency_override(signal.id)
        assert restored.state == TrafficSignalState.GREEN
        assert restored.is_emergency_override is False

    async def test_create_spawn_point(self, db: AsyncSession):
        svc = TrafficService(db)

        sp = await svc.create_spawn_point({
            "spawn_name": "SP South",
            "location_x": 0.0, "location_y": -100.0, "location_z": 0.0,
            "spawn_type": "spawn",
            "max_vehicles": 10,
        })
        assert sp.spawn_name == "SP South"

    async def test_create_density(self, db: AsyncSession):
        svc = TrafficService(db)

        density = await svc.create_density({
            "density_level": "high",
            "vehicle_limit": 40,
            "spawn_rate": 3.0,
        })
        assert density.density_level == TrafficDensityLevel.HIGH

    async def test_create_density_invalid_level(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(ValidationError):
            await svc.create_density({
                "density_level": "mega_ultra_high",
                "vehicle_limit": 100,
                "spawn_rate": 10.0,
            })

    async def test_create_spawn_rule(self, db: AsyncSession):
        svc = TrafficService(db)

        rule = await svc.create_spawn_rule({
            "rule_name": "Scheduled",
            "rule_type": "scheduled",
            "max_spawn_count": 5,
        })
        assert rule.rule_type == SpawnRuleType.SCHEDULED

    async def test_create_spawn_rule_invalid_type(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(ValidationError):
            await svc.create_spawn_rule({
                "rule_name": "Bad Rule",
                "rule_type": "invalid_rule",
            })

    async def test_create_despawn_rule(self, db: AsyncSession):
        svc = TrafficService(db)

        rule = await svc.create_despawn_rule({
            "rule_name": "Time Despawn",
            "rule_type": "time_based",
            "max_lifetime_seconds": 120,
        })
        assert rule.rule_type == DespawnRuleType.TIME_BASED

    async def test_spawn_vehicle(self, db: AsyncSession):
        svc = TrafficService(db)

        vehicle = await svc.spawn_vehicle({
            "vehicle_type": "sedan",
            "model_name": "Honda Civic",
            "location_x": 10.0, "location_y": 20.0, "location_z": 0.0,
        })
        assert vehicle.model_name == "Honda Civic"
        assert vehicle.spawned_at is not None

    async def test_spawn_vehicle_invalid_type(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(ValidationError):
            await svc.spawn_vehicle({
                "vehicle_type": "rocket",
                "model_name": "Falcon 9",
                "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
            })

    async def test_despawn_vehicle(self, db: AsyncSession):
        svc = TrafficService(db)

        vehicle = await svc.spawn_vehicle({
            "vehicle_type": "bus",
            "model_name": "City Bus",
            "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
        })

        result = await svc.despawn_vehicle(vehicle.id)
        assert result is True

        with pytest.raises(NotFoundError):
            await svc.get_vehicle(vehicle.id)

    async def test_register_emergency_vehicle(self, db: AsyncSession):
        svc = TrafficService(db)

        vehicle = await svc.spawn_vehicle({
            "vehicle_type": "sedan",
            "model_name": "Police Charger",
            "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
        })

        ev = await svc.register_emergency_vehicle({
            "vehicle_id": vehicle.id,
            "emergency_type": "police",
        })
        assert ev.emergency_type == EmergencyVehicleType.POLICE

        refreshed = await svc.get_vehicle(vehicle.id)
        assert refreshed.is_emergency is True

    async def test_register_emergency_vehicle_duplicate(self, db: AsyncSession):
        svc = TrafficService(db)

        vehicle = await svc.spawn_vehicle({
            "vehicle_type": "sedan",
            "model_name": "Double Register",
            "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
        })

        await svc.register_emergency_vehicle({
            "vehicle_id": vehicle.id,
            "emergency_type": "ambulance",
        })

        with pytest.raises(ConflictError):
            await svc.register_emergency_vehicle({
                "vehicle_id": vehicle.id,
                "emergency_type": "fire_truck",
            })

    async def test_activate_deactivate_siren(self, db: AsyncSession):
        svc = TrafficService(db)

        vehicle = await svc.spawn_vehicle({
            "vehicle_type": "sedan",
            "model_name": "Siren Car",
            "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
        })

        ev = await svc.register_emergency_vehicle({
            "vehicle_id": vehicle.id,
            "emergency_type": "fire_truck",
        })

        active = await svc.activate_siren(ev.id)
        assert active.siren_on is True
        assert active.is_active_call is True

        inactive = await svc.deactivate_siren(ev.id)
        assert inactive.siren_on is False
        assert inactive.is_active_call is False

    async def test_create_statistics(self, db: AsyncSession):
        svc = TrafficService(db)

        stats = await svc.create_statistics({
            "total_vehicles_spawned": 500,
            "total_vehicles_despawned": 480,
            "average_speed_kmh": 42.5,
            "peak_density": 35,
            "date_recorded": "2026-03-01",
        })
        assert stats.total_vehicles_spawned == 500

    async def test_create_speed_limit(self, db: AsyncSession):
        svc = TrafficService(db)

        sl = await svc.create_speed_limit({
            "road_name": "Interstate 5",
            "speed_limit_kmh": 110.0,
        })
        assert sl.speed_limit_kmh == 110.0

    async def test_create_violation_auto_fine(self, db: AsyncSession):
        svc = TrafficService(db)

        v = await svc.create_violation({
            "violation_type": "speeding",
            "speed_kmh": 130.0,
            "speed_limit_kmh": 60.0,
        })
        assert v.fine_amount == VIOLATION_FINE_AMOUNTS["speeding"]

    async def test_create_violation_custom_fine_preserved(self, db: AsyncSession):
        svc = TrafficService(db)

        v = await svc.create_violation({
            "violation_type": "speeding",
            "fine_amount": 999.0,
        })
        assert v.fine_amount == 999.0

    async def test_create_violation_invalid_type(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(ValidationError):
            await svc.create_violation({
                "violation_type": "flying",
            })

    async def test_resolve_violation(self, db: AsyncSession):
        svc = TrafficService(db)

        v = await svc.create_violation({
            "violation_type": "illegal_parking",
        })

        resolved = await svc.resolve_violation(v.id)
        assert resolved.is_resolved is True

    async def test_create_event(self, db: AsyncSession):
        svc = TrafficService(db)

        event = await svc.create_event({
            "event_type": "road_closure",
            "location_x": 50.0, "location_y": 50.0, "location_z": 0.0,
            "severity": "medium",
            "description": "Construction ahead",
        })
        assert event.event_type == TrafficEventType.ROAD_CLOSURE

    async def test_create_event_invalid_type(self, db: AsyncSession):
        svc = TrafficService(db)

        with pytest.raises(ValidationError):
            await svc.create_event({
                "event_type": "alien_invasion",
                "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
                "severity": "extreme",
            })

    async def test_resolve_event(self, db: AsyncSession):
        svc = TrafficService(db)

        event = await svc.create_event({
            "event_type": "breakdown",
            "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
            "severity": "low",
        })

        resolved = await svc.resolve_event(event.id)
        assert resolved.is_resolved is True

    async def test_list_zones_with_filter(self, db: AsyncSession):
        svc = TrafficService(db)

        await svc.create_zone({
            "zone_name": "Filter HW",
            "zone_type": "highway",
            "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
            "radius": 500.0,
        })
        await svc.create_zone({
            "zone_name": "Filter Res",
            "zone_type": "residential",
            "center_x": 10.0, "center_y": 10.0, "center_z": 0.0,
            "radius": 200.0,
        })

        zones, total = await svc.list_zones(zone_type="highway")
        assert all(z.zone_type == TrafficZoneType.HIGHWAY for z in zones)


# ── API Tests ──────────────────────────────────────────────────────────────────


class TestTrafficAPI:
    async def test_create_zone_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/zones",
            json={
                "zone_name": "API Zone",
                "zone_type": "city_center",
                "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
                "radius": 500.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["zone_name"] == "API Zone"

    async def test_list_zones_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/traffic/zones", headers=auth_headers)
        assert resp.status_code == 200

    async def test_get_zone_api(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/traffic/zones",
            json={
                "zone_name": "Get Zone",
                "zone_type": "residential",
                "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
                "radius": 200.0,
            },
            headers=auth_headers,
        )
        zone_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/traffic/zones/{zone_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["zone_name"] == "Get Zone"

    async def test_update_zone_api(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/traffic/zones",
            json={
                "zone_name": "Old Zone",
                "zone_type": "highway",
                "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
                "radius": 500.0,
            },
            headers=auth_headers,
        )
        zone_id = create_resp.json()["data"]["id"]

        resp = await client.patch(
            f"/api/v1/traffic/zones/{zone_id}",
            json={"zone_name": "Updated Zone"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["zone_name"] == "Updated Zone"

    async def test_delete_zone_api(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/traffic/zones",
            json={
                "zone_name": "Delete Zone",
                "zone_type": "toll_zone",
                "center_x": 0.0, "center_y": 0.0, "center_z": 0.0,
                "radius": 100.0,
            },
            headers=auth_headers,
        )
        zone_id = create_resp.json()["data"]["id"]

        resp = await client.delete(f"/api/v1/traffic/zones/{zone_id}", headers=auth_headers)
        assert resp.status_code == 200

    async def test_create_route_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/routes",
            json={
                "route_name": "API Route",
                "route_type": "highway",
                "start_x": 0.0, "start_y": 0.0, "start_z": 0.0,
                "end_x": 1000.0, "end_y": 0.0, "end_z": 0.0,
                "distance_km": 10.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["route_name"] == "API Route"

    async def test_create_lane_api(self, client: AsyncClient, auth_headers: dict):
        route_resp = await client.post(
            "/api/v1/traffic/routes",
            json={
                "route_name": "Lane Route",
                "route_type": "city",
                "start_x": 0.0, "start_y": 0.0, "start_z": 0.0,
                "end_x": 100.0, "end_y": 0.0, "end_z": 0.0,
            },
            headers=auth_headers,
        )
        route_id = route_resp.json()["data"]["id"]

        resp = await client.post(
            "/api/v1/traffic/lanes",
            json={
                "route_id": route_id,
                "lane_number": 1,
                "direction": "forward",
                "speed_limit_kmh": 50.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["lane_number"] == 1

    async def test_create_signal_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/signals",
            json={
                "signal_name": "API Signal",
                "location_x": 10.0, "location_y": 20.0, "location_z": 0.0,
                "state": "green",
                "cycle_duration_seconds": 30,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["state"] == "green"

    async def test_emergency_override_api(self, client: AsyncClient, auth_headers: dict):
        sig_resp = await client.post(
            "/api/v1/traffic/signals",
            json={
                "signal_name": "Override API",
                "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
                "state": "green",
            },
            headers=auth_headers,
        )
        signal_id = sig_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/traffic/signals/{signal_id}/emergency-on",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["state"] == "emergency_override"

        resp = await client.post(
            f"/api/v1/traffic/signals/{signal_id}/emergency-off",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["state"] == "green"

    async def test_spawn_vehicle_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/vehicles",
            json={
                "vehicle_type": "sedan",
                "model_name": "API Car",
                "location_x": 5.0, "location_y": 10.0, "location_z": 0.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["model_name"] == "API Car"

    async def test_despawn_vehicle_api(self, client: AsyncClient, auth_headers: dict):
        veh_resp = await client.post(
            "/api/v1/traffic/vehicles",
            json={
                "vehicle_type": "suv",
                "model_name": "Despawn Me",
                "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
            },
            headers=auth_headers,
        )
        vehicle_id = veh_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/traffic/vehicles/{vehicle_id}/despawn",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    async def test_create_violation_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/violations",
            json={
                "violation_type": "running_red_light",
                "speed_kmh": 80.0,
                "speed_limit_kmh": 50.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["fine_amount"] == 1000.0

    async def test_resolve_violation_api(self, client: AsyncClient, auth_headers: dict):
        v_resp = await client.post(
            "/api/v1/traffic/violations",
            json={"violation_type": "wrong_lane"},
            headers=auth_headers,
        )
        v_id = v_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/traffic/violations/{v_id}/resolve",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_resolved"] is True

    async def test_create_event_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/events",
            json={
                "event_type": "accident",
                "location_x": 100.0, "location_y": 200.0, "location_z": 0.0,
                "severity": "high",
                "description": "Fender bender",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["event_type"] == "accident"

    async def test_resolve_event_api(self, client: AsyncClient, auth_headers: dict):
        e_resp = await client.post(
            "/api/v1/traffic/events",
            json={
                "event_type": "breakdown",
                "location_x": 0.0, "location_y": 0.0, "location_z": 0.0,
                "severity": "low",
            },
            headers=auth_headers,
        )
        event_id = e_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/traffic/events/{event_id}/resolve",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_resolved"] is True

    async def test_create_statistics_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/statistics",
            json={
                "total_vehicles_spawned": 200,
                "total_vehicles_despawned": 180,
                "average_speed_kmh": 45.0,
                "peak_density": 25,
                "date_recorded": "2026-05-01",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["total_vehicles_spawned"] == 200

    async def test_create_speed_limit_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/speed-limits",
            json={
                "road_name": "API Highway",
                "speed_limit_kmh": 100.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["speed_limit_kmh"] == 100.0

    async def test_create_spawn_rule_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/spawn-rules",
            json={
                "rule_name": "API Spawn",
                "rule_type": "density_based",
                "max_spawn_count": 15,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["rule_type"] == "density_based"

    async def test_create_despawn_rule_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/despawn-rules",
            json={
                "rule_name": "API Despawn",
                "rule_type": "off_screen",
                "max_distance_from_player": 1000.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["rule_type"] == "off_screen"

    async def test_create_density_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/density",
            json={
                "density_level": "rush_hour_evening",
                "vehicle_limit": 60,
                "spawn_rate": 4.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["density_level"] == "rush_hour_evening"

    async def test_create_spawn_point_api(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/traffic/spawn-points",
            json={
                "spawn_name": "API Spawn Point",
                "location_x": 0.0, "location_y": 50.0, "location_z": 0.0,
                "spawn_type": "despawn",
                "max_vehicles": 8,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["spawn_name"] == "API Spawn Point"
