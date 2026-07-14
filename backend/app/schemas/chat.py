from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    GLOBAL = "global"
    LOCAL = "local"
    CLUB = "club"
    PRIVATE = "private"
    SYSTEM = "system"


class ChatChannelResponse(BaseModel):
    """Chat channel data."""

    id: uuid.UUID
    name: str
    type: ChannelType
    description: str = ""
    is_active: bool = True
    created_at: datetime | None = None


class ChatMessageResponse(BaseModel):
    """A single chat message."""

    id: uuid.UUID
    channel_id: uuid.UUID
    player_id: uuid.UUID
    display_name: str
    message: str
    created_at: datetime | None = None


class SendMessageRequest(BaseModel):
    """Request to send a message to a channel."""

    channel_id: uuid.UUID
    message: str = Field(..., min_length=1, max_length=500)
