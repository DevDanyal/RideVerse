"""Repository layer for garage-related database operations."""
from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.garage import Garage, GarageSlot


class GarageRepository:
    """Data-access layer for Garage and GarageSlot."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_player_id(self, player_id: uuid.UUID) -> list[Garage]:
        stmt = select(Garage).where(
            Garage.player_id == player_id,
            Garage.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, garage_id: uuid.UUID) -> Garage | None:
        stmt = select(Garage).where(
            Garage.id == garage_id,
            Garage.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, player_id: uuid.UUID, **kwargs) -> Garage:
        garage = Garage(player_id=player_id, **kwargs)
        self._session.add(garage)
        await self._session.flush()
        return garage

    async def update(self, garage_id: uuid.UUID, **kwargs) -> Garage | None:
        stmt = (
            update(Garage)
            .where(
                Garage.id == garage_id,
                Garage.is_deleted.is_(False),
            )
            .values(**kwargs)
            .returning(Garage)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete(self, garage_id: uuid.UUID) -> bool:
        stmt = (
            update(Garage)
            .where(
                Garage.id == garage_id,
                Garage.is_deleted.is_(False),
            )
            .values(is_deleted=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_slots(self, garage_id: uuid.UUID) -> list[GarageSlot]:
        stmt = select(GarageSlot).where(
            GarageSlot.garage_id == garage_id,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_slot_by_id(self, slot_id: uuid.UUID) -> GarageSlot | None:
        stmt = select(GarageSlot).where(
            GarageSlot.id == slot_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
