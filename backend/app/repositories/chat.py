from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class ChatRepository:
    """Data-access layer for chat channel and message models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        pass

    async def get_by_id(self, id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_channels(self, channel_type: str | None = None) -> list[dict[str, Any]]:
        pass

    async def get_messages(self, channel_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, id: uuid.UUID) -> bool:
        pass

    async def send_message(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
