from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class PoliceRepository:
    """Data-access layer for police / crime-record models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        pass

    async def get_by_id(self, id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_status(self, player_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_crime_history(self, player_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, id: uuid.UUID) -> bool:
        pass
