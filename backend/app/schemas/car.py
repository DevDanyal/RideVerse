from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import SuccessResponse


# ---------------------------------------------------------------------------
# Car Variant
# ---------------------------------------------------------------------------

class CarVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str
    brand: str
    model_name: str
    year: int
    description: str | None = None
    category: str
    purchase_price: float
    engine_cc: int
    horsepower: float
    torque_nm: float
    cylinders: int
    fuel_type: str
    doors: int
    seats: int
    cargo_space_liters: float
    top_speed_kmh: float
    acceleration_0_100: float
    weight_kg: float
    braking_distance: float
    handling_rating: float
    fuel_tank_liters: float
    fuel_consumption_l100km: float
    max_upgrade_level: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CarVariantListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[CarVariantResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    total_pages: int = 0


# ---------------------------------------------------------------------------
# Car Customization
# ---------------------------------------------------------------------------

class CarCustomizationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    paint_id: str | None = None
    window_tint: str | None = None
    license_plate_text: str | None = Field(default=None, max_length=10)


class CarUpgradeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    component: str = Field(
        ...,
        description="Component to upgrade: engine, turbo, exhaust, transmission, brake, suspension, wheel, tire, nitrous, interior, seat, steering_wheel, horn, headlight, taillight, spoiler, hood, roof, mirror",
    )
    target_level: int = Field(..., ge=1, le=10)


class CarCustomizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    vehicle_id: UUID
    variant_id: UUID | None = None
    engine_level: int
    turbo_level: int
    exhaust_level: int
    transmission_level: int
    brake_level: int
    suspension_level: int
    wheel_level: int
    tire_level: int
    nitrous_level: int
    interior_level: int
    seat_level: int
    steering_wheel_level: int
    horn_level: int
    headlight_level: int
    taillight_level: int
    spoiler_level: int
    hood_level: int
    roof_level: int
    mirror_level: int
    paint_id: str | None = None
    window_tint: str = "none"
    license_plate_text: str | None = None
    variant_name: str | None = None
    variant_brand: str | None = None
    variant_model_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CarPerformanceStats(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    effective_top_speed: float
    effective_acceleration: float
    effective_braking: float
    effective_handling: float
    upgrade_level_average: float
    horsepower: float
    torque: float
    weight: float


# ---------------------------------------------------------------------------
# Fuel
# ---------------------------------------------------------------------------

class CarFuelPurchase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    fuel_liters: float = Field(..., gt=0)


class CarFuelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    fuel_level: float
    max_fuel: float
    fuel_price_per_liter: float
    cost_for_full_tank: float


class CarRefuelRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    station_id: UUID
    fuel_liters: float = Field(..., gt=0)


class FuelStationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    station_name: str
    location: str
    fuel_price: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Damage & Repair
# ---------------------------------------------------------------------------

class CarDamageReport(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    health: float = Field(..., ge=0, le=100)
    engine_health: float = Field(..., ge=0, le=100)
    body_health: float = Field(..., ge=0, le=100)
    wheel_health: float = Field(..., ge=0, le=100)
    brake_health: float = Field(..., ge=0, le=100)
    suspension_health: float = Field(..., ge=0, le=100)


class CarApplyDamageRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    damage_type: str = Field(
        ...,
        description="Type of damage: engine, body, brakes, suspension, wheels, tires, full",
    )
    damage_amount: float = Field(..., gt=0)


class CarRepairRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    repair_type: str = Field(
        ...,
        description="Type of repair: engine, body, brakes, suspension, wheels, tires, full",
    )


class CarRepairCostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    repair_type: str
    estimated_cost: float
    current_damage_level: float
    damage_to_repair: float


class CarRepairResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vehicle_id: UUID
    repair_type: str
    repair_cost: float
    new_health_values: CarDamageReport
    message: str


# ---------------------------------------------------------------------------
# Insurance
# ---------------------------------------------------------------------------

class CarInsuranceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    tier: str = Field(
        ...,
        description="Insurance tier: basic, standard, premium",
    )


class CarInsuranceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    vehicle_id: UUID
    tier: str
    monthly_premium: float
    coverage_amount: float
    deductible: float
    is_active: bool
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CarInsurancePurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    insurance: CarInsuranceResponse
    message: str


# ---------------------------------------------------------------------------
# Purchase / Sell
# ---------------------------------------------------------------------------

class CarPurchaseRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    variant_id: UUID
    name: str = Field(..., min_length=1, max_length=100)


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    player_id: UUID
    vehicle_type: str
    name: str
    purchase_price: float
    current_value: float
    insurance_active: bool
    registration_date: datetime | None = None
    license_plate: str | None = None
    is_stolen: bool = False
    fuel_level: float
    max_fuel: float
    health: float
    engine_health: float
    body_health: float
    wheel_health: float
    brake_health: float
    suspension_health: float
    top_speed: float
    acceleration: float
    braking: float
    handling: float
    mileage: float = 0.0
    garage_id: UUID | None = None
    is_primary: bool = False
    garage_slot_id: UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CarPurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vehicle: VehicleResponse
    variant: CarVariantResponse
    message: str


class CarSellResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    sold_price: float
    message: str


class CarListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cars: list[CarCustomizationResponse] = Field(default_factory=list)
    total: int = 0
