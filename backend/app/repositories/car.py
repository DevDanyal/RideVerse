"""Repository layer for car-specific database operations."""
from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.car import Car
from app.models.car_insurance import CarInsurance
from app.models.car_variant import CarVariant
from app.models.fuel import FuelStation, FuelTransaction
from app.models.repair_history import RepairHistory
from app.models.vehicle import Vehicle


class CarRepository:
    """Data-access layer for car, variant, insurance, repair, and fuel models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── CRUD for Car ──────────────────────────────────────────────────────

    async def get_by_id(self, car_id: uuid.UUID) -> Car | None:
        stmt = select(Car).where(
            Car.id == car_id,
            Car.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_vehicle_id(self, vehicle_id: uuid.UUID) -> Car | None:
        stmt = select(Car).where(Car.vehicle_id == vehicle_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_player_id(self, player_id: uuid.UUID) -> list[Car]:
        stmt = (
            select(Car)
            .join(Vehicle, Car.vehicle_id == Vehicle.id)
            .where(Vehicle.player_id == player_id, Vehicle.is_deleted.is_(False))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[Car]:
        stmt = (
            select(Car)
            .where(Car.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, data: dict) -> Car:
        car = Car(**data)
        self._session.add(car)
        await self._session.flush()
        return car

    async def update(self, car_id: uuid.UUID, data: dict) -> Car | None:
        stmt = (
            update(Car)
            .where(Car.id == car_id, Car.is_deleted.is_(False))
            .values(**data)
            .returning(Car)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, car_id: uuid.UUID) -> bool:
        stmt = update(Car).where(
            Car.id == car_id,
            Car.is_deleted.is_(False),
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Car Variants ──────────────────────────────────────────────────────

    async def get_variant_by_id(self, variant_id: uuid.UUID) -> CarVariant | None:
        stmt = select(CarVariant).where(CarVariant.id == variant_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_variants(self, skip: int = 0, limit: int = 50) -> list[CarVariant]:
        stmt = select(CarVariant).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ── Insurance ──────────────────────────────────────────────────────────

    async def get_insurance(self, vehicle_id: uuid.UUID) -> CarInsurance | None:
        stmt = select(CarInsurance).where(
            CarInsurance.vehicle_id == vehicle_id,
            CarInsurance.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_insurance(self, data: dict) -> CarInsurance:
        insurance = CarInsurance(**data)
        self._session.add(insurance)
        await self._session.flush()
        return insurance

    # ── Repair History ─────────────────────────────────────────────────────

    async def add_repair_record(self, data: dict) -> RepairHistory:
        record = RepairHistory(**data)
        self._session.add(record)
        await self._session.flush()
        return record

    async def get_repair_history(
        self, vehicle_id: uuid.UUID, limit: int = 10
    ) -> list[RepairHistory]:
        stmt = (
            select(RepairHistory)
            .where(RepairHistory.vehicle_id == vehicle_id)
            .order_by(RepairHistory.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ── Fuel ───────────────────────────────────────────────────────────────

    async def get_fuel_station(self, station_id: uuid.UUID) -> FuelStation | None:
        stmt = select(FuelStation).where(FuelStation.id == station_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_fuel_transaction(self, data: dict) -> FuelTransaction:
        transaction = FuelTransaction(**data)
        self._session.add(transaction)
        await self._session.flush()
        return transaction
