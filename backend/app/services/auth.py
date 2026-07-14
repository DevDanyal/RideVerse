"""Business logic for authentication, registration, and token management."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.auth import AccountStatus
from app.models.bank import AccountType, BankAccount
from app.models.character import Character, CharacterAppearance
from app.models.economy import Wallet
from app.models.inventory import Inventory
from app.models.player import Player, PlayerSettings, PlayerStatistics
from app.repositories.auth import AuthRepository

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Orchestrates registration, login, logout, and token refresh."""

    def __init__(self, auth_repo: AuthRepository) -> None:
        self._repo = auth_repo

    # ── Registration ───────────────────────────────────────────────────────────

    async def register(
        self,
        email: str,
        username: str,
        password: str,
    ) -> dict[str, Any]:
        """Create a new account and return a token pair."""
        if await self._repo.get_account_by_email(email):
            raise ConflictError("An account with this email already exists")

        if await self._repo.get_account_by_username(username):
            raise ConflictError("This username is already taken")

        password_hash = get_password_hash(password)
        account = await self._repo.create_account(
            email=email,
            username=username,
            password_hash=password_hash,
        )

        # Auto-create player profile, stats, settings, wallet, inventory
        session = self._repo._session
        player = Player(
            account_id=account.id,
            display_name=username,
            level=1,
            experience=0,
            cash=1000.0,
        )
        session.add(player)
        await session.flush()

        session.add(PlayerStatistics(player_id=player.id))
        session.add(PlayerSettings(player_id=player.id))
        session.add(Wallet(player_id=player.id, cash=1000.0, bank_balance=0.0))
        session.add(Inventory(player_id=player.id, max_slots=50, used_slots=0, total_weight=0.0))
        await session.flush()

        tokens = self._issue_tokens(account.id)
        await self._repo.create_refresh_token(
            account_id=account.id,
            token=tokens["refresh_token"],
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self._repo.create_session(account_id=account.id)

        logger.info("New account registered: %s (%s)", username, email)

        return {
            "account_id": str(account.id),
            "email": account.email,
            "username": account.username,
            "role": account.role.value,
            **tokens,
        }

    # ── Login ──────────────────────────────────────────────────────────────────

    async def login(
        self,
        email: str,
        password: str,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> dict[str, Any]:
        """Verify credentials and return a token pair."""
        account = await self._repo.get_account_by_email(email)
        if account is None:
            raise AuthenticationError("Invalid email or password")

        if account.account_status != AccountStatus.ACTIVE:
            raise AuthenticationError("Account is not active")

        if not verify_password(password, account.password_hash):
            raise AuthenticationError("Invalid email or password")

        await self._repo.update_last_login(account.id)

        tokens = self._issue_tokens(account.id)
        await self._repo.create_refresh_token(
            account_id=account.id,
            token=tokens["refresh_token"],
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self._repo.create_session(
            account_id=account.id,
            device_info=device_info,
            ip_address=ip_address,
        )

        logger.info("User logged in: %s", account.username)

        return {
            "account_id": str(account.id),
            "email": account.email,
            "username": account.username,
            "role": account.role.value,
            **tokens,
        }

    # ── Refresh Token ──────────────────────────────────────────────────────────

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Validate a refresh token and issue a new token pair."""
        payload = verify_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        stored = await self._repo.get_refresh_token(refresh_token)
        if stored is None:
            raise AuthenticationError("Refresh token has been revoked or expired")

        account = await self._repo.get_account_by_id(stored.account_id)
        if account is None or account.account_status != AccountStatus.ACTIVE:
            raise AuthenticationError("Account is not active")

        # Revoke the old refresh token (token rotation)
        await self._repo.revoke_refresh_token(refresh_token)

        tokens = self._issue_tokens(account.id)
        await self._repo.create_refresh_token(
            account_id=account.id,
            token=tokens["refresh_token"],
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

        return {
            "account_id": str(account.id),
            "email": account.email,
            "username": account.username,
            "role": account.role.value,
            **tokens,
        }

    # ── Logout ─────────────────────────────────────────────────────────────────

    async def logout(self, refresh_token: str) -> None:
        """Revoke a single refresh token (current session)."""
        payload = verify_token(refresh_token)
        if payload is None:
            return
        await self._repo.revoke_refresh_token(refresh_token)
        logger.info("User logged out (token revoked)")

    async def logout_all(self, account_id: uuid.UUID) -> None:
        """Revoke every refresh token for an account (all sessions)."""
        await self._repo.revoke_all_account_tokens(account_id)
        logger.info("All sessions revoked for account %s", account_id)

    # ── Account Lookup ─────────────────────────────────────────────────────────

    async def get_account(self, account_id: uuid.UUID) -> dict[str, Any]:
        account = await self._repo.get_account_by_id(account_id)
        if account is None:
            raise NotFoundError("Account not found")
        return {
            "id": account.id,
            "email": account.email,
            "username": account.username,
            "role": account.role.value,
            "email_verified": account.email_verified,
            "account_status": account.account_status.value,
            "created_at": account.created_at,
        }

    # ── Internal Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _issue_tokens(account_id: uuid.UUID) -> dict[str, str]:
        """Create a JWT access + refresh pair for the given account."""
        token_data = {"sub": str(account_id)}
        access = create_access_token(token_data)
        refresh = create_refresh_token(token_data)
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
