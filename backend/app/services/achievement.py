"""Business logic for achievement definitions and unlock tracking."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from app.core.exceptions import NotFoundError
from app.repositories.achievement import AchievementRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)


class AchievementService:
    """Orchestrates achievement lookups and unlock tracking."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        achievement_repo: AchievementRepository,
    ) -> None:
        self._player_repo = player_repo
        self._achievement_repo = achievement_repo

    async def _get_player_id(self, account_id: uuid.UUID) -> uuid.UUID:
        """Resolve account_id to player_id or raise."""
        player = await self._player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player.id

    async def get_player_achievements(
        self, account_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """Return all achievements unlocked by the player."""
        player_id = await self._get_player_id(account_id)

        achievements = await self._achievement_repo.get_player_achievements(player_id)
        return [
            {
                "id": pa.id,
                "player_id": pa.player_id,
                "achievement_id": pa.achievement_id,
                "unlocked_at": pa.unlocked_at,
            }
            for pa in achievements
        ]
