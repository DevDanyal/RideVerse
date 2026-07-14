from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AdminDashboardResponse(BaseModel):
    """Admin dashboard overview stats."""

    total_players: int = Field(default=0, ge=0)
    online_players: int = Field(default=0, ge=0)
    active_servers: int = Field(default=0, ge=0)
    total_revenue: int = Field(default=0, ge=0)
    new_players_today: int = Field(default=0, ge=0)
    total_vehicles: int = Field(default=0, ge=0)
    total_properties: int = Field(default=0, ge=0)
    uptime_seconds: int = Field(default=0, ge=0)


class BanPlayerRequest(BaseModel):
    """Request to ban a player."""

    player_id: uuid.UUID
    reason: str = Field(..., min_length=1, max_length=512)
    duration_hours: int | None = Field(default=None, description="None = permanent")
    delete_character: bool = False


class MutePlayerRequest(BaseModel):
    """Request to mute a player."""

    player_id: uuid.UUID
    duration: int = Field(default=3600, gt=0, description="Duration in seconds")
    reason: str = Field(..., min_length=1, max_length=512)


class AdminActionLog(BaseModel):
    """Record of an admin action."""

    id: uuid.UUID
    admin_id: uuid.UUID
    action: str
    target_player_id: uuid.UUID | None = None
    details: str = ""
    created_at: datetime | None = None
