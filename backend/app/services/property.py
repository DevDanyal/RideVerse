from __future__ import annotations

import uuid
from typing import Any

from app.repositories.property import PropertyRepository


class PropertyService:
    """Business logic for property purchase, sale, and management."""

    def __init__(self, property_repo: PropertyRepository) -> None:
        self._property_repo = property_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new property listing."""
        pass

    async def get_by_id(self, property_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_by_owner(self, owner_id: uuid.UUID) -> list[dict[str, Any]]:
        pass

    async def get_available(self, city: str | None = None) -> list[dict[str, Any]]:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, property_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, property_id: uuid.UUID) -> bool:
        pass

    async def buy(self, player_id: uuid.UUID, property_id: uuid.UUID) -> dict[str, Any]:
        """Transfer property ownership, deduct cost, and update records."""
        pass

    async def sell(self, player_id: uuid.UUID, property_id: uuid.UUID) -> dict[str, Any]:
        """Sell property back at a fraction of its value and credit the player."""
        pass
