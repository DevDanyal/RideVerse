"""Pydantic schemas for the Weapon system."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import SuccessResponse


# ---------------------------------------------------------------------------
# Weapon Catalog
# ---------------------------------------------------------------------------

class WeaponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    weapon_name: str
    weapon_type: str
    damage: float = Field(ge=0)
    fire_rate: float = Field(ge=0)
    accuracy: float = Field(ge=0, le=100)
    range_distance: float = Field(ge=0)
    magazine_size: int = Field(ge=0)
    reload_time: float = Field(ge=0)
    weight: float = Field(ge=0)
    max_durability: float = Field(ge=0)
    purchase_price: float = Field(ge=0)
    sell_price: float = Field(ge=0)
    required_level: int = Field(ge=1)
    ammo_type: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class WeaponListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[WeaponResponse] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Player Weapon
# ---------------------------------------------------------------------------

class PlayerWeaponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    weapon_id: uuid.UUID
    weapon: WeaponResponse | None = None
    current_ammo: int = Field(ge=0)
    reserve_ammo: int = Field(ge=0)
    durability: float = Field(ge=0, le=100)
    equipped: bool = False
    skin: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class PlayerWeaponListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[PlayerWeaponResponse] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Attachments
# ---------------------------------------------------------------------------

class WeaponAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_weapon_id: uuid.UUID
    scope: bool = False
    silencer: bool = False
    extended_magazine: bool = False
    grip: bool = False
    laser: bool = False
    flashlight: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class WeaponAttachmentRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    attachment_type: str = Field(
        ...,
        description="Attachment type: scope, silencer, extended_magazine, grip, laser, flashlight",
    )


# ---------------------------------------------------------------------------
# Ammunition
# ---------------------------------------------------------------------------

class WeaponAmmunitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    ammo_type: str
    quantity: int = Field(ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class WeaponAmmunitionListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[WeaponAmmunitionResponse] = Field(default_factory=list)


class AmmoPurchaseRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    ammo_type: str = Field(..., description="Ammo type: 9mm, 45acp, 5.56, 7.62, 12gauge, 50cal")
    quantity: int = Field(..., gt=0)


# ---------------------------------------------------------------------------
# Purchase / Sell
# ---------------------------------------------------------------------------

class WeaponBuyRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    weapon_id: uuid.UUID


class WeaponSellRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_weapon_id: uuid.UUID


# ---------------------------------------------------------------------------
# Equip / Unequip
# ---------------------------------------------------------------------------

class WeaponEquipRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_weapon_id: uuid.UUID
    equip: bool = True


# ---------------------------------------------------------------------------
# Reload
# ---------------------------------------------------------------------------

class WeaponReloadRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_weapon_id: uuid.UUID


# ---------------------------------------------------------------------------
# Repair
# ---------------------------------------------------------------------------

class WeaponRepairRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_weapon_id: uuid.UUID


class WeaponRepairCostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    current_durability: float
    max_durability: float
    durability_to_repair: float
    repair_cost: float


class WeaponRepairResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_weapon_id: uuid.UUID
    repair_cost: float
    new_durability: float
    message: str


# ---------------------------------------------------------------------------
# Buy / Sell Responses
# ---------------------------------------------------------------------------

class WeaponBuyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_weapon: PlayerWeaponResponse
    cost: float
    message: str


class WeaponSellResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    sold_price: float
    message: str


# ---------------------------------------------------------------------------
# Weapon Stats (with attachment modifiers)
# ---------------------------------------------------------------------------

class WeaponStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    weapon_name: str
    weapon_type: str
    base_damage: float
    effective_damage: float
    base_fire_rate: float
    effective_fire_rate: float
    base_accuracy: float
    effective_accuracy: float
    base_range: float
    effective_range: float
    magazine_size: int
    reload_time: float
    weight: float
    durability: float
    attachments: list[str] = Field(default_factory=list)


class AmmoShopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    ammo_type: str
    price_per_round: float
    description: str
