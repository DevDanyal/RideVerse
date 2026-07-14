"""Repository layer for vehicle-related database operations."""
from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bike import Bike
from app.models.car import Car
from app.models.vehicle import Vehicle


class VehicleRepository:
    """Data-access layer for Vehicle, Bike, and Car."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_player_id(self, player_id: uuid.UUID) -> list[Vehicle]:
        stmt = select(Vehicle).where(
            Vehicle.player_id == player_id,
            Vehicle.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, vehicle_id: uuid.UUID) -> Vehicle | None:
        stmt = select(Vehicle).where(
            Vehicle.id == vehicle_id,
            Vehicle.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, player_id: uuid.UUID, **kwargs) -> Vehicle:
        vehicle = Vehicle(player_id=player_id, **kwargs)
        self._session.add(vehicle)
        await self._session.flush()
        return vehicle

    async def update(self, vehicle_id: uuid.UUID, **kwargs) -> Vehicle | None:
        stmt = (
            update(Vehicle)
            .where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted.is_(False),
            )
            .values(**kwargs)
            .returning(Vehicle)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete(self, vehicle_id: uuid.UUID) -> bool:
        stmt = (
            update(Vehicle)
            .where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted.is_(False),
            )
            .values(is_deleted=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_bike(self, vehicle_id: uuid.UUID) -> Bike | None:
        stmt = select(Bike).where(
            Bike.vehicle_id == vehicle_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_car(self, vehicle_id: uuid.UUID) -> Car | None:
        stmt = select(Car).where(
            Car.vehicle_id == vehicle_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
