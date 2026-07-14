from __future__ import annotations

import uuid
from typing import Any

from app.repositories.npc import NpcRepository


class NpcService:
    """Business logic for NPC interactions and dialogue."""

    def __init__(self, npc_repo: NpcRepository) -> None:
        self._npc_repo = npc_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new NPC with initial dialogue and spawn data."""
        pass

    async def get_by_id(self, npc_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_by_location(self, location: str) -> list[dict[str, Any]]:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, npc_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, npc_id: uuid.UUID) -> bool:
        pass

    async def interact(self, player_id: uuid.UUID, npc_id: uuid.UUID, action: str) -> dict[str, Any]:
        """Handle an interaction, dispatching to the correct handler (shop, quest, dialogue)."""
        pass

    async def get_dialogue(self, npc_id: uuid.UUID) -> list[dict[str, Any]]:
        pass
