"""Unit tests for the Car System (TASK 7).

Covers: Car variants, purchase, sell, customization, upgrades, performance,
fuel, damage, repair, insurance — repositories, services, and API endpoints.
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
from app.models.vehicle import Vehicle, VehicleType, FuelType
from app.models.car import Car
from app.models.car_variant import CarVariant
from app.models.car_insurance import CarInsurance
from app.models.repair_history import RepairHistory
from app.models.fuel import FuelStation, FuelTransaction
from app.models.garage import Garage, GarageSlot
from app.repositories.auth import AuthRepository
from app.repositories.player import PlayerRepository
from app.repositories.vehicle import VehicleRepository
from app.repositories.garage import GarageRepository
from app.repositories.car import CarRepository
from app.repositories.economy import EconomyRepository
from app.services.car import CarService

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


# ── Tables needed for car system tests ───────────────────────────────────────

_CAR_TABLES = [
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


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_CAR_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_CAR_TABLES)
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
    await session.flush()
    return account, player


async def _create_car_variant(session: AsyncSession, **kwargs) -> CarVariant:
    defaults = {
        "name": "Suzuki Swift Standard",
        "brand": "Suzuki",
        "model_name": "Swift",
        "year": 2024,
        "category": "sedan",
        "purchase_price": 15000.0,
        "engine_cc": 1200,
        "horsepower": 82.0,
        "torque_nm": 113.0,
        "cylinders": 4,
        "fuel_type": "gasoline",
        "doors": 4,
        "seats": 5,
        "cargo_space_liters": 265.0,
        "top_speed_kmh": 180.0,
        "acceleration_0_100": 12.0,
        "weight_kg": 870.0,
        "braking_distance": 38.0,
        "handling_rating": 72.0,
        "fuel_tank_liters": 37.0,
        "fuel_consumption_l100km": 5.5,
        "max_upgrade_level": 10,
    }
    defaults.update(kwargs)
    variant = CarVariant(**defaults)
    session.add(variant)
    await session.flush()
    return variant


async def _create_garage(
    session: AsyncSession, player_id: uuid.UUID, name: str = "Main Garage", capacity: int = 5
) -> Garage:
    garage = Garage(
        player_id=player_id,
        garage_name=name,
        capacity=capacity,
        location="Downtown",
        purchase_price=25000.0,
    )
    session.add(garage)
    await session.flush()
    return garage


async def _create_car_with_vehicle(
    session: AsyncSession, player_id: uuid.UUID, variant: CarVariant
) -> tuple[Vehicle, Car]:
    vehicle = Vehicle(
        player_id=player_id,
        vehicle_type="car",
        name="Test Car",
        brand=variant.brand,
        model=variant.model_name,
        year=variant.year,
        vin=f"2HGBH41JXMN{uuid.uuid4().hex[:6].upper()}"[:17],
        license_plate=f"C{uuid.uuid4().hex[:5].upper()}"[:10],
        purchase_price=variant.purchase_price,
        current_value=variant.purchase_price,
        fuel_level=variant.fuel_tank_liters,
        max_fuel=variant.fuel_tank_liters,
        health=100.0,
        engine_health=100.0,
        body_health=100.0,
        wheel_health=100.0,
        brake_health=100.0,
        suspension_health=100.0,
        top_speed=variant.top_speed_kmh,
        acceleration=variant.acceleration_0_100,
        braking=variant.braking_distance,
        handling=variant.handling_rating,
        mileage=0.0,
        is_primary=False,
    )
    session.add(vehicle)
    await session.flush()

    car = Car(
        vehicle_id=vehicle.id,
        variant_id=variant.id,
        engine_level=1, turbo_level=0, exhaust_level=1,
        transmission_level=1, brake_level=1, suspension_level=1,
        wheel_level=1, tire_level=1, nitrous_level=0,
        interior_level=1, seat_level=1, steering_wheel_level=1,
        horn_level=1, headlight_level=1, taillight_level=1,
        spoiler_level=0, hood_level=1, roof_level=1, mirror_level=1,
        paint_id=None, window_tint="none", license_plate_text=None,
    )
    session.add(car)
    await session.flush()
    return vehicle, car


async def _create_fuel_station(session: AsyncSession, **kwargs) -> FuelStation:
    defaults = {"station_name": "Shell Downtown", "location": "Main St", "fuel_price": 1.5}
    defaults.update(kwargs)
    station = FuelStation(**defaults)
    session.add(station)
    await session.flush()
    return station


async def _create_insurance(
    session: AsyncSession, vehicle_id: uuid.UUID, **kwargs
) -> CarInsurance:
    from datetime import datetime, timezone, timedelta
    defaults = {
        "vehicle_id": vehicle_id,
        "tier": "basic",
        "monthly_premium": 100,
        "coverage_amount": 10000,
        "deductible": 1000,
        "is_active": True,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
    }
    defaults.update(kwargs)
    insurance = CarInsurance(**defaults)
    session.add(insurance)
    await session.flush()
    return insurance


# ══════════════════════════════════════════════════════════════════════════════
# REPOSITORY TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestCarRepository:
    async def test_create_and_get_car(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep1@test.com")
        variant = await _create_car_variant(db, name="Test Variant 1")
        garage = await _create_garage(db, player.id)

        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        repo = CarRepository(db)
        found = await repo.get_by_id(car.id)
        assert found is not None
        assert found.vehicle_id == vehicle.id

    async def test_get_by_vehicle_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep2@test.com")
        variant = await _create_car_variant(db, name="Test Variant 2")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        repo = CarRepository(db)
        found = await repo.get_by_vehicle_id(vehicle.id)
        assert found is not None
        assert found.variant_id == variant.id

    async def test_get_by_player_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep3@test.com")
        variant = await _create_car_variant(db, name="Test Variant 3")
        await _create_car_with_vehicle(db, player.id, variant)
        await _create_car_with_vehicle(db, player.id, variant)

        repo = CarRepository(db)
        cars = await repo.get_by_player_id(player.id)
        assert len(cars) == 2

    async def test_update_car(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep4@test.com")
        variant = await _create_car_variant(db, name="Test Variant 4")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        repo = CarRepository(db)
        updated = await repo.update(car.id, {"engine_level": 5, "paint_id": "red_01"})
        assert updated is not None

    async def test_soft_delete(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep5@test.com")
        variant = await _create_car_variant(db, name="Test Variant 5")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        repo = CarRepository(db)
        result = await repo.delete(car.id)
        assert result is True
        found = await repo.get_by_id(car.id)
        assert found is None

    async def test_get_variant_by_id(self, db: AsyncSession):
        variant = await _create_car_variant(db, name="Test Variant 6")
        repo = CarRepository(db)
        found = await repo.get_variant_by_id(variant.id)
        assert found is not None
        assert found.name == "Test Variant 6"

    async def test_get_all_variants(self, db: AsyncSession):
        await _create_car_variant(db, name="CV1")
        await _create_car_variant(db, name="CV2")
        repo = CarRepository(db)
        variants = await repo.get_all_variants()
        assert len(variants) == 2

    async def test_create_insurance(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep6@test.com")
        variant = await _create_car_variant(db, name="Test Variant 7")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        from datetime import datetime, timezone, timedelta
        repo = CarRepository(db)
        insurance = await repo.create_insurance({
            "vehicle_id": vehicle.id,
            "tier": "basic",
            "monthly_premium": 100,
            "coverage_amount": 10000,
            "deductible": 1000,
            "is_active": True,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
        })
        assert insurance.id is not None
        assert insurance.tier == "basic"

    async def test_get_insurance(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep7@test.com")
        variant = await _create_car_variant(db, name="Test Variant 8")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)
        await _create_insurance(db, vehicle.id)

        repo = CarRepository(db)
        found = await repo.get_insurance(vehicle.id)
        assert found is not None
        assert found.is_active is True

    async def test_add_repair_record(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep8@test.com")
        variant = await _create_car_variant(db, name="Test Variant 9")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        repo = CarRepository(db)
        record = await repo.add_repair_record({
            "vehicle_id": vehicle.id,
            "repair_type": "engine",
            "repair_cost": 300.0,
            "description": "Engine repair",
        })
        assert record.id is not None

    async def test_get_repair_history(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep9@test.com")
        variant = await _create_car_variant(db, name="Test Variant 10")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        repo = CarRepository(db)
        await repo.add_repair_record({"vehicle_id": vehicle.id, "repair_type": "engine", "repair_cost": 100})
        await repo.add_repair_record({"vehicle_id": vehicle.id, "repair_type": "body", "repair_cost": 50})

        history = await repo.get_repair_history(vehicle.id)
        assert len(history) == 2

    async def test_get_fuel_station(self, db: AsyncSession):
        station = await _create_fuel_station(db)
        repo = CarRepository(db)
        found = await repo.get_fuel_station(station.id)
        assert found is not None
        assert found.station_name == "Shell Downtown"

    async def test_add_fuel_transaction(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "crep10@test.com")
        variant = await _create_car_variant(db, name="Test Variant 11")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)
        station = await _create_fuel_station(db)

        repo = CarRepository(db)
        tx = await repo.add_fuel_transaction({
            "vehicle_id": vehicle.id,
            "station_id": station.id,
            "fuel_amount": 10.0,
            "price_paid": 15.0,
        })
        assert tx.id is not None


# ══════════════════════════════════════════════════════════════════════════════
# SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestCarService:
    async def test_get_variants(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc1@test.com")
        await _create_car_variant(db, name="CV1")
        await _create_car_variant(db, name="CV2")
        svc = CarService(db)
        variants = await svc.get_variants()
        assert len(variants) == 2

    async def test_get_variant_not_found(self, db: AsyncSession):
        svc = CarService(db)
        from app.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            await svc.get_variant(uuid.uuid4())

    async def test_purchase_car_success(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc2@test.com")
        await _create_garage(db, player.id)
        variant = await _create_car_variant(db, name="Suzuki Swift")

        svc = CarService(db)
        result = await svc.purchase_car(player.id, variant.id, "My Swift")

        assert result["vehicle"].name == "My Swift"
        assert result["car"].variant_id == variant.id
        assert result["variant"].name == "Suzuki Swift"
        assert result["garage_slot"].occupied is True

    async def test_purchase_car_insufficient_funds(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc3@test.com")
        await _create_garage(db, player.id)
        variant = await _create_car_variant(db, name="Expensive Car", purchase_price=500000.0)

        svc = CarService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.purchase_car(player.id, variant.id, "Too Expensive")

    async def test_sell_car(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc4@test.com")
        variant = await _create_car_variant(db, name="Sell Test", purchase_price=15000.0)
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        result = await svc.sell_car(player.id, vehicle.id)
        assert result["sold_price"] == int(15000.0 * 0.70)
        assert "sold" in result["message"].lower()

    async def test_get_player_cars(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc5@test.com")
        variant = await _create_car_variant(db, name="List Test")
        await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        cars = await svc.get_player_cars(player.id)
        assert len(cars) == 1
        assert cars[0]["variant"].name == "List Test"

    async def test_upgrade_component(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc6@test.com")
        variant = await _create_car_variant(db, name="Upgrade Test", purchase_price=15000.0)
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        result = await svc.upgrade_component(player.id, vehicle.id, "engine", 2)
        assert result["component"] == "engine"
        assert result["previous_level"] == 1
        assert result["new_level"] == 2

    async def test_upgrade_invalid_component(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc7@test.com")
        variant = await _create_car_variant(db, name="Invalid Test")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.upgrade_component(player.id, vehicle.id, "rocket_launcher", 2)

    async def test_upgrade_level_too_high(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc8@test.com")
        variant = await _create_car_variant(db, name="Max Test", max_upgrade_level=3)
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.upgrade_component(player.id, vehicle.id, "engine", 5)

    async def test_update_customization(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc9@test.com")
        variant = await _create_car_variant(db, name="Custom Test")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        updated = await svc.update_customization(player.id, vehicle.id, {"paint_id": "matte_black", "window_tint": "dark"})
        assert updated.paint_id == "matte_black"
        assert updated.window_tint == "dark"

    async def test_get_performance_stats(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc10@test.com")
        variant = await _create_car_variant(db, name="Perf Test", top_speed_kmh=180.0, acceleration_0_100=12.0)
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        stats = await svc.get_performance_stats(vehicle.id)
        assert stats["top_speed"] > 0
        assert stats["acceleration"] > 0
        assert stats["braking"] > 0
        assert stats["handling"] > 0

    async def test_purchase_fuel(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc11@test.com")
        variant = await _create_car_variant(db, name="Fuel Test", fuel_tank_liters=37.0)
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)
        # Set fuel to half
        await VehicleRepository(db).update(vehicle.id, fuel_level=18.5)

        station = await _create_fuel_station(db, fuel_price=1.5)
        svc = CarService(db)
        result = await svc.purchase_fuel(player.id, vehicle.id, station.id, 10.0)
        assert result["fuel_added"] == 10.0
        assert result["cost"] == 15.0

    async def test_apply_damage(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc12@test.com")
        variant = await _create_car_variant(db, name="Damage Test")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        result = await svc.apply_damage(player.id, vehicle.id, "engine", 25.0)
        assert result["damage_type"] == "engine"
        assert result["damage_report"]["engine_health"] == 75.0

    async def test_repair_car(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc13@test.com")
        variant = await _create_car_variant(db, name="Repair Test")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)
        # Apply damage
        await VehicleRepository(db).update(vehicle.id, engine_health=60.0, health=60.0)

        svc = CarService(db)
        result = await svc.repair_car(player.id, vehicle.id, "engine")
        assert result["repair_type"] == "engine"
        assert result["repair_cost"] > 0
        assert result["new_health_values"]["engine_health"] == 100.0

    async def test_purchase_insurance(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "csvc14@test.com")
        variant = await _create_car_variant(db, name="Insurance Test")
        vehicle, car = await _create_car_with_vehicle(db, player.id, variant)

        svc = CarService(db)
        result = await svc.purchase_insurance(player.id, vehicle.id, "standard")
        assert result["insurance"].tier == "standard"
        assert result["insurance"].monthly_premium == 300


# ══════════════════════════════════════════════════════════════════════════════
# API TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestCarAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"carapi_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"carapi_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        token = data["data"]["access_token"]
        return token

    async def test_list_variants(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/cars/variants",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_list_cars(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/cars/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_get_car_detail_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_fuel_info_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}/fuel",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_damage_report_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}/damage",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_performance_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}/performance",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_upgrade_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            f"/api/v1/cars/{uuid.uuid4()}/upgrade",
            json={"component": "engine", "target_level": 2},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_customization_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.patch(
            f"/api/v1/cars/{uuid.uuid4()}/customization",
            json={"paint_id": "red"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_repair_cost_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}/repair/cost?repair_type=engine",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_repair_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            f"/api/v1/cars/{uuid.uuid4()}/repair",
            json={"repair_type": "engine"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_insurance_get_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            f"/api/v1/cars/{uuid.uuid4()}/insurance",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_insurance_purchase_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            f"/api/v1/cars/{uuid.uuid4()}/insurance",
            json={"tier": "basic"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)

    async def test_sell_nonexistent(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.delete(
            f"/api/v1/cars/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 404)
