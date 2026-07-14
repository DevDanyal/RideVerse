"""Repository layer for player-related database operations."""
from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player, PlayerSettings, PlayerStatistics


class PlayerRepository:
    """Data-access layer for Player, PlayerStatistics, and PlayerSettings."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_account_id(self, account_id: uuid.UUID) -> Player | None:
        stmt = select(Player).where(
            Player.account_id == account_id,
            Player.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, player_id: uuid.UUID) -> Player | None:
        stmt = select(Player).where(
            Player.id == player_id,
            Player.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, player_id: uuid.UUID, **kwargs) -> Player | None:
        stmt = (
            update(Player)
            .where(
                Player.id == player_id,
                Player.is_deleted.is_(False),
            )
            .values(**kwargs)
            .returning(Player)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_statistics(self, player_id: uuid.UUID) -> PlayerStatistics | None:
        stmt = select(PlayerStatistics).where(
            PlayerStatistics.player_id == player_id,
            PlayerStatistics.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_settings(self, player_id: uuid.UUID) -> PlayerSettings | None:
        stmt = select(PlayerSettings).where(
            PlayerSettings.player_id == player_id,
            PlayerSettings.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_settings(
        self, player_id: uuid.UUID, **kwargs
    ) -> PlayerSettings | None:
        stmt = (
            update(PlayerSettings)
            .where(
                PlayerSettings.player_id == player_id,
                PlayerSettings.is_deleted.is_(False),
            )
            .values(**kwargs)
            .returning(PlayerSettings)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
