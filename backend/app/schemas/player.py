"""Player profile, statistics, and settings schemas — aligned with actual models."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PlayerProfile(BaseModel):
    """Core player profile returned to clients."""

    id: uuid.UUID
    account_id: uuid.UUID
    display_name: str
    level: int = Field(default=1, ge=1)
    experience: int = Field(default=0, ge=0)
    cash: float = Field(default=0.0, ge=0)
    bank_balance: float = Field(default=0.0, ge=0)
    reputation: float = Field(default=0.0)
    health: int = Field(default=100, ge=0, le=100)
    stamina: int = Field(default=100, ge=0, le=100)
    energy: int = Field(default=100, ge=0, le=100)
    wanted_level: int = Field(default=0, ge=0, le=5)
    current_server: str | None = None
    current_region: str | None = None
    created_at: datetime | None = None


class PlayerUpdate(BaseModel):
    """Fields a player may update on their own profile."""

    display_name: str | None = Field(default=None, min_length=2, max_length=50)


class PlayerStatisticsResponse(BaseModel):
    """Aggregate gameplay statistics for a player."""

    player_id: uuid.UUID
    total_play_time: float = Field(default=0.0, description="Seconds")
    distance_walked: float = Field(default=0.0, description="Meters")
    distance_driven: float = Field(default=0.0, description="Meters")
    missions_completed: int = Field(default=0, ge=0)
    races_won: int = Field(default=0, ge=0)
    vehicles_owned: int = Field(default=0, ge=0)
    weapons_owned: int = Field(default=0, ge=0)
    money_earned: float = Field(default=0.0, ge=0)
    money_spent: float = Field(default=0.0, ge=0)
    highest_speed: float = Field(default=0.0, ge=0, description="km/h")
    highest_wheelie_score: float = Field(default=0.0, ge=0)
    daily_login_streak: int = Field(default=0, ge=0)


class PlayerSettingsResponse(BaseModel):
    """Current settings for a player."""

    player_id: uuid.UUID
    language: str = "en"
    graphics_quality: str = "medium"
    audio_volume: int = Field(default=80, ge=0, le=100)
    music_volume: int = Field(default=80, ge=0, le=100)
    voice_chat: bool = True
    notifications: bool = True
    control_layout: str = "default"
    camera_mode: str = "third_person"
    theme: str = "dark"


class PlayerSettingsUpdate(BaseModel):
    """Fields a player may update in their settings."""

    language: str | None = None
    graphics_quality: str | None = None
    audio_volume: int | None = Field(default=None, ge=0, le=100)
    music_volume: int | None = Field(default=None, ge=0, le=100)
    voice_chat: bool | None = None
    notifications: bool | None = None
    control_layout: str | None = None
    camera_mode: str | None = None
    theme: str | None = None
