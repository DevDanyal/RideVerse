"""Achievement schemas — aligned with actual model fields."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AchievementResponse(BaseModel):
    """Achievement definition data (maps from Achievement model)."""

    id: uuid.UUID
    achievement_name: str
    description: str = ""
    reward: dict[str, Any] | None = None


class PlayerAchievementResponse(BaseModel):
    """An achievement unlocked by a player."""

    id: uuid.UUID
    player_id: uuid.UUID
    achievement_id: uuid.UUID
    unlocked_at: datetime | None = None
