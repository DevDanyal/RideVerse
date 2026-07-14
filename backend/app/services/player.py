"""Business logic for player profiles, settings, and statistics."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)


class PlayerService:
    """Orchestrates player profile, statistics, and settings operations."""

    def __init__(self, player_repo: PlayerRepository) -> None:
        self._player_repo = player_repo

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        """Look up the player by account_id or raise NotFoundError."""
        player = await self._player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def get_profile(self, account_id: uuid.UUID) -> dict[str, Any]:
        """Return the player's public profile data."""
        player = await self._get_player_or_raise(account_id)
        return {
            "id": player.id,
            "account_id": player.account_id,
            "display_name": player.display_name,
            "level": player.level,
            "experience": player.experience,
            "cash": player.cash,
            "bank_balance": player.bank_balance,
            "reputation": player.reputation,
            "health": player.health,
            "stamina": player.stamina,
            "energy": player.energy,
            "wanted_level": player.wanted_level,
            "current_server": player.current_server,
            "current_region": player.current_region,
            "created_at": player.created_at,
        }

    async def update_profile(
        self,
        account_id: uuid.UUID,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        """Update allowed player profile fields."""
        player = await self._get_player_or_raise(account_id)

        kwargs: dict[str, Any] = {}
        if display_name is not None:
            if len(display_name) < 2 or len(display_name) > 50:
                raise ValidationError(
                    "Display name must be between 2 and 50 characters"
                )
            kwargs["display_name"] = display_name

        if not kwargs:
            return {
                "id": player.id,
                "display_name": player.display_name,
                "level": player.level,
            }

        updated = await self._player_repo.update(player.id, **kwargs)
        if updated is None:
            raise NotFoundError("Player profile not found")

        logger.info("Player profile updated: %s", player.id)

        return {
            "id": updated.id,
            "account_id": updated.account_id,
            "display_name": updated.display_name,
            "level": updated.level,
            "experience": updated.experience,
            "cash": updated.cash,
            "bank_balance": updated.bank_balance,
            "reputation": updated.reputation,
        }

    async def get_statistics(self, account_id: uuid.UUID) -> dict[str, Any]:
        """Return the player's gameplay statistics."""
        player = await self._get_player_or_raise(account_id)

        stats = await self._player_repo.get_statistics(player.id)
        if stats is None:
            raise NotFoundError("Player statistics not found")

        return {
            "player_id": stats.player_id,
            "total_play_time": stats.total_play_time,
            "distance_walked": stats.distance_walked,
            "distance_driven": stats.distance_driven,
            "missions_completed": stats.missions_completed,
            "races_won": stats.races_won,
            "vehicles_owned": stats.vehicles_owned,
            "weapons_owned": stats.weapons_owned,
            "money_earned": stats.money_earned,
            "money_spent": stats.money_spent,
            "highest_speed": stats.highest_speed,
            "highest_wheelie_score": stats.highest_wheelie_score,
            "daily_login_streak": stats.daily_login_streak,
        }

    async def get_settings(self, account_id: uuid.UUID) -> dict[str, Any]:
        """Return the player's game settings."""
        player = await self._get_player_or_raise(account_id)

        settings = await self._player_repo.get_settings(player.id)
        if settings is None:
            raise NotFoundError("Player settings not found")

        return {
            "player_id": settings.player_id,
            "language": settings.language,
            "graphics_quality": settings.graphics_quality,
            "audio_volume": settings.audio_volume,
            "music_volume": settings.music_volume,
            "voice_chat": settings.voice_chat,
            "notifications": settings.notifications,
            "control_layout": settings.control_layout,
            "camera_mode": settings.camera_mode,
            "theme": settings.theme,
        }

    async def update_settings(
        self, account_id: uuid.UUID, **kwargs: Any
    ) -> dict[str, Any]:
        """Update player settings with only the provided non-None values."""
        player = await self._get_player_or_raise(account_id)

        allowed_fields = {
            "language",
            "graphics_quality",
            "audio_volume",
            "music_volume",
            "voice_chat",
            "notifications",
            "control_layout",
            "camera_mode",
            "theme",
        }
        filtered = {k: v for k, v in kwargs.items() if v is not None and k in allowed_fields}

        if not filtered:
            settings = await self._player_repo.get_settings(player.id)
            if settings is None:
                raise NotFoundError("Player settings not found")
            return {
                "player_id": settings.player_id,
                "language": settings.language,
                "graphics_quality": settings.graphics_quality,
                "audio_volume": settings.audio_volume,
                "music_volume": settings.music_volume,
                "voice_chat": settings.voice_chat,
                "notifications": settings.notifications,
                "control_layout": settings.control_layout,
                "camera_mode": settings.camera_mode,
                "theme": settings.theme,
            }

        updated = await self._player_repo.update_settings(player.id, **filtered)
        if updated is None:
            raise NotFoundError("Player settings not found")

        logger.info("Player settings updated: %s", player.id)

        return {
            "player_id": updated.player_id,
            "language": updated.language,
            "graphics_quality": updated.graphics_quality,
            "audio_volume": updated.audio_volume,
            "music_volume": updated.music_volume,
            "voice_chat": updated.voice_chat,
            "notifications": updated.notifications,
            "control_layout": updated.control_layout,
            "camera_mode": updated.camera_mode,
            "theme": updated.theme,
        }
