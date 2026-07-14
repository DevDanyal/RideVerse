"""Business logic for player inventory management."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from app.core.exceptions import NotFoundError
from app.repositories.inventory import InventoryRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)


class InventoryService:
    """Orchestrates inventory lookups and item management."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        inventory_repo: InventoryRepository,
    ) -> None:
        self._player_repo = player_repo
        self._inventory_repo = inventory_repo

    async def _get_player_id(self, account_id: uuid.UUID) -> uuid.UUID:
        """Resolve account_id to player_id or raise."""
        player = await self._player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player.id

    async def get_inventory(self, account_id: uuid.UUID) -> dict[str, Any]:
        """Return the player's full inventory with all items."""
        player_id = await self._get_player_id(account_id)

        inventory = await self._inventory_repo.get_by_player_id(player_id)
        if inventory is None:
            raise NotFoundError("Inventory not found")

        items = await self._inventory_repo.get_items(inventory.id)
        item_list = [
            {
                "id": item.id,
                "item_id": item.item_id,
                "item_name": item.item_name,
                "item_type": item.item_type.value,
                "quantity": item.quantity,
                "rarity": item.rarity.value,
                "weight": item.weight,
                "durability": item.durability,
                "stackable": item.stackable,
                "equipped": item.equipped,
            }
            for item in items
        ]

        return {
            "id": inventory.id,
            "player_id": inventory.player_id,
            "max_slots": inventory.max_slots,
            "used_slots": inventory.used_slots,
            "total_weight": inventory.total_weight,
            "items": item_list,
        }
