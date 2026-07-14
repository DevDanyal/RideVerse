from __future__ import annotations

import uuid
from typing import Any

from app.repositories.business import BusinessRepository


class BusinessService:
    """Business logic for business ownership, income, and employees."""

    def __init__(self, business_repo: BusinessRepository) -> None:
        self._business_repo = business_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new business listing."""
        pass

    async def get_by_id(self, business_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_by_owner(self, owner_id: uuid.UUID) -> list[dict[str, Any]]:
        pass

    async def get_available(self, location: str | None = None) -> list[dict[str, Any]]:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, business_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, business_id: uuid.UUID) -> bool:
        pass

    async def buy(self, player_id: uuid.UUID, business_id: uuid.UUID) -> dict[str, Any]:
        """Transfer business ownership and deduct cost."""
        pass

    async def sell(self, player_id: uuid.UUID, business_id: uuid.UUID) -> dict[str, Any]:
        """Sell business and credit the player."""
        pass

    async def collect_income(self, business_id: uuid.UUID) -> dict[str, Any]:
        """Calculate and credit accumulated daily income."""
        pass
