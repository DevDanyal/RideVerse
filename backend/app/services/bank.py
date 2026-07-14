"""Business logic for player bank accounts."""
from __future__ import annotations

import logging
import uuid
import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.bank import AccountType
from app.repositories.bank import BankAccountRepository
from app.repositories.economy import EconomyRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)


def _generate_account_number() -> str:
    return f"RV{random.randint(10000000, 99999999)}"


class BankAccountService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.bank_repo = BankAccountRepository(session)
        self.economy_repo = EconomyRepository(session)
        self.player_repo = PlayerRepository(session)

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        player = await self.player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def get_accounts(self, account_id: uuid.UUID) -> list:
        player = await self._get_player_or_raise(account_id)
        return await self.bank_repo.get_by_player_id(player.id)

    async def create_account(
        self, account_id: uuid.UUID, account_type: str, initial_deposit: float = 0.0
    ) -> dict:
        player = await self._get_player_or_raise(account_id)

        if account_type not in [t.value for t in AccountType]:
            raise ValidationError(f"Invalid account type: {account_type}")

        existing = await self.bank_repo.get_by_player_id(player.id)
        if len(existing) >= 5:
            raise ValidationError("Maximum 5 bank accounts allowed")

        if initial_deposit > 0:
            wallet = await self.economy_repo.get_wallet(player.id)
            if not wallet:
                raise NotFoundError("Wallet not found")
            if wallet.cash < initial_deposit:
                raise ValidationError("Insufficient cash for initial deposit")
            new_cash = wallet.cash - initial_deposit
            await self.economy_repo.update_wallet(player.id, cash=new_cash)
            await self.economy_repo.record_transaction({
                "player_id": player.id,
                "transaction_type": "deposit",
                "amount": initial_deposit,
                "balance_before": wallet.cash,
                "balance_after": new_cash,
                "description": f"Initial deposit to new {account_type} account",
            })

        account_number = _generate_account_number()
        interest_rate = 0.02 if account_type == "savings" else 0.005

        account = await self.bank_repo.create_account({
            "player_id": player.id,
            "account_number": account_number,
            "account_type": account_type,
            "balance": initial_deposit,
            "interest_rate": interest_rate,
            "is_active": True,
        })
        logger.info("Player %s created %s account %s", player.id, account_type, account_number)
        return account

    async def deposit_to_account(
        self, account_id: uuid.UUID, bank_account_id: uuid.UUID, amount: float
    ) -> dict:
        player = await self._get_player_or_raise(account_id)
        bank_account = await self.bank_repo.get_by_id(bank_account_id)
        if not bank_account or bank_account.player_id != player.id:
            raise NotFoundError("Bank account not found")
        if not bank_account.is_active:
            raise ValidationError("Account is not active")

        wallet = await self.economy_repo.get_wallet(player.id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        if wallet.cash < amount:
            raise ValidationError("Insufficient cash")

        new_wallet_cash = wallet.cash - amount
        new_account_balance = bank_account.balance + amount
        await self.economy_repo.update_wallet(player.id, cash=new_wallet_cash)
        await self.bank_repo.update_account(bank_account_id, balance=new_account_balance)
        await self.economy_repo.record_transaction({
            "player_id": player.id, "transaction_type": "deposit",
            "amount": amount, "balance_before": wallet.cash,
            "balance_after": new_wallet_cash,
            "description": f"Deposited ${amount} to account {bank_account.account_number}",
        })
        return {"new_wallet_cash": new_wallet_cash, "new_account_balance": new_account_balance}

    async def withdraw_from_account(
        self, account_id: uuid.UUID, bank_account_id: uuid.UUID, amount: float
    ) -> dict:
        player = await self._get_player_or_raise(account_id)
        bank_account = await self.bank_repo.get_by_id(bank_account_id)
        if not bank_account or bank_account.player_id != player.id:
            raise NotFoundError("Bank account not found")
        if not bank_account.is_active:
            raise ValidationError("Account is not active")
        if bank_account.balance < amount:
            raise ValidationError("Insufficient account balance")

        wallet = await self.economy_repo.get_wallet(player.id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        if wallet.cash + amount > wallet.max_cash:
            raise ValidationError("Cash limit would be exceeded")

        new_wallet_cash = wallet.cash + amount
        new_account_balance = bank_account.balance - amount
        await self.economy_repo.update_wallet(player.id, cash=new_wallet_cash)
        await self.bank_repo.update_account(bank_account_id, balance=new_account_balance)
        await self.economy_repo.record_transaction({
            "player_id": player.id, "transaction_type": "withdraw",
            "amount": amount, "balance_before": wallet.cash,
            "balance_after": new_wallet_cash,
            "description": f"Withdrew ${amount} from account {bank_account.account_number}",
        })
        return {"new_wallet_cash": new_wallet_cash, "new_account_balance": new_account_balance}

    async def close_account(
        self, account_id: uuid.UUID, bank_account_id: uuid.UUID
    ) -> dict:
        player = await self._get_player_or_raise(account_id)
        bank_account = await self.bank_repo.get_by_id(bank_account_id)
        if not bank_account or bank_account.player_id != player.id:
            raise NotFoundError("Bank account not found")
        if bank_account.loan_balance > 0:
            raise ValidationError("Cannot close account with outstanding loan")

        if bank_account.balance > 0:
            wallet = await self.economy_repo.get_wallet(player.id)
            if wallet and wallet.cash + bank_account.balance <= wallet.max_cash:
                await self.economy_repo.update_wallet(
                    player.id, cash=wallet.cash + bank_account.balance
                )
                await self.bank_repo.update_account(bank_account_id, balance=0.0)

        await self.bank_repo.soft_delete(bank_account_id)
        logger.info("Player %s closed account %s", player.id, bank_account.account_number)
        return {"message": f"Account {bank_account.account_number} closed"}
