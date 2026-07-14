from __future__ import annotations

import uuid
from typing import Any

from app.repositories.weapon import WeaponRepository


class WeaponService:
    """Business logic for weapon purchase, sale, and equipment."""

    def __init__(self, weapon_repo: WeaponRepository) -> None:
        self._weapon_repo = weapon_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Register a new weapon type in the game."""
        pass

    async def get_by_id(self, weapon_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, weapon_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, weapon_id: uuid.UUID) -> bool:
        pass

    async def buy(self, player_id: uuid.UUID, weapon_id: uuid.UUID) -> dict[str, Any]:
        """Purchase a weapon, deduct cost, and add to player inventory."""
        pass

    async def sell(self, player_id: uuid.UUID, player_weapon_id: uuid.UUID) -> dict[str, Any]:
        """Sell a weapon and credit the player with its resale value."""
        pass

    async def equip(self, player_id: uuid.UUID, player_weapon_id: uuid.UUID, equip: bool = True) -> dict[str, Any]:
        """Equip or unequip a weapon, enforcing equip-slot limits."""
        pass
