from __future__ import annotations

import uuid
from enum import Enum

from pydantic import BaseModel, Field


class ShopType(str, Enum):
    WEAPON = "weapon"
    CLOTHING = "clothing"
    FOOD = "food"
    ELECTRONICS = "electronics"
    VEHICLE = "vehicle"
    GENERAL = "general"


class ShopItem(BaseModel):
    """An item available for purchase in a shop."""

    id: uuid.UUID
    shop_id: uuid.UUID
    name: str
    type: ShopType
    price: int = Field(default=0, ge=0)
    description: str = ""
    stock: int = Field(default=-1, description="-1 for unlimited")
    required_level: int = Field(default=1, ge=0)
    is_available: bool = True


class PurchaseRequest(BaseModel):
    """Request to buy an item from a shop."""

    item_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)


class SellRequest(BaseModel):
    """Request to sell an item to a shop."""

    item_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)
