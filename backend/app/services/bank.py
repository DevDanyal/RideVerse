"""Business logic for player bank accounts."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from app.core.exceptions import NotFoundError
from app.repositories.bank import BankAccountRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)


class BankAccountService:
    """Orchestrates bank account lookups for players."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        bank_repo: BankAccountRepository,
    ) -> None:
        self._player_repo = player_repo
        self._bank_repo = bank_repo

    async def _get_player_id(self, account_id: uuid.UUID) -> uuid.UUID:
        """Resolve account_id to player_id or raise."""
        player = await self._player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player.id

    async def get_accounts(self, account_id: uuid.UUID) -> list[dict[str, Any]]:
        """Return all bank accounts belonging to the player."""
        player_id = await self._get_player_id(account_id)

        accounts = await self._bank_repo.get_by_player_id(player_id)
        return [
            {
                "id": acct.id,
                "player_id": acct.player_id,
                "account_number": acct.account_number,
                "account_type": acct.account_type.value,
                "balance": acct.balance,
                "interest_rate": acct.interest_rate,
                "is_active": acct.is_active,
            }
            for acct in accounts
        ]
