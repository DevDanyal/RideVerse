from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CrimeType(str, Enum):
    THEFT = "theft"
    ASSAULT = "assault"
    MURDER = "murder"
    ROBBERY = "robbery"
    DRUGS = "drugs"
    SPEEDING = "speeding"
    HIT_AND_RUN = "hit_and_run"
    VEHICLE_THEFT = "vehicle_theft"


class PoliceStatusResponse(BaseModel):
    """Player police record summary."""

    wanted_level: int = Field(default=0, ge=0, le=5)
    total_arrests: int = Field(default=0, ge=0)
    total_fines: int = Field(default=0, ge=0)
    outstanding_fine: int = Field(default=0, ge=0)
    last_arrested_at: datetime | None = None


class PayFineRequest(BaseModel):
    """Request to pay outstanding fines."""

    amount: int = Field(..., gt=0)


class CrimeRecord(BaseModel):
    """A single crime entry."""

    id: uuid.UUID
    player_id: uuid.UUID
    crime_type: CrimeType
    description: str = ""
    fine: int = Field(default=0, ge=0)
    wanted_level: int = Field(default=0, ge=0, le=5)
    reported_at: datetime | None = None
    resolved: bool = False


class CrimeHistoryResponse(BaseModel):
    """Paginated crime history."""

    crimes: list[CrimeRecord] = Field(default_factory=list)
    total: int = 0
