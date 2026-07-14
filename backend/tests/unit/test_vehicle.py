"""Unit tests for the Vehicle & Garage System (TASK 5).

Covers: Vehicle CRUD, bike/car sub-records, garage storage, ownership
validation — repositories, services, and API endpoints.
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
from app.models.bike import Bike
from app.models.car import Car
from app.models.garage import Garage, GarageSlot
from app.repositories.auth import AuthRepository
from app.repositories.player import PlayerRepository
from app.repositories.vehicle import VehicleRepository
from app.repositories.garage import GarageRepository
from app.services.vehicle import VehicleService
from app.services.garage import GarageService

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


# ── Tables needed for vehicle system tests ────────────────────────────────────

_VEHICLE_TABLES = [
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
        "bikes",
        "cars",
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
        await conn.run_sync(Base.metadata.create_all, tables=_VEHICLE_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_VEHICLE_TABLES)
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


async def _create_player_with_account(
    session: AsyncSession, email: str = "player@test.com"
) -> tuple[PlayerAccount, Player]:
    """Helper: create an account + player, stats, settings, wallet, inventory."""
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
        cash=50000.0,
    )
    session.add(player)
    await session.flush()

    stats = PlayerStatistics(player_id=player.id)
    session.add(stats)
    settings = PlayerSettings(player_id=player.id)
    session.add(settings)
    wallet = Wallet(player_id=player.id, cash=50000.0, bank_balance=0.0)
    session.add(wallet)
    inventory = Inventory(player_id=player.id, max_slots=50, used_slots=0, total_weight=0.0)
    session.add(inventory)
    await session.flush()
    return account, player


def _vin(seed: str) -> str:
    """Return a 17-char VIN from a short seed string."""
    return f"1HGBH41JXMN{seed.upper():<6}"[:17]


def _plate(seed: str) -> str:
    """Return a short plate string."""
    return f"P{seed.upper()}"[:10]


async def _create_vehicle(
    session: AsyncSession,
    player_id: uuid.UUID,
    vehicle_type: VehicleType = VehicleType.CAR,
    brand: str = "Toyota",
    model: str = "Supra",
    year: int = 2024,
) -> Vehicle:
    """Helper: create a vehicle and its sub-record."""
    vehicle = Vehicle(
        player_id=player_id,
        vehicle_type=vehicle_type,
        brand=brand,
        model=model,
        year=year,
        vin=_vin(str(uuid.uuid4().hex[:6])),
        license_plate=_plate(str(uuid.uuid4().hex[:5])),
        purchase_price=50000.0,
        current_value=45000.0,
    )
    session.add(vehicle)
    await session.flush()

    if vehicle_type == VehicleType.BIKE:
        bike = Bike(vehicle_id=vehicle.id)
        session.add(bike)
    elif vehicle_type == VehicleType.CAR:
        car = Car(vehicle_id=vehicle.id)
        session.add(car)
    await session.flush()
    return vehicle


async def _create_garage(
    session: AsyncSession,
    player_id: uuid.UUID,
    name: str = "Main Garage",
    capacity: int = 5,
) -> Garage:
    """Helper: create a garage."""
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


# ══════════════════════════════════════════════════════════════════════════════
# REPOSITORY TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestVehicleRepository:
    async def test_create_and_get(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "veh1@test.com")
        repo = VehicleRepository(db)
        vehicle = await repo.create(
            player_id=player.id,
            vehicle_type=VehicleType.CAR,
            brand="Honda",
            model="Civic",
            year=2023,
            vin=_vin("V001"),
            license_plate=_plate("R001"),
            purchase_price=25000.0,
            current_value=25000.0,
        )
        assert vehicle.id is not None
        found = await repo.get_by_id(vehicle.id)
        assert found is not None
        assert found.brand == "Honda"

    async def test_get_by_player_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "veh2@test.com")
        repo = VehicleRepository(db)
        await repo.create(
            player_id=player.id,
            vehicle_type=VehicleType.CAR,
            brand="Toyota", model="Supra", year=2024,
            vin=_vin("V002A"), license_plate=_plate("R002A"),
            purchase_price=50000.0, current_value=50000.0,
        )
        await repo.create(
            player_id=player.id,
            vehicle_type=VehicleType.BIKE,
            brand="Yamaha", model="R1", year=2023,
            vin=_vin("V002B"), license_plate=_plate("R002B"),
            purchase_price=15000.0, current_value=15000.0,
        )
        vehicles = await repo.get_by_player_id(player.id)
        assert len(vehicles) == 2

    async def test_update(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "veh3@test.com")
        repo = VehicleRepository(db)
        vehicle = await repo.create(
            player_id=player.id,
            vehicle_type=VehicleType.CAR,
            brand="Ford", model="Mustang", year=2024,
            vin=_vin("V003"), license_plate=_plate("R003"),
            purchase_price=40000.0, current_value=40000.0,
        )
        updated = await repo.update(vehicle.id, license_plate="NEW01")
        assert updated is not None
        assert updated.license_plate == "NEW01"

    async def test_soft_delete(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "veh4@test.com")
        repo = VehicleRepository(db)
        vehicle = await repo.create(
            player_id=player.id,
            vehicle_type=VehicleType.BIKE,
            brand="Kawasaki", model="Ninja", year=2024,
            vin=_vin("V004"), license_plate=_plate("R004"),
            purchase_price=12000.0, current_value=12000.0,
        )
        result = await repo.soft_delete(vehicle.id)
        assert result is True
        found = await repo.get_by_id(vehicle.id)
        assert found is None

    async def test_get_bike(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "veh5@test.com")
        vehicle = await _create_vehicle(db, player.id, VehicleType.BIKE)
        repo = VehicleRepository(db)
        bike = await repo.get_bike(vehicle.id)
        assert bike is not None
        assert bike.engine_level == 1

    async def test_get_car(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "veh6@test.com")
        vehicle = await _create_vehicle(db, player.id, VehicleType.CAR)
        repo = VehicleRepository(db)
        car = await repo.get_car(vehicle.id)
        assert car is not None
        assert car.engine_level == 1


class TestGarageRepository:
    async def test_create_and_get(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "g1@test.com")
        repo = GarageRepository(db)
        garage = await repo.create(
            player_id=player.id,
            garage_name="My Garage",
            capacity=5,
            location="Downtown",
            purchase_price=25000.0,
        )
        assert garage.id is not None
        found = await repo.get_by_id(garage.id)
        assert found is not None
        assert found.garage_name == "My Garage"

    async def test_get_by_player_id(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "g2@test.com")
        repo = GarageRepository(db)
        await repo.create(
            player_id=player.id, garage_name="G1",
            capacity=5, purchase_price=25000.0,
        )
        await repo.create(
            player_id=player.id, garage_name="G2",
            capacity=10, purchase_price=50000.0,
        )
        garages = await repo.get_by_player_id(player.id)
        assert len(garages) == 2

    async def test_get_slots(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "g3@test.com")
        garage = await _create_garage(db, player.id)
        repo = GarageRepository(db)
        slots = await repo.get_slots(garage.id)
        assert len(slots) == 0

    async def test_soft_delete(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "g4@test.com")
        repo = GarageRepository(db)
        garage = await repo.create(
            player_id=player.id, garage_name="DelGarage",
            capacity=3, purchase_price=10000.0,
        )
        result = await repo.soft_delete(garage.id)
        assert result is True
        found = await repo.get_by_id(garage.id)
        assert found is None


# ══════════════════════════════════════════════════════════════════════════════
# SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestVehicleService:
    async def test_buy_car(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc1@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        result = await svc.buy_vehicle(
            account.id, "car", "Toyota", "Supra", 2024,
            _vin("S001"), _plate("S001"), 50000.0,
        )
        assert result["brand"] == "Toyota"
        assert result["vehicle_type"] == VehicleType.CAR
        assert result["car"] is not None
        assert result["bike"] is None

    async def test_buy_bike(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc2@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        result = await svc.buy_vehicle(
            account.id, "bike", "Yamaha", "R1", 2023,
            _vin("S002"), _plate("S002"), 15000.0,
        )
        assert result["vehicle_type"] == VehicleType.BIKE
        assert result["bike"] is not None
        assert result["car"] is None

    async def test_buy_invalid_type(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc3@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.buy_vehicle(
                account.id, "airplane", "Boeing", "747", 2024,
                _vin("S003"), _plate("S003"), 100000.0,
            )

    async def test_get_vehicles(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc4@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        await svc.buy_vehicle(
            account.id, "car", "Honda", "Civic", 2023,
            _vin("S004"), _plate("S004"), 25000.0,
        )
        vehicles = await svc.get_vehicles(account.id)
        assert len(vehicles) == 1

    async def test_get_vehicle_detail(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc5@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        result = await svc.buy_vehicle(
            account.id, "car", "Ford", "Mustang", 2024,
            _vin("S005"), _plate("S005"), 40000.0,
        )
        detail = await svc.get_vehicle(account.id, result["id"])
        assert detail["brand"] == "Ford"
        assert detail["car"]["engine_level"] == 1

    async def test_sell_vehicle(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc6@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        result = await svc.buy_vehicle(
            account.id, "car", "Nissan", "GTR", 2024,
            _vin("S006"), _plate("S006"), 120000.0,
        )
        sold = await svc.sell_vehicle(account.id, result["id"])
        assert sold["sold_price"] == 120000.0

    async def test_update_vehicle(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc7@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        result = await svc.buy_vehicle(
            account.id, "car", "BMW", "M4", 2024,
            _vin("S007"), _plate("S007"), 80000.0,
        )
        updated = await svc.update_vehicle(
            account.id, result["id"], license_plate="NEWWW"
        )
        assert updated["license_plate"] == "NEWWW"

    async def test_store_in_garage(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc8@test.com")
        vehicle_repo = VehicleRepository(db)
        garage_repo = GarageRepository(db)
        svc = VehicleService(PlayerRepository(db), vehicle_repo, garage_repo)

        result = await svc.buy_vehicle(
            account.id, "car", "Audi", "R8", 2024,
            _vin("S008"), _plate("S008"), 150000.0,
        )
        garage = await _create_garage(db, player.id, "My Garage")

        stored = await svc.store_in_garage(account.id, result["id"], garage.id)
        assert stored["garage_id"] == garage.id

    async def test_store_full_garage(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc9@test.com")
        vehicle_repo = VehicleRepository(db)
        garage_repo = GarageRepository(db)
        svc = VehicleService(PlayerRepository(db), vehicle_repo, garage_repo)

        garage = await _create_garage(db, player.id, "Tiny Garage", capacity=1)
        v1 = await svc.buy_vehicle(
            account.id, "car", "A", "B", 2024,
            _vin("S009A"), _plate("S09A"), 10000.0,
        )
        v2 = await svc.buy_vehicle(
            account.id, "car", "C", "D", 2024,
            _vin("S009B"), _plate("S09B"), 10000.0,
        )
        await svc.store_in_garage(account.id, v1["id"], garage.id)

        from app.core.exceptions import ConflictError
        with pytest.raises(ConflictError):
            await svc.store_in_garage(account.id, v2["id"], garage.id)

    async def test_remove_from_garage(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc10@test.com")
        vehicle_repo = VehicleRepository(db)
        garage_repo = GarageRepository(db)
        svc = VehicleService(PlayerRepository(db), vehicle_repo, garage_repo)

        result = await svc.buy_vehicle(
            account.id, "car", "Tesla", "ModelS", 2024,
            _vin("S010"), _plate("S010"), 90000.0,
        )
        garage = await _create_garage(db, player.id, "Tesla Garage")
        await svc.store_in_garage(account.id, result["id"], garage.id)

        removed = await svc.remove_from_garage(account.id, result["id"])
        assert removed["garage_id"] is None

    async def test_remove_not_in_garage(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "svc11@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        result = await svc.buy_vehicle(
            account.id, "car", "X", "Y", 2024,
            _vin("S011"), _plate("S011"), 50000.0,
        )
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await svc.remove_from_garage(account.id, result["id"])

    async def test_ownership_violation(self, db: AsyncSession):
        account1, player1 = await _create_player_with_account(db, "svc_own1@test.com")
        account2, player2 = await _create_player_with_account(db, "svc_own2@test.com")
        svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        result = await svc.buy_vehicle(
            account1.id, "car", "X", "Y", 2024,
            _vin("SOWN"), _plate("SOWN"), 50000.0,
        )
        from app.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            await svc.get_vehicle(account2.id, result["id"])


class TestGarageService:
    async def test_create_garage(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "gsvc1@test.com")
        svc = GarageService(PlayerRepository(db), GarageRepository(db))
        result = await svc.create_garage(account.id, "My Garage", "Downtown", 25000.0)
        assert result["garage_name"] == "My Garage"
        assert result["capacity"] == 5

    async def test_get_garages(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "gsvc2@test.com")
        svc = GarageService(PlayerRepository(db), GarageRepository(db))
        await svc.create_garage(account.id, "G1 Garage", "Downtown", 25000.0)
        await svc.create_garage(account.id, "G2 Garage", "Uptown", 50000.0)
        garages = await svc.get_garages(account.id)
        assert len(garages) == 2

    async def test_store_and_retrieve_vehicle(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "gsvc3@test.com")
        v_svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        g_svc = GarageService(PlayerRepository(db), GarageRepository(db))

        vehicle = await v_svc.buy_vehicle(
            account.id, "car", "Porsche", "911", 2024,
            _vin("GS03"), _plate("GS03"), 180000.0,
        )
        garage = await g_svc.create_garage(account.id, "Luxury Garage", "Ritz", 100000.0)

        stored = await g_svc.store_vehicle(account.id, garage["id"], vehicle["id"])
        assert stored["garage_name"] == "Luxury Garage"

        retrieved = await g_svc.retrieve_vehicle(account.id, garage["id"], vehicle["id"])
        assert retrieved["vehicle"]["garage_id"] is None

    async def test_store_nonexistent_garage(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "gsvc4@test.com")
        v_svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        g_svc = GarageService(PlayerRepository(db), GarageRepository(db))

        vehicle = await v_svc.buy_vehicle(
            account.id, "car", "X", "Y", 2024,
            _vin("GS04"), _plate("GS04"), 50000.0,
        )
        from app.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            await g_svc.store_vehicle(account.id, uuid.uuid4(), vehicle["id"])

    async def test_store_already_stored(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "gsvc5@test.com")
        v_svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        g_svc = GarageService(PlayerRepository(db), GarageRepository(db))

        vehicle = await v_svc.buy_vehicle(
            account.id, "car", "X", "Y", 2024,
            _vin("GS05"), _plate("GS05"), 50000.0,
        )
        garage = await g_svc.create_garage(account.id, "Test Garage", "Loc", 10000.0)
        await g_svc.store_vehicle(account.id, garage["id"], vehicle["id"])

        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await g_svc.store_vehicle(account.id, garage["id"], vehicle["id"])

    async def test_retrieve_not_stored(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, "gsvc6@test.com")
        v_svc = VehicleService(
            PlayerRepository(db), VehicleRepository(db), GarageRepository(db)
        )
        g_svc = GarageService(PlayerRepository(db), GarageRepository(db))

        vehicle = await v_svc.buy_vehicle(
            account.id, "car", "X", "Y", 2024,
            _vin("GS06"), _plate("GS06"), 50000.0,
        )
        garage = await g_svc.create_garage(account.id, "Test Garage", "Loc", 10000.0)

        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            await g_svc.retrieve_vehicle(account.id, garage["id"], vehicle["id"])

    async def test_ownership_violation(self, db: AsyncSession):
        account1, player1 = await _create_player_with_account(db, "gsvc_own1@test.com")
        account2, player2 = await _create_player_with_account(db, "gsvc_own2@test.com")
        g_svc = GarageService(PlayerRepository(db), GarageRepository(db))

        garage = await g_svc.create_garage(account1.id, "Owner Garage", "Loc", 10000.0)
        from app.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            await g_svc.get_garage(account2.id, garage["id"])


# ══════════════════════════════════════════════════════════════════════════════
# API TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestVehicleAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"vehapi_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"vehapi_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    def _buy_payload(self, suffix: str) -> dict:
        return {
            "vehicle_type": "car",
            "brand": "Toyota",
            "model": "Supra",
            "year": 2024,
            "vin": _vin(f"A{suffix}"),
            "license_plate": _plate(f"A{suffix}"),
            "purchase_price": 50000.0,
        }

    async def test_list_vehicles_empty(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    async def test_buy_car_returns_201(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
            json=self._buy_payload("BC1"),
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["vehicle"]["brand"] == "Toyota"
        assert data["car"] is not None
        assert data["bike"] is None

    async def test_buy_bike_returns_201(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_type": "bike",
                "brand": "Yamaha",
                "model": "R1",
                "year": 2023,
                "vin": _vin("BB02X"),
                "license_plate": _plate("BB02"),
                "purchase_price": 15000.0,
            },
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["vehicle"]["vehicle_type"] == "bike"
        assert data["bike"] is not None
        assert data["car"] is None

    async def test_get_vehicle_detail(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        buy_resp = await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_type": "car",
                "brand": "Honda",
                "model": "Civic",
                "year": 2023,
                "vin": _vin("GD03X"),
                "license_plate": _plate("GD03"),
                "purchase_price": 25000.0,
            },
        )
        vehicle_id = buy_resp.json()["data"]["vehicle"]["id"]
        resp = await client.get(
            f"/api/v1/vehicles/{vehicle_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["vehicle"]["brand"] == "Honda"

    async def test_update_vehicle(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        buy_resp = await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_type": "car",
                "brand": "Ford",
                "model": "Mustang",
                "year": 2024,
                "vin": _vin("UP04X"),
                "license_plate": _plate("UP04"),
                "purchase_price": 40000.0,
            },
        )
        vehicle_id = buy_resp.json()["data"]["vehicle"]["id"]
        resp = await client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"license_plate": "NEW04"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["vehicle"]["license_plate"] == "NEW04"

    async def test_sell_vehicle(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        buy_resp = await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_type": "car",
                "brand": "BMW",
                "model": "M4",
                "year": 2024,
                "vin": _vin("SV05X"),
                "license_plate": _plate("SV05"),
                "purchase_price": 80000.0,
            },
        )
        vehicle_id = buy_resp.json()["data"]["vehicle"]["id"]
        resp = await client.delete(
            f"/api/v1/vehicles/{vehicle_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    async def test_list_vehicles_after_buy(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_type": "car",
                "brand": "Tesla",
                "model": "Model 3",
                "year": 2024,
                "vin": _vin("LV06"),
                "license_plate": _plate("LV06"),
                "purchase_price": 45000.0,
            },
        )
        resp = await client.get(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1

    async def test_store_and_remove_garage(self, client: AsyncClient):
        token = await self._register_and_get_token(client)

        buy_resp = await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_type": "car",
                "brand": "Audi",
                "model": "R8",
                "year": 2024,
                "vin": _vin("SR07X"),
                "license_plate": _plate("SR07"),
                "purchase_price": 150000.0,
            },
        )
        vehicle_id = buy_resp.json()["data"]["vehicle"]["id"]

        garage_resp = await client.post(
            "/api/v1/garages/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "garage_name": "API Garage",
                "location": "Downtown",
                "purchase_price": 25000.0,
            },
        )
        garage_id = garage_resp.json()["data"]["id"]

        store_resp = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/garage/store?garage_id={garage_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert store_resp.status_code == 200
        assert store_resp.json()["data"]["vehicle"]["garage_id"] == garage_id

        remove_resp = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/garage/remove",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert remove_resp.status_code == 200
        assert remove_resp.json()["data"]["vehicle"]["garage_id"] is None

    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/vehicles/")
        assert resp.status_code == 401

    async def test_ownership_violation_returns_404(self, client: AsyncClient):
        token1 = await self._register_and_get_token(client)
        token2 = await self._register_and_get_token(client)

        buy_resp = await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "vehicle_type": "car",
                "brand": "X",
                "model": "Y",
                "year": 2024,
                "vin": _vin("OW08X"),
                "license_plate": _plate("OW08"),
                "purchase_price": 50000.0,
            },
        )
        vehicle_id = buy_resp.json()["data"]["vehicle"]["id"]

        resp = await client.get(
            f"/api/v1/vehicles/{vehicle_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert resp.status_code == 404


class TestGarageAPI:
    async def _register_and_get_token(self, client: AsyncClient) -> str:
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"gapi_{uuid.uuid4().hex[:8]}@test.com",
                "username": f"gapi_{uuid.uuid4().hex[:8]}",
                "password": "StrongPass1!",
            },
        )
        return resp.json()["data"]["access_token"]

    async def test_list_garages_empty(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.get(
            "/api/v1/garages/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    async def test_create_garage_returns_201(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        resp = await client.post(
            "/api/v1/garages/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "garage_name": "Test Garage",
                "location": "Downtown",
                "purchase_price": 25000.0,
            },
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["garage_name"] == "Test Garage"

    async def test_get_garage(self, client: AsyncClient):
        token = await self._register_and_get_token(client)
        create_resp = await client.post(
            "/api/v1/garages/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "garage_name": "My Garage",
                "location": "Uptown",
                "purchase_price": 30000.0,
            },
        )
        garage_id = create_resp.json()["data"]["id"]
        resp = await client.get(
            f"/api/v1/garages/{garage_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["garage_name"] == "My Garage"

    async def test_store_and_retrieve(self, client: AsyncClient):
        token = await self._register_and_get_token(client)

        buy_resp = await client.post(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_type": "car",
                "brand": "Porsche",
                "model": "911",
                "year": 2024,
                "vin": _vin("GS10X"),
                "license_plate": _plate("GS10"),
                "purchase_price": 180000.0,
            },
        )
        vehicle_id = buy_resp.json()["data"]["vehicle"]["id"]

        garage_resp = await client.post(
            "/api/v1/garages/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "garage_name": "Luxury Garage",
                "purchase_price": 100000.0,
            },
        )
        garage_id = garage_resp.json()["data"]["id"]

        store_resp = await client.post(
            "/api/v1/garages/store",
            headers={"Authorization": f"Bearer {token}"},
            json={"garage_id": garage_id, "vehicle_id": vehicle_id},
        )
        assert store_resp.status_code == 200

        retrieve_resp = await client.post(
            "/api/v1/garages/retrieve",
            headers={"Authorization": f"Bearer {token}"},
            json={"garage_id": garage_id, "vehicle_id": vehicle_id},
        )
        assert retrieve_resp.status_code == 200

    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/garages/")
        assert resp.status_code == 401

    async def test_ownership_violation_returns_404(self, client: AsyncClient):
        token1 = await self._register_and_get_token(client)
        token2 = await self._register_and_get_token(client)

        create_resp = await client.post(
            "/api/v1/garages/",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "garage_name": "T1 Garage",
                "purchase_price": 25000.0,
            },
        )
        garage_id = create_resp.json()["data"]["id"]

        resp = await client.get(
            f"/api/v1/garages/{garage_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert resp.status_code == 404
