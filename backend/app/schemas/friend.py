from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FriendStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class FriendResponse(BaseModel):
    """Friend or friend-request entry."""

    player_id: uuid.UUID
    display_name: str
    status: FriendStatus
    online: bool = False
    level: int = 1
    last_seen: datetime | None = None


class FriendRequest(BaseModel):
    """Request to send a friend request."""

    friend_player_id: uuid.UUID


class BlockRequest(BaseModel):
    """Request to block a player."""

    player_id: uuid.UUID
