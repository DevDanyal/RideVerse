from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MissionType(str, Enum):
    STORY = "story"
    SIDE = "side"
    DAILY = "daily"
    REPEATABLE = "repeatable"
    HEIST = "heist"
    RACE = "race"
    DELIVERY = "delivery"


class MissionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"


class MissionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MissionResponse(BaseModel):
    """Mission definition data."""

    id: uuid.UUID
    name: str
    description: str = ""
    type: MissionType
    difficulty: MissionDifficulty = MissionDifficulty.MEDIUM
    reward_cash: int = Field(default=0, ge=0)
    reward_experience: int = Field(default=0, ge=0)
    reward_items: list[dict] = Field(default_factory=list)
    required_level: int = Field(default=1, ge=0)
    required_missions: list[uuid.UUID] = Field(default_factory=list)
    max_players: int = Field(default=1, ge=1)
    time_limit: int | None = Field(default=None, description="Seconds")
    is_available: bool = True


class MissionStartRequest(BaseModel):
    """Request to start a mission."""

    mission_id: uuid.UUID


class MissionCompleteRequest(BaseModel):
    """Request to mark a mission as completed."""

    mission_id: uuid.UUID


class MissionProgressResponse(BaseModel):
    """Current progress on a mission for a player."""

    mission_id: uuid.UUID
    status: MissionStatus
    progress: float = Field(default=0.0, ge=0, le=100, description="Percentage")
    started_at: datetime | None = None
    completed_at: datetime | None = None
    objectives_completed: int = 0
    objectives_total: int = 0
