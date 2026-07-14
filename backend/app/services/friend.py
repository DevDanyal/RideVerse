from __future__ import annotations

import uuid
from typing import Any

from app.repositories.friend import FriendRepository


class FriendService:
    """Business logic for friend requests, acceptance, and blocking."""

    def __init__(self, friend_repo: FriendRepository) -> None:
        self._friend_repo = friend_repo

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        pass

    async def get_by_id(self, id: uuid.UUID) -> dict[str, Any] | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        pass

    async def update(self, id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any] | None:
        pass

    async def delete(self, id: uuid.UUID) -> bool:
        pass

    async def send_request(self, player_id: uuid.UUID, friend_id: uuid.UUID) -> dict[str, Any]:
        """Create a pending friend request, checking for blocks and duplicates."""
        pass

    async def accept_request(self, player_id: uuid.UUID, friend_id: uuid.UUID) -> dict[str, Any]:
        """Accept a pending friend request and create the bidirectional link."""
        pass

    async def remove_friend(self, player_id: uuid.UUID, friend_id: uuid.UUID) -> bool:
        """Remove an existing friendship."""
        pass

    async def block_player(self, player_id: uuid.UUID, target_id: uuid.UUID) -> dict[str, Any]:
        """Block a player, removing any existing friendship and preventing future requests."""
        pass

    async def get_friends(self, player_id: uuid.UUID) -> list[dict[str, Any]]:
        pass
