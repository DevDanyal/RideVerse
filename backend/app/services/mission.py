from __future__ import annotations

import uuid
from typing import Any

from app.repositories.mission import MissionRepository


class MissionService:
    """Business logic for mission lifecycle and progress tracking."""

    def __init__(self, mission_repo: MissionRepository) -> None:
        self._mission_repo = mission_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new mission definition."""
        pass

    async def get_by_id(self, mission_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, mission_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, mission_id: uuid.UUID) -> bool:
        pass

    async def start(self, player_id: uuid.UUID, mission_id: uuid.UUID) -> dict[str, Any]:
        """Validate prerequisites, create progress record, and start the mission."""
        pass

    async def complete(self, player_id: uuid.UUID, mission_id: uuid.UUID) -> dict[str, Any]:
        """Validate completion conditions, award rewards, and update progress."""
        pass

    async def get_progress(self, player_id: uuid.UUID, mission_id: uuid.UUID) -> dict[str, Any] | None:
        pass
