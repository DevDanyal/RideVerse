"""Repository layer for economy / wallet-related database operations."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.economy import Transaction, Wallet


class EconomyRepository:
    """Data-access layer for Wallet and Transaction models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        pass

    async def get_by_id(self, id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_wallet(self, player_id: uuid.UUID) -> Wallet | None:
        stmt = select(Wallet).where(
            Wallet.player_id == player_id,
            Wallet.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_transactions(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> list[dict[str, Any]]:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, id: uuid.UUID) -> bool:
        pass

    async def record_transaction(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
