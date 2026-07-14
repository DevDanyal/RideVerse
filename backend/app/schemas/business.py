from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BusinessType(str, Enum):
    RESTAURANT = "restaurant"
    BAR = "bar"
    CLUB = "club"
    MECHANIC = "mechanic"
    DEALERSHIP = "dealership"
    REAL_ESTATE = "real_estate"
    LOGISTICS = "logistics"
    FARM = "farm"


class BusinessResponse(BaseModel):
    """Business data returned to clients."""

    id: uuid.UUID
    owner_id: uuid.UUID | None = None
    name: str
    type: BusinessType
    location: str
    daily_income: int = Field(default=0, ge=0)
    daily_upkeep: int = Field(default=0, ge=0)
    employees: int = Field(default=0, ge=0)
    max_employees: int = Field(default=10, ge=0)
    level: int = Field(default=1, ge=1, le=10)
    price: int = Field(default=0, ge=0)
    is_for_sale: bool = True
    created_at: datetime | None = None


class BusinessBuyRequest(BaseModel):
    """Request to purchase a business."""

    business_type: BusinessType
    business_name: str = Field(..., min_length=1, max_length=64)
    location: str = Field(..., min_length=1, max_length=128)


class BusinessSellRequest(BaseModel):
    """Request to sell a business."""

    business_id: uuid.UUID
