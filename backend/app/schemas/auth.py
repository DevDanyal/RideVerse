from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class AccountRole(str, Enum):
    GUEST = "guest"
    PLAYER = "player"
    MODERATOR = "moderator"
    ADMIN = "admin"
    DEVELOPER = "developer"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class RegisterRequest(BaseModel):
    """Request to register a new account."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Request to log in."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token pair returned after authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=1800, description="Access token TTL in seconds")


class RefreshTokenRequest(BaseModel):
    """Request to refresh an expired access token."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Request to logout — revokes the given refresh token."""

    refresh_token: str


class AccountResponse(BaseModel):
    """Public account information."""

    id: uuid.UUID
    email: str
    username: str
    role: AccountRole = AccountRole.PLAYER
    email_verified: bool = False
    account_status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime | None = None
