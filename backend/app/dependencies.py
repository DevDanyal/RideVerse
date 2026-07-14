"""Shared FastAPI dependencies — database sessions, auth, role gates."""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator, Sequence
from functools import wraps
from typing import Any, Callable

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import verify_token
from app.database.session import async_session_maker
from app.models.auth import AccountRole, AccountStatus
from app.repositories.auth import AuthRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

# ── Database Session ───────────────────────────────────────────────────────────


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session with auto-commit / rollback."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Authentication ─────────────────────────────────────────────────────────────


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    """Decode a JWT access token and return the payload.

    Raises ``AuthenticationError`` when the token is missing, invalid, or
    expired.
    """
    payload = verify_token(token)
    if payload is None:
        raise AuthenticationError("Invalid or expired token")
    if payload.get("type") != "access":
        raise AuthenticationError("Token type must be 'access'")
    if payload.get("sub") is None:
        raise AuthenticationError("Token missing subject claim")
    return payload


async def get_current_active_user(
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Extend ``get_current_user`` to verify the account still exists and is active."""
    repo = AuthRepository(session)
    account = await repo.get_account_by_id(uuid.UUID(current_user["sub"]))
    if account is None:
        raise AuthenticationError("Account not found")
    if account.account_status != AccountStatus.ACTIVE:
        raise AuthenticationError("Account is not active")
    current_user["role"] = account.role.value
    return current_user


# ── Role-Based Access Control ──────────────────────────────────────────────────

_ROLE_HIERARCHY: dict[str, int] = {
    AccountRole.GUEST: 0,
    AccountRole.PLAYER: 1,
    AccountRole.MODERATOR: 2,
    AccountRole.ADMIN: 3,
    AccountRole.DEVELOPER: 4,
}


def require_role(*allowed_roles: str | AccountRole) -> Callable[..., Any]:
    """Return a dependency that enforces a minimum role level.

    Usage::

        @router.get("/admin", dependencies=[Depends(require_role(AccountRole.ADMIN))])
        async def admin_only(): ...

    If multiple roles are given the user needs **any** of them (OR logic).
    """

    async def _check(
        current_user: dict[str, Any] = Depends(get_current_active_user),
    ) -> dict[str, Any]:
        user_role = current_user.get("role", AccountRole.GUEST)
        allowed_strs = {r.value if isinstance(r, AccountRole) else r for r in allowed_roles}
        if user_role not in allowed_strs:
            raise AuthorizationError(
                f"Required role: {' or '.join(allowed_strs)} — your role: {user_role}"
            )
        return current_user

    return _check


def require_min_role(minimum: str | AccountRole) -> Callable[..., Any]:
    """Require the user's role to be at least ``minimum`` in the hierarchy.

    Usage::

        @router.get("/mod+", dependencies=[Depends(require_min_role(AccountRole.MODERATOR))])
        async def moderators_and_above(): ...
    """

    async def _check(
        current_user: dict[str, Any] = Depends(get_current_active_user),
    ) -> dict[str, Any]:
        user_level = _ROLE_HIERARCHY.get(current_user.get("role", AccountRole.GUEST), 0)
        required_level = _ROLE_HIERARCHY.get(
            minimum.value if isinstance(minimum, AccountRole) else minimum, 0
        )
        if user_level < required_level:
            raise AuthorizationError(
                f"Minimum role required: {minimum} — your role: {current_user.get('role')}"
            )
        return current_user

    return _check


# Re-export
__all__ = [
    "get_db_session",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_min_role",
]
