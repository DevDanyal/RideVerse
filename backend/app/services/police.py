from __future__ import annotations

import uuid
from typing import Any

from app.repositories.police import PoliceRepository


class PoliceService:
    """Business logic for wanted levels, fines, and crime records."""

    def __init__(self, police_repo: PoliceRepository) -> None:
        self._police_repo = police_repo

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

    async def get_status(self, player_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def report_crime(self, player_id: uuid.UUID, crime_type: str, description: str = "") -> dict[str, Any]:
        """Record a crime, increase wanted level, and apply immediate fines."""
        pass

    async def pay_fine(self, player_id: uuid.UUID, amount: int) -> dict[str, Any]:
        """Validate and deduct the fine amount, clearing the outstanding balance."""
        pass

    async def get_crime_history(self, player_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass
