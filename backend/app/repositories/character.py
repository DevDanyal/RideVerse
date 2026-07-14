"""Repository layer for character-related database operations."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character, CharacterAppearance


class CharacterRepository:
    """Data-access layer for Character and CharacterAppearance models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        pass

    async def get_by_id(self, character_id: uuid.UUID) -> Character | None:
        stmt = select(Character).where(
            Character.id == character_id,
            Character.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_player_id(self, player_id: uuid.UUID) -> list[Character]:
        stmt = select(Character).where(
            Character.player_id == player_id,
            Character.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_player_id(self, player_id: uuid.UUID) -> Character | None:
        stmt = select(Character).where(
            Character.player_id == player_id,
            Character.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, character_id: uuid.UUID, **kwargs) -> Character | None:
        stmt = (
            update(Character)
            .where(
                Character.id == character_id,
                Character.is_deleted.is_(False),
            )
            .values(**kwargs)
            .returning(Character)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_appearance(
        self, character_id: uuid.UUID, **kwargs
    ) -> CharacterAppearance | None:
        stmt = (
            update(CharacterAppearance)
            .where(
                CharacterAppearance.character_id == character_id,
                CharacterAppearance.is_deleted.is_(False),
            )
            .values(**kwargs)
            .returning(CharacterAppearance)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, character_id: uuid.UUID) -> bool:
        pass
