from __future__ import annotations

import uuid
from typing import Any

from app.repositories.leaderboard import LeaderboardRepository


class LeaderboardService:
    """Business logic for leaderboard rankings and season management."""

    def __init__(self, leaderboard_repo: LeaderboardRepository) -> None:
        self._leaderboard_repo = leaderboard_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new leaderboard for a type and season."""
        pass

    async def get_by_id(self, leaderboard_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, leaderboard_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, leaderboard_id: uuid.UUID) -> bool:
        pass

    async def get_entries(self, leaderboard_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        pass

    async def get_player_rank(self, leaderboard_id: uuid.UUID, player_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def update_score(self, leaderboard_id: uuid.UUID, player_id: uuid.UUID, score: int) -> dict[str, Any]:
        """Update or insert a player's score on the leaderboard."""
        pass
