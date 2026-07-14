from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AccountRole(StrEnum):
    GUEST = "guest"
    PLAYER = "player"
    MODERATOR = "moderator"
    ADMIN = "admin"
    DEVELOPER = "developer"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class PlayerAccount(Base):
    __tablename__ = "player_accounts"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    account_status: Mapped[AccountStatus] = mapped_column(
        SAEnum(AccountStatus, native_enum=False),
        default=AccountStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    role: Mapped[AccountRole] = mapped_column(
        SAEnum(AccountRole, native_enum=False),
        default=AccountRole.PLAYER,
        nullable=False,
        index=True,
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    player: Mapped["Player | None"] = relationship(
        "Player", back_populates="account", uselist=False
    )
    sessions: Mapped[list[PlayerSession]] = relationship(
        "PlayerSession", back_populates="account", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken", back_populates="account", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_player_accounts_email_username", "email", "username"),
    )


class PlayerSession(Base):
    __tablename__ = "player_sessions"

    account_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("player_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    refresh_token_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    last_active: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    account: Mapped[PlayerAccount] = relationship(
        "PlayerAccount", back_populates="sessions"
    )

    __table_args__ = (Index("ix_player_sessions_account_id", "account_id"),)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    account_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("player_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    account: Mapped[PlayerAccount] = relationship(
        "PlayerAccount", back_populates="refresh_tokens"
    )

    __table_args__ = (
        Index("ix_refresh_tokens_account_id", "account_id"),
        Index("ix_refresh_tokens_token", "token"),
    )
