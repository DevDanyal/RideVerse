from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ListingStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ItemType(str, Enum):
    VEHICLE = "vehicle"
    WEAPON = "weapon"
    ITEM = "item"
    PROPERTY = "property"
    BUSINESS = "business"


class ListingResponse(BaseModel):
    """Marketplace listing data."""

    id: uuid.UUID
    seller_id: uuid.UUID
    item_type: ItemType
    item_id: uuid.UUID
    price: int = Field(default=0, ge=0)
    status: ListingStatus = ListingStatus.ACTIVE
    description: str = ""
    created_at: datetime | None = None
    expires_at: datetime | None = None


class CreateListingRequest(BaseModel):
    """Request to create a new marketplace listing."""

    item_type: ItemType
    item_id: uuid.UUID
    price: int = Field(..., gt=0)
    description: str = ""


class BuyListingRequest(BaseModel):
    """Request to purchase a marketplace listing."""

    listing_id: uuid.UUID
