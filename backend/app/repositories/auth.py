"""Repository layer for authentication-related database operations."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import AccountStatus, PlayerAccount, PlayerSession, RefreshToken


class AuthRepository:
    """Data-access layer for PlayerAccount, PlayerSession, and RefreshToken."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── PlayerAccount ──────────────────────────────────────────────────────────

    async def create_account(
        self,
        email: str,
        username: str,
        password_hash: str,
    ) -> PlayerAccount:
        account = PlayerAccount(
            email=email,
            username=username,
            password_hash=password_hash,
        )
        self._session.add(account)
        await self._session.flush()
        return account

    async def get_account_by_id(self, account_id: uuid.UUID) -> PlayerAccount | None:
        stmt = select(PlayerAccount).where(
            PlayerAccount.id == account_id,
            PlayerAccount.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_account_by_email(self, email: str) -> PlayerAccount | None:
        stmt = select(PlayerAccount).where(
            PlayerAccount.email == email,
            PlayerAccount.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_account_by_username(self, username: str) -> PlayerAccount | None:
        stmt = select(PlayerAccount).where(
            PlayerAccount.username == username,
            PlayerAccount.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_login(self, account_id: uuid.UUID) -> None:
        stmt = (
            update(PlayerAccount)
            .where(PlayerAccount.id == account_id)
            .values(last_login=datetime.now(timezone.utc))
        )
        await self._session.execute(stmt)

    async def update_account_status(
        self, account_id: uuid.UUID, status: AccountStatus
    ) -> None:
        stmt = (
            update(PlayerAccount)
            .where(PlayerAccount.id == account_id)
            .values(account_status=status)
        )
        await self._session.execute(stmt)

    async def update_password_hash(
        self, account_id: uuid.UUID, password_hash: str
    ) -> None:
        stmt = (
            update(PlayerAccount)
            .where(PlayerAccount.id == account_id)
            .values(password_hash=password_hash)
        )
        await self._session.execute(stmt)

    # ── RefreshToken ───────────────────────────────────────────────────────────

    async def create_refresh_token(
        self,
        account_id: uuid.UUID,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken:
        refresh = RefreshToken(
            account_id=account_id,
            token=token,
            expires_at=expires_at,
        )
        self._session.add(refresh)
        await self._session.flush()
        return refresh

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.revoked.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(revoked=True)
        )
        await self._session.execute(stmt)

    async def revoke_all_account_tokens(self, account_id: uuid.UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.account_id == account_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
        await self._session.execute(stmt)

    # ── PlayerSession ──────────────────────────────────────────────────────────

    async def create_session(
        self,
        account_id: uuid.UUID,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> PlayerSession:
        session = PlayerSession(
            account_id=account_id,
            device_info=device_info,
            ip_address=ip_address,
            last_active=datetime.now(timezone.utc),
        )
        self._session.add(session)
        await self._session.flush()
        return session
