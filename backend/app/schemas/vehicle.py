from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class VehicleType(StrEnum):
    BIKE = "bike"
    CAR = "car"


class FuelType(StrEnum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    NONE = "none"


# ── Vehicle ──────────────────────────────────────────────────────────────

class VehicleResponse(BaseModel):
    id: uuid.UUID
    player_id: uuid.UUID
    vehicle_type: VehicleType
    brand: str
    model: str
    year: int
    vin: str
    license_plate: str
    purchase_price: float
    current_value: float
    fuel_type: FuelType
    fuel_level: float
    max_fuel: float
    health: float
    engine_health: float
    body_health: float
    top_speed: float
    acceleration: float
    braking: float
    handling: float
    mileage: float
    garage_id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class VehicleCreate(BaseModel):
    vehicle_type: str = Field(..., min_length=1, max_length=10)
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    vin: str = Field(..., min_length=17, max_length=17)
    license_plate: str = Field(..., min_length=1, max_length=20)
    purchase_price: float = Field(..., ge=0)


class VehicleUpdate(BaseModel):
    license_plate: str | None = Field(default=None, min_length=1, max_length=20)


# ── Bike ─────────────────────────────────────────────────────────────────

class BikeResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    engine_level: int
    turbo_level: int
    exhaust_level: int
    brake_level: int
    wheel_level: int
    tire_level: int
    seat_level: int
    paint_id: str | None = None
    decal_id: str | None = None
    headlight_level: int
    horn_level: int
    fuel_tank_level: int
    suspension_level: int
    chain_level: int
    mirror_level: int
    speedometer_level: int

    model_config = {"from_attributes": True}


# ── Car ──────────────────────────────────────────────────────────────────

class CarResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    engine_level: int
    transmission_level: int
    brake_level: int
    suspension_level: int
    wheel_level: int
    tire_level: int
    paint_id: str | None = None
    interior_level: int
    spoiler_level: int
    hood_level: int
    roof_level: int
    window_tint: str
    nitrous_level: int
    headlight_level: int

    model_config = {"from_attributes": True}


# ── Combined detail ──────────────────────────────────────────────────────

class VehicleDetailResponse(BaseModel):
    vehicle: VehicleResponse
    bike: BikeResponse | None = None
    car: CarResponse | None = None
