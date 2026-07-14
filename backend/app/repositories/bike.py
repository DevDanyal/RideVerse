"""Repository layer for bike-specific database operations."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bike import Bike
from app.models.bike_insurance import BikeInsurance
from app.models.bike_variant import BikeVariant
from app.models.fuel import FuelStation, FuelTransaction
from app.models.repair_history import RepairHistory
from app.models.vehicle import Vehicle


class BikeRepository:
    """Data-access layer for bike, variant, insurance, repair, and fuel models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── CRUD for Bike ──────────────────────────────────────────────────────

    async def get_by_id(self, bike_id: uuid.UUID) -> Bike | None:
        stmt = select(Bike).where(
            Bike.id == bike_id,
            Bike.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_vehicle_id(self, vehicle_id: uuid.UUID) -> Bike | None:
        stmt = select(Bike).where(Bike.vehicle_id == vehicle_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_player_id(self, player_id: uuid.UUID) -> list[Bike]:
        stmt = (
            select(Bike)
            .join(Vehicle, Bike.vehicle_id == Vehicle.id)
            .where(Vehicle.player_id == player_id, Vehicle.is_deleted.is_(False))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[Bike]:
        stmt = (
            select(Bike)
            .where(Bike.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, data: dict) -> Bike:
        bike = Bike(**data)
        self._session.add(bike)
        await self._session.flush()
        return bike

    async def update(self, bike_id: uuid.UUID, data: dict) -> Bike | None:
        stmt = (
            update(Bike)
            .where(Bike.id == bike_id, Bike.is_deleted.is_(False))
            .values(**data)
            .returning(Bike)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, bike_id: uuid.UUID) -> bool:
        stmt = update(Bike).where(
            Bike.id == bike_id,
            Bike.is_deleted.is_(False),
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Bike Variants ──────────────────────────────────────────────────────

    async def get_variant_by_id(self, variant_id: uuid.UUID) -> BikeVariant | None:
        stmt = select(BikeVariant).where(BikeVariant.id == variant_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_variants(self, skip: int = 0, limit: int = 50) -> list[BikeVariant]:
        stmt = select(BikeVariant).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ── Insurance ──────────────────────────────────────────────────────────

    async def get_insurance(self, vehicle_id: uuid.UUID) -> BikeInsurance | None:
        stmt = select(BikeInsurance).where(
            BikeInsurance.vehicle_id == vehicle_id,
            BikeInsurance.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_insurance(self, data: dict) -> BikeInsurance:
        insurance = BikeInsurance(**data)
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
