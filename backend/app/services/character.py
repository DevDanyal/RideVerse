"""Business logic for character creation and appearance management."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.character import CharacterRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)


class CharacterService:
    """Orchestrates character CRUD and appearance updates."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        character_repo: CharacterRepository,
    ) -> None:
        self._player_repo = player_repo
        self._character_repo = character_repo

    async def _get_player_id(self, account_id: uuid.UUID) -> uuid.UUID:
        """Resolve account_id to player_id or raise."""
        player = await self._player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player.id

    async def _get_character_or_raise(
        self, character_id: uuid.UUID
    ):
        """Fetch a character by id or raise NotFoundError."""
        character = await self._character_repo.get_by_id(character_id)
        if character is None:
            raise NotFoundError("Character not found")
        return character

    async def get_characters(self, account_id: uuid.UUID) -> list[dict[str, Any]]:
        """Return all characters belonging to the player."""
        player_id = await self._get_player_id(account_id)
        characters = await self._character_repo.get_all_by_player_id(player_id)
        return [
            {
                "id": c.id,
                "player_id": c.player_id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "gender": c.gender,
                "date_of_birth": c.date_of_birth,
                "height": c.height,
                "weight": c.weight,
                "current_health": c.current_health,
                "current_stamina": c.current_stamina,
                "current_hunger": c.current_hunger,
                "current_thirst": c.current_thirst,
                "spawn_location": c.spawn_location,
            }
            for c in characters
        ]

    async def get_character(
        self, account_id: uuid.UUID, character_id: uuid.UUID
    ) -> dict[str, Any]:
        """Return a specific character after validating ownership."""
        player_id = await self._get_player_id(account_id)
        character = await self._get_character_or_raise(character_id)

        if character.player_id != player_id:
            raise NotFoundError("Character not found")

        return {
            "id": character.id,
            "player_id": character.player_id,
            "first_name": character.first_name,
            "last_name": character.last_name,
            "gender": character.gender,
            "date_of_birth": character.date_of_birth,
            "height": character.height,
            "weight": character.weight,
            "current_health": character.current_health,
            "current_stamina": character.current_stamina,
            "current_hunger": character.current_hunger,
            "current_thirst": character.current_thirst,
            "spawn_location": character.spawn_location,
        }

    async def update_character(
        self, account_id: uuid.UUID, character_id: uuid.UUID, **kwargs: Any
    ) -> dict[str, Any]:
        """Update character fields after validating ownership."""
        player_id = await self._get_player_id(account_id)
        character = await self._get_character_or_raise(character_id)

        if character.player_id != player_id:
            raise NotFoundError("Character not found")

        allowed_fields = {
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "height",
            "weight",
            "current_health",
            "current_stamina",
            "current_hunger",
            "current_thirst",
            "spawn_location",
        }
        filtered = {k: v for k, v in kwargs.items() if v is not None and k in allowed_fields}

        if not filtered:
            return {
                "id": character.id,
                "first_name": character.first_name,
                "last_name": character.last_name,
            }

        if "first_name" in filtered:
            if len(filtered["first_name"]) < 1 or len(filtered["first_name"]) > 50:
                raise ValidationError("First name must be between 1 and 50 characters")
        if "last_name" in filtered:
            if len(filtered["last_name"]) < 1 or len(filtered["last_name"]) > 50:
                raise ValidationError("Last name must be between 1 and 50 characters")

        updated = await self._character_repo.update(character_id, **filtered)
        if updated is None:
            raise NotFoundError("Character not found")

        logger.info("Character %s updated", character_id)

        return {
            "id": updated.id,
            "player_id": updated.player_id,
            "first_name": updated.first_name,
            "last_name": updated.last_name,
            "gender": updated.gender,
            "date_of_birth": updated.date_of_birth,
            "height": updated.height,
            "weight": updated.weight,
            "current_health": updated.current_health,
            "current_stamina": updated.current_stamina,
            "current_hunger": updated.current_hunger,
            "current_thirst": updated.current_thirst,
            "spawn_location": updated.spawn_location,
        }

    async def update_appearance(
        self, account_id: uuid.UUID, character_id: uuid.UUID, **kwargs: Any
    ) -> dict[str, Any]:
        """Update character appearance fields after validating ownership."""
        player_id = await self._get_player_id(account_id)
        character = await self._get_character_or_raise(character_id)

        if character.player_id != player_id:
            raise NotFoundError("Character not found")

        allowed_fields = {
            "hair_style",
            "hair_color",
            "eye_color",
            "skin_tone",
            "face_type",
            "beard_style",
            "tattoos",
            "glasses",
            "mask",
            "helmet",
        }
        filtered = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not filtered:
            return {"character_id": character_id, "message": "No appearance fields to update"}

        updated = await self._character_repo.update_appearance(character_id, **filtered)
        if updated is None:
            raise NotFoundError("Character appearance not found")

        logger.info("Appearance updated for character %s", character_id)

        return {
            "character_id": str(updated.character_id),
            "hair_style": updated.hair_style,
            "hair_color": updated.hair_color,
            "eye_color": updated.eye_color,
            "skin_tone": updated.skin_tone,
            "face_type": updated.face_type,
            "beard_style": updated.beard_style,
            "tattoos": updated.tattoos,
            "glasses": updated.glasses,
            "mask": updated.mask,
            "helmet": updated.helmet,
        }
