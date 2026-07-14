"""Character schemas — aligned with actual model fields."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    """Request to create a new character."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    gender: str = Field(..., min_length=1, max_length=20)
    date_of_birth: date | None = None
    height: float = Field(..., gt=0, le=2.5, description="Height in meters")
    weight: float = Field(..., gt=0, le=300, description="Weight in kg")
    spawn_location: str | None = Field(default=None, description="Initial spawn location")


class CharacterAppearanceResponse(BaseModel):
    """Character appearance customisation data."""

    id: uuid.UUID
    character_id: uuid.UUID
    hair_style: str | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    skin_tone: str | None = None
    face_type: str | None = None
    beard_style: str | None = None
    tattoos: dict[str, Any] | None = None
    glasses: bool = False
    mask: bool = False
    helmet: bool = False


class CharacterResponse(BaseModel):
    """Full character data returned to clients."""

    id: uuid.UUID
    player_id: uuid.UUID
    first_name: str
    last_name: str
    gender: str
    date_of_birth: date | None = None
    height: float
    weight: float
    current_health: int = Field(default=100, ge=0, le=100)
    current_stamina: int = Field(default=100, ge=0, le=100)
    current_hunger: int = Field(default=100, ge=0, le=100)
    current_thirst: int = Field(default=100, ge=0, le=100)
    spawn_location: str | None = None


class CharacterUpdate(BaseModel):
    """Fields a player may update on their character."""

    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    gender: str | None = Field(default=None, min_length=1, max_length=20)
    height: float | None = Field(default=None, gt=0, le=2.5)
    weight: float | None = Field(default=None, gt=0, le=300)
    spawn_location: str | None = None


class CharacterAppearanceUpdate(BaseModel):
    """Fields a player may update to customise their character's appearance."""

    hair_style: str | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    skin_tone: str | None = None
    face_type: str | None = None
    beard_style: str | None = None
    tattoos: dict[str, Any] | None = None
    glasses: bool | None = None
    mask: bool | None = None
    helmet: bool | None = None
