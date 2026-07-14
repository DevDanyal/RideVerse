from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ClubRole(str, Enum):
    MEMBER = "member"
    OFFICER = "officer"
    OWNER = "owner"


class ClubResponse(BaseModel):
    """Club data returned to clients."""

    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    description: str = ""
    member_count: int = Field(default=1, ge=1)
    level: int = Field(default=1, ge=1, le=50)
    treasury: int = Field(default=0, ge=0)
    tag: str = Field(default="", max_length=6)
    created_at: datetime | None = None


class ClubCreate(BaseModel):
    """Request to create a new club."""

    name: str = Field(..., min_length=2, max_length=32)
    description: str = Field(default="", max_length=256)


class ClubInviteRequest(BaseModel):
    """Request to invite a player to the club."""

    player_id: uuid.UUID


class ClubMemberResponse(BaseModel):
    """A single club member."""

    player_id: uuid.UUID
    display_name: str
    role: ClubRole = ClubRole.MEMBER
    contribution: int = Field(default=0, ge=0)
    joined_at: datetime | None = None
