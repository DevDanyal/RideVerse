from __future__ import annotations

import uuid
from typing import Any

from app.repositories.chat import ChatRepository


class ChatService:
    """Business logic for chat channels and message delivery."""

    def __init__(self, chat_repo: ChatRepository) -> None:
        self._chat_repo = chat_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        pass

    async def get_by_id(self, id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, id: uuid.UUID) -> bool:
        pass

    async def get_channels(self, channel_type: str | None = None) -> list[dict[str, Any]]:
        pass

    async def send_message(self, player_id: uuid.UUID, channel_id: uuid.UUID, message: str) -> dict[str, Any]:
        """Validate channel access, sanitise message, persist, and broadcast."""
        pass

    async def get_messages(self, channel_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        pass
