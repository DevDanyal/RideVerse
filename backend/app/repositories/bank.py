"""Repository layer for bank account database operations."""
from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank import BankAccount


class BankAccountRepository:
    """Data-access layer for BankAccount models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, account_id: uuid.UUID) -> BankAccount | None:
        stmt = select(BankAccount).where(
            BankAccount.id == account_id,
            BankAccount.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_player_id(self, player_id: uuid.UUID) -> list[BankAccount]:
        stmt = select(BankAccount).where(
            BankAccount.player_id == player_id,
            BankAccount.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_account_number(self, account_number: str) -> BankAccount | None:
        stmt = select(BankAccount).where(
            BankAccount.account_number == account_number,
            BankAccount.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_account(self, data: dict) -> BankAccount:
        account = BankAccount(**data)
        self._session.add(account)
        await self._session.flush()
        return account

    async def update_account(
        self, account_id: uuid.UUID, **kwargs
    ) -> BankAccount | None:
        stmt = (
            update(BankAccount)
            .where(
                BankAccount.id == account_id,
                BankAccount.is_deleted.is_(False),
            )
            .values(**kwargs)
            .returning(BankAccount)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete(self, account_id: uuid.UUID) -> bool:
        stmt = update(BankAccount).where(
            BankAccount.id == account_id,
            BankAccount.is_deleted.is_(False),
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0
