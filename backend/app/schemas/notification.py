from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    SYSTEM = "system"
    FRIEND = "friend"
    CLUB = "club"
    MISSION = "mission"
    ECONOMY = "economy"
    POLICE = "police"
    MARKETPLACE = "marketplace"
    ACHIEVEMENT = "achievement"


class NotificationResponse(BaseModel):
    """A single notification."""

    id: uuid.UUID
    player_id: uuid.UUID
    title: str
    message: str
    type: NotificationType = NotificationType.SYSTEM
    read: bool = False
    action_url: str | None = None
    created_at: datetime | None = None


class MarkNotificationsReadRequest(BaseModel):
    """Request to mark one or more notifications as read."""

    notification_ids: list[uuid.UUID] = Field(default_factory=list)
    mark_all: bool = False
