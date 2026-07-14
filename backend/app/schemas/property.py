from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    MANSION = "mansion"
    WAREHOUSE = "warehouse"
    SAFEHOUSE = "safehouse"


class PropertyResponse(BaseModel):
    """Property data returned to clients."""

    id: uuid.UUID
    owner_id: uuid.UUID | None = None
    name: str
    type: PropertyType
    city: str
    address: str
    price: int = Field(default=0, ge=0)
    level: int = Field(default=1, ge=1, le=10)
    interior_id: int = 0
    max_occupants: int = Field(default=1, ge=0)
    current_occupants: int = Field(default=0, ge=0)
    is_for_sale: bool = True
    is_locked: bool = False
    created_at: datetime | None = None


class PropertyBuyRequest(BaseModel):
    """Request to purchase a property."""

    property_type: PropertyType
    property_name: str = Field(..., min_length=1, max_length=64)
    city: str = Field(..., min_length=1, max_length=64)
    address: str = Field(..., min_length=1, max_length=128)


class PropertySellRequest(BaseModel):
    """Request to sell a property."""

    property_id: uuid.UUID
