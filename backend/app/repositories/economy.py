"""Repository layer for economy / wallet / transaction database operations."""
from __future__ import annotations

import uuid

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.economy import ATM, DailyReward, Transaction, Wallet


class EconomyRepository:
    """Data-access layer for Wallet, Transaction, DailyReward, and ATM models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Wallet ────────────────────────────────────────────────────────────

    async def get_wallet(self, player_id: uuid.UUID) -> Wallet | None:
        stmt = select(Wallet).where(
            Wallet.player_id == player_id,
            Wallet.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_wallet(self, data: dict) -> Wallet:
        wallet = Wallet(**data)
        self._session.add(wallet)
        await self._session.flush()
        return wallet

    async def update_wallet(self, player_id: uuid.UUID, **kwargs) -> Wallet | None:
        stmt = (
            update(Wallet)
            .where(Wallet.player_id == player_id, Wallet.is_deleted.is_(False))
            .values(**kwargs)
            .returning(Wallet)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Transactions ──────────────────────────────────────────────────────

    async def record_transaction(self, data: dict) -> Transaction:
        tx = Transaction(**data)
        self._session.add(tx)
        await self._session.flush()
        return tx

    async def get_transactions(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.player_id == player_id,
                Transaction.is_deleted.is_(False),
            )
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_transactions_by_type(
        self, player_id: uuid.UUID, transaction_type: str,
        skip: int = 0, limit: int = 50,
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.player_id == player_id,
                Transaction.transaction_type == transaction_type,
                Transaction.is_deleted.is_(False),
            )
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def check_idempotency(self, idempotency_key: str) -> Transaction | None:
        stmt = select(Transaction).where(
            Transaction.idempotency_key == idempotency_key
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_transfer_between(
        self, sender_id: uuid.UUID, receiver_id: uuid.UUID
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.source_player_id == sender_id,
                Transaction.destination_player_id == receiver_id,
                Transaction.is_deleted.is_(False),
            )
            .order_by(Transaction.created_at.desc())
            .limit(10)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_transactions_today(self, player_id: uuid.UUID) -> int:
        from datetime import datetime, timezone
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = select(func.count(Transaction.id)).where(
            Transaction.player_id == player_id,
            Transaction.created_at >= today_start,
            Transaction.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    # ── Daily Rewards ─────────────────────────────────────────────────────

    async def get_daily_reward(
        self, player_id: uuid.UUID, day_number: int
    ) -> DailyReward | None:
        stmt = select(DailyReward).where(
            DailyReward.player_id == player_id,
            DailyReward.day_number == day_number,
            DailyReward.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_last_claimed_day(self, player_id: uuid.UUID) -> int:
        stmt = (
            select(DailyReward.day_number)
            .where(
                DailyReward.player_id == player_id,
                DailyReward.claimed.is_(True),
                DailyReward.is_deleted.is_(False),
            )
            .order_by(DailyReward.day_number.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return row or 0

    async def get_unclaimed_reward(
        self, player_id: uuid.UUID
    ) -> DailyReward | None:
        stmt = (
            select(DailyReward)
            .where(
                DailyReward.player_id == player_id,
                DailyReward.claimed.is_(False),
                DailyReward.is_deleted.is_(False),
            )
            .order_by(DailyReward.day_number.asc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_daily_reward(self, data: dict) -> DailyReward:
        reward = DailyReward(**data)
        self._session.add(reward)
        await self._session.flush()
        return reward

    async def update_daily_reward(
        self, reward_id: uuid.UUID, **kwargs
    ) -> DailyReward | None:
        stmt = (
            update(DailyReward)
            .where(DailyReward.id == reward_id, DailyReward.is_deleted.is_(False))
            .values(**kwargs)
            .returning(DailyReward)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── ATM ───────────────────────────────────────────────────────────────

    async def get_atm(self, atm_id: uuid.UUID) -> ATM | None:
        stmt = select(ATM).where(
            ATM.id == atm_id,
            ATM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_atms(self, skip: int = 0, limit: int = 50) -> list[ATM]:
        stmt = (
            select(ATM)
            .where(ATM.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_atm(self, data: dict) -> ATM:
        atm = ATM(**data)
        self._session.add(atm)
        await self._session.flush()
        return atm

    async def update_atm(self, atm_id: uuid.UUID, **kwargs) -> ATM | None:
        stmt = (
            update(ATM)
            .where(ATM.id == atm_id, ATM.is_deleted.is_(False))
            .values(**kwargs)
            .returning(ATM)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
