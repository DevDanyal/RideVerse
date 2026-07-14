from __future__ import annotations

import uuid
from typing import Any

from app.repositories.notification import NotificationRepository


class NotificationService:
    """Business logic for creating and managing player notifications."""

    def __init__(self, notification_repo: NotificationRepository) -> None:
        self._notification_repo = notification_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a notification and optionally push it to online players."""
        pass

    async def get_by_id(self, notification_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, notification_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, notification_id: uuid.UUID) -> bool:
        pass

    async def get_player_notifications(self, player_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def get_unread_count(self, player_id: uuid.UUID) -> int:
        pass

    async def mark_read(self, player_id: uuid.UUID, notification_ids: list[uuid.UUID] | None = None) -> int:
        """Mark specific or all notifications as read."""
        pass
