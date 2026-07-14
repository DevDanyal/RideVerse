from __future__ import annotations

import uuid
from typing import Any


class AdminService:
    """Business logic for admin dashboard, bans, and mutes."""

    def __init__(self) -> None:
        pass

    async def get_dashboard(self) -> dict[str, Any]:
        """Aggregate server-wide statistics for the admin dashboard."""
        pass

    async def ban_player(self, admin_id: uuid.UUID, player_id: uuid.UUID, reason: str, duration_hours: int | None = None) -> dict[str, Any]:
        """Ban a player, optionally for a duration, and log the action."""
        pass

    async def mute_player(self, admin_id: uuid.UUID, player_id: uuid.UUID, duration: int, reason: str) -> dict[str, Any]:
        """Mute a player for the specified duration."""
        pass

    async def get_action_logs(self, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        pass
