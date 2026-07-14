from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LeaderboardType(str, Enum):
    OVERALL = "overall"
    RACE = "race"
    MONEY = "money"
    MISSIONS = "missions"
    COMBAT = "combat"
    REPUTATION = "reputation"
    CLUB = "club"


class LeaderboardResponse(BaseModel):
    """Leaderboard metadata."""

    id: uuid.UUID
    type: LeaderboardType
    season: int = Field(default=1, ge=1)
    is_active: bool = True
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class LeaderboardEntryResponse(BaseModel):
    """A single entry in a leaderboard."""

    rank: int = Field(..., ge=1)
    player_id: uuid.UUID
    display_name: str
    score: int = Field(default=0, ge=0)
    level: int = Field(default=1, ge=1)


class LeaderboardListResponse(BaseModel):
    """Paginated leaderboard results."""

    entries: list[LeaderboardEntryResponse] = Field(default_factory=list)
    total: int = 0
    leaderboard_type: LeaderboardType = LeaderboardType.OVERALL
    season: int = 1
