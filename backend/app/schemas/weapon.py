from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class WeaponType(str, Enum):
    PISTOL = "pistol"
    SMG = "smg"
    SHOTGUN = "shotgun"
    RIFLE = "rifle"
    SNIPER = "sniper"
    HEAVY = "heavy"
    MELEE = "melee"
    thrown = "thrown"


class WeaponResponse(BaseModel):
    """Weapon data returned to clients."""

    id: uuid.UUID
    weapon_name: str
    weapon_type: WeaponType
    damage: float = Field(default=0.0, ge=0)
    fire_rate: float = Field(default=0.0, ge=0, description="Rounds per second")
    accuracy: float = Field(default=0.0, ge=0, le=100)
    range_distance: float = Field(default=0.0, ge=0, description="Effective range in meters")
    magazine_size: int = Field(default=0, ge=0)
    reload_time: float = Field(default=0.0, ge=0, description="Seconds")
    price: int = Field(default=0, ge=0)
    is_legal: bool = True
    description: str = ""


class PlayerWeaponResponse(BaseModel):
    """A weapon owned by a player."""

    id: uuid.UUID
    player_id: uuid.UUID
    weapon_id: uuid.UUID
    weapon: WeaponResponse | None = None
    ammo: int = Field(default=0, ge=0)
    condition: float = Field(default=100.0, ge=0, le=100)
    is_equipped: bool = False
    acquired_at: datetime | None = None


class WeaponBuyRequest(BaseModel):
    """Request to buy a weapon from a shop."""

    weapon_id: uuid.UUID


class WeaponSellRequest(BaseModel):
    """Request to sell a weapon back to a shop."""

    player_weapon_id: uuid.UUID


class WeaponEquipRequest(BaseModel):
    """Request to equip or unequip a weapon."""

    player_weapon_id: uuid.UUID
    equip: bool = True
