"""Business logic for the Economy system."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.economy import TransactionType
from app.repositories.bank import BankAccountRepository
from app.repositories.economy import EconomyRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)

SALARY_CLAIM_COOLDOWN_HOURS = 24

DAILY_REWARD_AMOUNTS = {
    1: 500, 2: 600, 3: 750, 4: 900, 5: 1000,
    6: 1200, 7: 2000,
}
MAX_DAILY_STREAK = 7


class EconomyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.economy_repo = EconomyRepository(session)
        self.player_repo = PlayerRepository(session)
        self.bank_repo = BankAccountRepository(session)

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        player = await self.player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def _get_wallet_or_raise(self, player_id: uuid.UUID):
        wallet = await self.economy_repo.get_wallet(player_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        return wallet

    # -- Wallet --

    async def get_wallet(self, account_id: uuid.UUID) -> dict:
        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)
        return {
            "id": wallet.id,
            "player_id": wallet.player_id,
            "cash": wallet.cash,
            "bank_balance": wallet.bank_balance,
            "max_cash": wallet.max_cash,
            "max_bank_balance": wallet.max_bank_balance,
            "daily_salary": wallet.daily_salary,
            "last_salary_claim": wallet.last_salary_claim,
            "total_earned": wallet.total_earned,
            "total_spent": wallet.total_spent,
            "last_transaction": wallet.last_transaction,
        }

    # -- Deposit --

    async def deposit(
        self, account_id: uuid.UUID, amount: float, atm_id: uuid.UUID | None = None
    ) -> dict:
        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)
        if wallet.cash < amount:
            raise ValidationError("Insufficient cash")

        fee = 0.0
        if atm_id:
            atm = await self.economy_repo.get_atm(atm_id)
            if not atm:
                raise NotFoundError("ATM not found")
            if not atm.is_operational:
                raise ValidationError("ATM is out of service")
            if atm.daily_withdrawn + amount > atm.daily_withdrawal_limit:
                raise ValidationError("ATM daily withdrawal limit reached")
            fee = atm.transaction_fee
            await self.economy_repo.update_atm(atm_id, daily_withdrawn=atm.daily_withdrawn + amount)

        total_deducted = amount + fee
        if wallet.cash < total_deducted:
            raise ValidationError(
                f"Insufficient cash (need ${total_deducted} including ${fee} fee)"
            )

        balance_before = wallet.cash
        new_cash = wallet.cash - total_deducted
        new_bank = wallet.bank_balance + amount

        await self.economy_repo.update_wallet(
            player.id, cash=new_cash, bank_balance=new_bank,
            last_transaction=datetime.now(timezone.utc),
            total_spent=wallet.total_spent + total_deducted,
        )
        desc = f"Deposited ${amount} to bank"
        if fee:
            desc += f" (ATM fee: ${fee})"
        await self.economy_repo.record_transaction({
            "player_id": player.id,
            "transaction_type": TransactionType.DEPOSIT,
            "amount": amount, "balance_before": balance_before,
            "balance_after": new_cash, "description": desc,
        })
        logger.info("Player %s deposited $%s (fee: $%s)", player.id, amount, fee)
        return {"deposited": amount, "fee": fee, "new_cash": new_cash, "new_bank_balance": new_bank}

    # -- Withdraw --

    async def withdraw(
        self, account_id: uuid.UUID, amount: float, atm_id: uuid.UUID | None = None
    ) -> dict:
        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)
        if wallet.bank_balance < amount:
            raise ValidationError("Insufficient bank balance")

        fee = 0.0
        if atm_id:
            atm = await self.economy_repo.get_atm(atm_id)
            if not atm:
                raise NotFoundError("ATM not found")
            if not atm.is_operational:
                raise ValidationError("ATM is out of service")
            if atm.daily_withdrawn + amount > atm.daily_withdrawal_limit:
                raise ValidationError("ATM daily withdrawal limit reached")
            fee = atm.transaction_fee
            await self.economy_repo.update_atm(atm_id, daily_withdrawn=atm.daily_withdrawn + amount)

        total_withdrawn = amount + fee
        if wallet.bank_balance < total_withdrawn:
            raise ValidationError(
                f"Insufficient bank balance (need ${total_withdrawn} including ${fee} fee)"
            )
        if wallet.cash + amount > wallet.max_cash:
            raise ValidationError(f"Cash limit reached. Max: ${wallet.max_cash}")

        balance_before = wallet.cash
        new_cash = wallet.cash + amount
        new_bank = wallet.bank_balance - total_withdrawn

        await self.economy_repo.update_wallet(
            player.id, cash=new_cash, bank_balance=new_bank,
            last_transaction=datetime.now(timezone.utc),
            total_spent=wallet.total_spent + fee,
        )
        desc = f"Withdrew ${amount} from bank"
        if fee:
            desc += f" (ATM fee: ${fee})"
        await self.economy_repo.record_transaction({
            "player_id": player.id,
            "transaction_type": TransactionType.WITHDRAW,
            "amount": amount, "balance_before": balance_before,
            "balance_after": new_cash, "description": desc,
        })
        logger.info("Player %s withdrew $%s (fee: $%s)", player.id, amount, fee)
        return {"withdrawn": amount, "fee": fee, "new_cash": new_cash, "new_bank_balance": new_bank}

    # -- Transfer --

    async def transfer(
        self, account_id: uuid.UUID, target_player_id: uuid.UUID,
        amount: float, description: str | None = None,
    ) -> dict:
        if amount <= 0:
            raise ValidationError("Transfer amount must be positive")

        player = await self._get_player_or_raise(account_id)
        sender_wallet = await self._get_wallet_or_raise(player.id)

        target_player = await self.player_repo.get_by_id(target_player_id)
        if not target_player:
            raise NotFoundError("Target player not found")
        receiver_wallet = await self.economy_repo.get_wallet(target_player_id)
        if not receiver_wallet:
            raise NotFoundError("Target player wallet not found")

        if receiver_wallet.bank_balance + amount > receiver_wallet.max_bank_balance:
            raise ValidationError("Recipient bank balance limit would be exceeded")

        fee = max(1.0, amount * 0.02)
        if sender_wallet.cash < amount + fee:
            raise ValidationError("Insufficient cash for transfer and fee")

        sender_balance_before = sender_wallet.cash
        new_sender_cash = sender_wallet.cash - amount - fee
        new_receiver_bank = receiver_wallet.bank_balance + amount

        await self.economy_repo.update_wallet(
            player.id, cash=new_sender_cash,
            last_transaction=datetime.now(timezone.utc),
            total_spent=sender_wallet.total_spent + amount + fee,
        )
        await self.economy_repo.update_wallet(
            target_player_id, bank_balance=new_receiver_bank,
            total_earned=receiver_wallet.total_earned + amount,
        )

        await self.economy_repo.record_transaction({
            "player_id": player.id,
            "transaction_type": TransactionType.TRANSFER_OUT,
            "amount": amount, "balance_before": sender_balance_before,
            "balance_after": new_sender_cash,
            "source_player_id": player.id,
            "destination_player_id": target_player_id,
            "description": description or f"Transfer to {target_player.display_name}",
        })
        await self.economy_repo.record_transaction({
            "player_id": target_player_id,
            "transaction_type": TransactionType.TRANSFER_IN,
            "amount": amount, "balance_before": receiver_wallet.bank_balance,
            "balance_after": new_receiver_bank,
            "source_player_id": player.id,
            "destination_player_id": target_player_id,
            "description": description or f"Transfer from {player.display_name}",
        })
        logger.info("Player %s transferred $%s to %s", player.id, amount, target_player_id)
        return {
            "sender_balance_after": new_sender_cash,
            "receiver_balance_after": new_receiver_bank,
            "amount": amount, "fee": fee,
            "message": f"${amount} transferred successfully",
        }

    # -- Transaction History --

    async def get_transaction_history(
        self, account_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list:
        player = await self._get_player_or_raise(account_id)
        return await self.economy_repo.get_transactions(player.id, skip, limit)

    async def get_transactions_by_type(
        self, account_id: uuid.UUID, transaction_type: str,
        skip: int = 0, limit: int = 50,
    ) -> list:
        player = await self._get_player_or_raise(account_id)
        return await self.economy_repo.get_transactions_by_type(
            player.id, transaction_type, skip, limit
        )

    # -- Salary --

    async def claim_salary(self, account_id: uuid.UUID) -> dict:
        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)

        if wallet.last_salary_claim:
            last_claim = wallet.last_salary_claim
            if last_claim.tzinfo is None:
                last_claim = last_claim.replace(tzinfo=timezone.utc)
            hours_since = (
                datetime.now(timezone.utc) - last_claim
            ).total_seconds() / 3600
            if hours_since < SALARY_CLAIM_COOLDOWN_HOURS:
                remaining = SALARY_CLAIM_COOLDOWN_HOURS - hours_since
                raise ValidationError(
                    f"Salary already claimed. Try again in {remaining:.1f} hours"
                )

        salary = wallet.daily_salary
        if wallet.cash + salary > wallet.max_cash:
            raise ValidationError("Cash limit would be exceeded")

        balance_before = wallet.cash
        new_cash = wallet.cash + salary
        await self.economy_repo.update_wallet(
            player.id, cash=new_cash,
            last_salary_claim=datetime.now(timezone.utc),
            total_earned=wallet.total_earned + salary,
        )
        await self.economy_repo.record_transaction({
            "player_id": player.id,
            "transaction_type": TransactionType.SALARY,
            "amount": salary, "balance_before": balance_before,
            "balance_after": new_cash, "description": "Daily salary claim",
        })
        logger.info("Player %s claimed salary: $%s", player.id, salary)
        return {"salary_amount": salary, "new_cash_balance": new_cash, "message": f"Salary of ${salary} claimed"}

    # -- Daily Rewards --

    async def get_daily_reward_status(self, account_id: uuid.UUID) -> list:
        player = await self._get_player_or_raise(account_id)
        last_claimed = await self.economy_repo.get_last_claimed_day(player.id)
        rewards = []
        for day in range(1, MAX_DAILY_STREAK + 1):
            claimed = day <= last_claimed
            amount = DAILY_REWARD_AMOUNTS.get(day, 500)
            rewards.append({"day_number": day, "reward_amount": amount, "claimed": claimed})
        return rewards

    async def claim_daily_reward(self, account_id: uuid.UUID) -> dict:
        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)
        last_claimed = await self.economy_repo.get_last_claimed_day(player.id)
        next_day = last_claimed + 1
        is_streak_reset = False
        if next_day > MAX_DAILY_STREAK:
            next_day = 1
            is_streak_reset = True

        existing = await self.economy_repo.get_daily_reward(player.id, next_day)
        if existing and existing.claimed and not is_streak_reset:
            raise ValidationError(f"Day {next_day} reward already claimed today")

        reward_amount = DAILY_REWARD_AMOUNTS.get(next_day, 500)
        if wallet.cash + reward_amount > wallet.max_cash:
            raise ValidationError("Cash limit would be exceeded")

        balance_before = wallet.cash
        new_cash = wallet.cash + reward_amount
        await self.economy_repo.update_wallet(
            player.id, cash=new_cash, total_earned=wallet.total_earned + reward_amount,
        )
        now = datetime.now(timezone.utc)
        if existing:
            await self.economy_repo.update_daily_reward(existing.id, claimed=True, claimed_at=now)
        else:
            await self.economy_repo.create_daily_reward({
                "player_id": player.id, "day_number": next_day,
                "reward_amount": reward_amount, "claimed": True, "claimed_at": now,
            })
        await self.economy_repo.record_transaction({
            "player_id": player.id,
            "transaction_type": TransactionType.DAILY_REWARD,
            "amount": reward_amount, "balance_before": balance_before,
            "balance_after": new_cash, "description": f"Day {next_day} daily reward",
        })
        return {
            "day_number": next_day, "reward_amount": reward_amount,
            "new_cash_balance": new_cash, "streak": next_day,
            "message": f"Day {next_day} reward of ${reward_amount} claimed",
        }

    # -- Business Income --

    async def credit_business_income(
        self, player_id: uuid.UUID, amount: float,
        business_id: uuid.UUID | None = None, description: str | None = None,
    ) -> dict:
        wallet = await self._get_wallet_or_raise(player_id)
        if wallet.cash + amount > wallet.max_cash:
            raise ValidationError("Cash limit would be exceeded")
        balance_before = wallet.cash
        new_cash = wallet.cash + amount
        await self.economy_repo.update_wallet(
            player_id, cash=new_cash, total_earned=wallet.total_earned + amount,
        )
        ref = f"business:{business_id}" if business_id else None
        await self.economy_repo.record_transaction({
            "player_id": player_id,
            "transaction_type": TransactionType.BUSINESS_INCOME,
            "amount": amount, "balance_before": balance_before,
            "balance_after": new_cash, "reference": ref,
            "description": description or f"Business income: ${amount}",
        })
        return {"amount": amount, "new_cash_balance": new_cash, "message": f"Business income of ${amount} credited"}

    # -- Tax --

    async def apply_tax(
        self, account_id: uuid.UUID, rate: float, description: str | None = None,
    ) -> dict:
        if rate < 0 or rate > 1:
            raise ValidationError("Tax rate must be between 0 and 1")
        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)
        tax_amount = round(wallet.cash * rate, 2)
        if tax_amount <= 0:
            raise ValidationError("No tax to collect")
        balance_before = wallet.cash
        new_cash = wallet.cash - tax_amount
        await self.economy_repo.update_wallet(
            player.id, cash=new_cash, total_spent=wallet.total_spent + tax_amount,
        )
        await self.economy_repo.record_transaction({
            "player_id": player.id, "transaction_type": TransactionType.TAX,
            "amount": tax_amount, "balance_before": balance_before,
            "balance_after": new_cash,
            "description": description or f"Tax applied at {rate*100:.1f}%",
        })
        return {"tax_amount": tax_amount, "rate": rate, "new_cash_balance": new_cash, "message": f"Tax of ${tax_amount} collected"}

    # -- Loan (disabled) --

    async def request_loan(self, account_id: uuid.UUID, amount: float, term_days: int = 30) -> dict:
        return {"message": "Loan system is not yet enabled"}

    async def repay_loan(self, account_id: uuid.UUID, amount: float) -> dict:
        return {"message": "Loan system is not yet enabled"}

    # -- ATM --

    async def get_atms(self) -> list:
        return await self.economy_repo.get_all_atms()

    # -- Economy Summary --

    async def get_economy_summary(self, account_id: uuid.UUID) -> dict:
        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)
        bank_accounts = await self.bank_repo.get_by_player_id(player.id)
        salary_claimed_today = False
        if wallet.last_salary_claim:
            last_claim = wallet.last_salary_claim
            if last_claim.tzinfo is None:
                last_claim = last_claim.replace(tzinfo=timezone.utc)
            hours_since = (
                datetime.now(timezone.utc) - last_claim
            ).total_seconds() / 3600
            salary_claimed_today = hours_since < SALARY_CLAIM_COOLDOWN_HOURS
        total_loans = sum(a.loan_balance for a in bank_accounts)
        return {
            "cash": wallet.cash, "bank_balance": wallet.bank_balance,
            "total_wealth": wallet.cash + wallet.bank_balance,
            "daily_salary": wallet.daily_salary,
            "salary_claimed_today": salary_claimed_today,
            "total_earned": wallet.total_earned, "total_spent": wallet.total_spent,
            "net_worth": wallet.cash + wallet.bank_balance - total_loans,
            "bank_accounts_count": len(bank_accounts), "active_loans": total_loans,
        }

    # -- Admin / Engine --

    async def credit_cash(
        self, player_id: uuid.UUID, amount: float,
        reference: str | None = None, description: str | None = None,
    ) -> dict:
        wallet = await self._get_wallet_or_raise(player_id)
        if wallet.cash + amount > wallet.max_cash:
            raise ValidationError("Cash limit would be exceeded")
        balance_before = wallet.cash
        new_cash = wallet.cash + amount
        await self.economy_repo.update_wallet(
            player_id, cash=new_cash, total_earned=wallet.total_earned + amount,
        )
        await self.economy_repo.record_transaction({
            "player_id": player_id, "transaction_type": TransactionType.EARN,
            "amount": amount, "balance_before": balance_before,
            "balance_after": new_cash, "reference": reference,
            "description": description or f"Credit: ${amount}",
        })
        return {"amount": amount, "new_cash_balance": new_cash}

    async def debit_cash(
        self, player_id: uuid.UUID, amount: float,
        reference: str | None = None, description: str | None = None,
    ) -> dict:
        wallet = await self._get_wallet_or_raise(player_id)
        if wallet.cash < amount:
            raise ValidationError("Insufficient cash")
        balance_before = wallet.cash
        new_cash = wallet.cash - amount
        await self.economy_repo.update_wallet(
            player_id, cash=new_cash, total_spent=wallet.total_spent + amount,
        )
        await self.economy_repo.record_transaction({
            "player_id": player_id, "transaction_type": TransactionType.SPEND,
            "amount": amount, "balance_before": balance_before,
            "balance_after": new_cash, "reference": reference,
            "description": description or f"Debit: ${amount}",
        })
        return {"amount": amount, "new_cash_balance": new_cash}