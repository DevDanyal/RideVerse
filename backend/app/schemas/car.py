from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


class CarCustomizeUpdate(BaseModel):
    """Upgrade levels for a car."""

    engine_level: int | None = Field(default=None, ge=0, le=10)
    transmission_level: int | None = Field(default=None, ge=0, le=10)
    brakes_level: int | None = Field(default=None, ge=0, le=10)
    suspension_level: int | None = Field(default=None, ge=0, le=10)
    turbo_level: int | None = Field(default=None, ge=0, le=5)
    nitro_level: int | None = Field(default=None, ge=0, le=5)
    armor_level: int | None = Field(default=None, ge=0, le=5)
    window_tint: int | None = None
    wheel_type: int | None = None
    horn_type: int | None = None
    neon_r: int | None = Field(default=None, ge=0, le=255)
    neon_g: int | None = Field(default=None, ge=0, le=255)
    neon_b: int | None = Field(default=None, ge=0, le=255)


class CarResponse(BaseModel):
    """Car-specific data returned to clients."""

    id: uuid.UUID
    vehicle_id: uuid.UUID
    engine_level: int = Field(default=0, ge=0, le=10)
    transmission_level: int = Field(default=0, ge=0, le=10)
    brakes_level: int = Field(default=0, ge=0, le=10)
    suspension_level: int = Field(default=0, ge=0, le=10)
    turbo_level: int = Field(default=0, ge=0, le=5)
    nitro_level: int = Field(default=0, ge=0, le=5)
    armor_level: int = Field(default=0, ge=0, le=5)
    window_tint: int = 0
    wheel_type: int = 0
    horn_type: int = 0
    neon_r: int = 0
    neon_g: int = 0
    neon_b: int = 0
    trunk_space: float = Field(default=50.0, ge=0)


class RepairRequest(BaseModel):
    """Request to repair a car."""

    vehicle_id: uuid.UUID


class RefuelRequest(BaseModel):
    """Request to refuel a car."""

    vehicle_id: uuid.UUID
    fuel_amount: float = Field(..., gt=0, description="Fuel units to add")
