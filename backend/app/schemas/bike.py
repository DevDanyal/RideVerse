from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


class BikeCustomizeUpdate(BaseModel):
    """Upgrade levels for a bike."""

    engine_level: int | None = Field(default=None, ge=0, le=10)
    transmission_level: int | None = Field(default=None, ge=0, le=10)
    brakes_level: int | None = Field(default=None, ge=0, le=10)
    suspension_level: int | None = Field(default=None, ge=0, le=10)
    turbo_level: int | None = Field(default=None, ge=0, le=5)
    nitro_level: int | None = Field(default=None, ge=0, le=5)
    wheel_type: int | None = None
    exhaust_type: int | None = None


class BikeResponse(BaseModel):
    """Bike-specific data returned to clients."""

    id: uuid.UUID
    vehicle_id: uuid.UUID
    engine_level: int = Field(default=0, ge=0, le=10)
    transmission_level: int = Field(default=0, ge=0, le=10)
    brakes_level: int = Field(default=0, ge=0, le=10)
    suspension_level: int = Field(default=0, ge=0, le=10)
    turbo_level: int = Field(default=0, ge=0, le=5)
    nitro_level: int = Field(default=0, ge=0, le=5)
    wheel_type: int = 0
    exhaust_type: int = 0
    wheelie_count: int = 0


class RepairRequest(BaseModel):
    """Request to repair a bike."""

    vehicle_id: uuid.UUID


class RefuelRequest(BaseModel):
    """Request to refuel a bike."""

    vehicle_id: uuid.UUID
    fuel_amount: float = Field(..., gt=0, description="Fuel units to add")
