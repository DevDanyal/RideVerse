from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TrafficEventType(str, Enum):
    ACCIDENT = "accident"
    CONSTRUCTION = "construction"
    ROAD_CLOSURE = "road_closure"
    SPEED_CHECK = "speed_check"
    POLICE_CHASE = "police_chase"


class TrafficSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrafficEventResponse(BaseModel):
    """A single traffic event."""

    id: uuid.UUID
    type: TrafficEventType
    location: str
    severity: TrafficSeverity = TrafficSeverity.LOW
    description: str = ""
    is_active: bool = True
    created_at: datetime | None = None
    expires_at: datetime | None = None


class TrafficStatusResponse(BaseModel):
    """Active traffic events summary."""

    events: list[TrafficEventResponse] = Field(default_factory=list)
    total_active: int = 0
    updated_at: datetime | None = None
