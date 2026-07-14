"""Business logic for wallets and financial transactions."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from app.core.exceptions import NotFoundError
from app.repositories.economy import EconomyRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)


class EconomyService:
    """Orchestrates wallet lookups and financial operations."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        economy_repo: EconomyRepository,
    ) -> None:
        self._player_repo = player_repo
        self._economy_repo = economy_repo

    async def _get_player_id(self, account_id: uuid.UUID) -> uuid.UUID:
        """Resolve account_id to player_id or raise."""
        player = await self._player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player.id

    async def get_wallet(self, account_id: uuid.UUID) -> dict[str, Any]:
        """Return the player's wallet balances."""
        player_id = await self._get_player_id(account_id)

        wallet = await self._economy_repo.get_wallet(player_id)
        if wallet is None:
            raise NotFoundError("Wallet not found")

        return {
            "id": wallet.id,
            "player_id": wallet.player_id,
            "cash": wallet.cash,
            "bank_balance": wallet.bank_balance,
            "last_transaction": wallet.last_transaction,
        }
