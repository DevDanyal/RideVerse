from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import SuccessResponse


# ---------------------------------------------------------------------------
# Bike Variant
# ---------------------------------------------------------------------------

class BikeVariantResponse(BaseModel):
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


class BikeVariantListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[BikeVariantResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    total_pages: int = 0


# ---------------------------------------------------------------------------
# Bike Customization
# ---------------------------------------------------------------------------

class BikeCustomizationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    engine_level: int | None = Field(default=None, ge=0, le=10)
    turbo_level: int | None = Field(default=None, ge=0, le=5)
    exhaust_level: int | None = Field(default=None, ge=0, le=10)
    brake_level: int | None = Field(default=None, ge=0, le=10)
    wheel_level: int | None = Field(default=None, ge=0, le=10)
    tire_level: int | None = Field(default=None, ge=0, le=10)
    suspension_level: int | None = Field(default=None, ge=0, le=10)
    fuel_tank_level: int | None = Field(default=None, ge=0, le=10)
    seat_level: int | None = Field(default=None, ge=0, le=10)
    headlight_level: int | None = Field(default=None, ge=0, le=10)
    tail_light_level: int | None = Field(default=None, ge=0, le=10)
    indicator_level: int | None = Field(default=None, ge=0, le=10)
    handlebar_level: int | None = Field(default=None, ge=0, le=10)
    horn_level: int | None = Field(default=None, ge=0, le=10)
    chain_level: int | None = Field(default=None, ge=0, le=10)
    mirror_level: int | None = Field(default=None, ge=0, le=10)
    speedometer_level: int | None = Field(default=None, ge=0, le=10)
    paint_id: str | None = None
    decal_id: str | None = None
    sticker_id: str | None = None
    license_plate_style: str | None = None


class BikeUpgradeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    component: str = Field(
        ...,
        description="Component to upgrade: engine, turbo, exhaust, brake, wheel, tire, suspension, fuel_tank, seat, headlight, tail_light, indicator, handlebar, horn, chain, mirror, speedometer",
    )
    target_level: int = Field(..., ge=1, le=10)


class BikeCustomizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    vehicle_id: UUID
    variant_id: UUID
    engine_level: int
    turbo_level: int
    exhaust_level: int
    brake_level: int
    wheel_level: int
    tire_level: int
    suspension_level: int
    fuel_tank_level: int
    seat_level: int
    headlight_level: int
    tail_light_level: int
    indicator_level: int
    handlebar_level: int
    horn_level: int
    chain_level: int
    mirror_level: int
    speedometer_level: int
    paint_id: str | None = None
    decal_id: str | None = None
    sticker_id: str | None = None
    license_plate_style: str | None = None
    variant_name: str | None = None
    variant_brand: str | None = None
    variant_model_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BikePerformanceStats(BaseModel):
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

class BikeFuelPurchase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    fuel_liters: float = Field(..., gt=0)


class BikeFuelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    fuel_level: float
    max_fuel: float
    fuel_price_per_liter: float
    cost_for_full_tank: float


class BikeRefuelRequest(BaseModel):
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

class BikeDamageReport(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    health: float = Field(..., ge=0, le=100)
    engine_health: float = Field(..., ge=0, le=100)
    body_health: float = Field(..., ge=0, le=100)
    wheel_health: float = Field(..., ge=0, le=100)
    brake_health: float = Field(..., ge=0, le=100)
    suspension_health: float = Field(..., ge=0, le=100)


class BikeApplyDamageRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    damage_type: str = Field(
        ...,
        description="Type of damage: engine, body, brakes, suspension, wheels, tires, full",
    )
    damage_amount: float = Field(..., gt=0)


class BikeRepairRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    repair_type: str = Field(
        ...,
        description="Type of repair: engine, body, brakes, suspension, wheels, tires, full",
    )


class BikeRepairCostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    repair_type: str
    estimated_cost: float
    current_damage_level: float
    damage_to_repair: float


class BikeRepairResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vehicle_id: UUID
    repair_type: str
    repair_cost: float
    new_health_values: BikeDamageReport
    message: str


# ---------------------------------------------------------------------------
# Insurance
# ---------------------------------------------------------------------------

class BikeInsuranceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    tier: str = Field(
        ...,
        description="Insurance tier: basic, standard, premium",
    )


class BikeInsuranceResponse(BaseModel):
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


class BikeInsurancePurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    insurance: BikeInsuranceResponse
    message: str


# ---------------------------------------------------------------------------
# Purchase / Sell
# ---------------------------------------------------------------------------

class BikePurchaseRequest(BaseModel):
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


class BikePurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vehicle: VehicleResponse
    variant: BikeVariantResponse
    message: str


class BikeSellResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    sold_price: float
    message: str


class BikeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    bikes: list[BikeCustomizationResponse] = Field(default_factory=list)
    total: int = 0
