from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GarageResponse(BaseModel):
    id: uuid.UUID
    player_id: uuid.UUID
    garage_name: str
    capacity: int
    location: str | None = None
    purchase_price: float
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class GarageCreate(BaseModel):
    garage_name: str = Field(..., min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=255)
    purchase_price: float = Field(..., ge=0)


class StoreVehicleRequest(BaseModel):
    garage_id: uuid.UUID
    vehicle_id: uuid.UUID


class RetrieveVehicleRequest(BaseModel):
    garage_id: uuid.UUID
    vehicle_id: uuid.UUID


class GarageSlotResponse(BaseModel):
    id: uuid.UUID
    garage_id: uuid.UUID
    slot_number: int
    vehicle_id: uuid.UUID | None = None
    occupied: bool

    model_config = {"from_attributes": True}
