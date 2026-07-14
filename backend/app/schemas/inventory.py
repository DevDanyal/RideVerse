"""Inventory schemas — aligned with actual model fields."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class InventoryResponse(BaseModel):
    """Player inventory summary."""

    id: uuid.UUID
    player_id: uuid.UUID
    max_slots: int = Field(default=50, ge=1)
    used_slots: int = Field(default=0, ge=0)
    total_weight: float = Field(default=0.0, ge=0)


class InventoryItemResponse(BaseModel):
    """A single item in the player's inventory."""

    id: uuid.UUID
    item_id: str
    item_name: str
    item_type: str
    quantity: int = Field(default=1, ge=0)
    rarity: str = "common"
    weight: float = Field(default=0.0, ge=0)
    durability: float = Field(default=100.0, ge=0, le=100)
    stackable: bool = True
    equipped: bool = False


class InventoryHistoryResponse(BaseModel):
    """A single inventory action history entry."""

    id: uuid.UUID
    player_id: uuid.UUID
    item_id: str
    action: str
    quantity: int = Field(default=1, ge=1)
    source: str | None = None
    destination: str | None = None
    created_at: datetime | None = None
