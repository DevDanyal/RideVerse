from __future__ import annotations

import uuid
from typing import Any

from app.repositories.club import ClubRepository


class ClubService:
    """Business logic for club creation, membership, and treasury."""

    def __init__(self, club_repo: ClubRepository) -> None:
        self._club_repo = club_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a club and set the creator as owner."""
        pass

    async def get_by_id(self, club_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_by_owner(self, owner_id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, club_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, club_id: uuid.UUID) -> bool:
        """Disband a club, removing all members."""
        pass

    async def invite(self, club_id: uuid.UUID, player_id: uuid.UUID) -> dict[str, Any]:
        """Send a club invitation to a player."""
        pass

    async def accept_invite(self, club_id: uuid.UUID, player_id: uuid.UUID) -> dict[str, Any]:
        """Accept a club invitation and add the player as a member."""
        pass

    async def kick_member(self, club_id: uuid.UUID, player_id: uuid.UUID) -> bool:
        """Remove a member from the club (owner/officer action)."""
        pass

    async def get_members(self, club_id: uuid.UUID) -> list[dict[str, Any]]:
        pass
