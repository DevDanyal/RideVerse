from __future__ import annotations

import uuid
from typing import Any

from app.repositories.car import CarRepository


class CarService:
    """Business logic for car customisation, repair, and refuelling."""

    def __init__(self, car_repo: CarRepository) -> None:
        self._car_repo = car_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create car-specific record linked to a vehicle."""
        pass

    async def get_by_id(self, car_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_by_vehicle_id(self, vehicle_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, car_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        """Apply upgrade levels with validation and cost deduction."""
        pass

    async def delete(self, car_id: uuid.UUID) -> bool:
        pass

    async def repair(self, vehicle_id: uuid.UUID, player_id: uuid.UUID) -> dict[str, Any]:
        """Restore car health and deduct repair cost from player."""
        pass

    async def refuel(self, vehicle_id: uuid.UUID, fuel_amount: float) -> dict[str, Any]:
        """Add fuel to the car up to its max capacity."""
        pass
