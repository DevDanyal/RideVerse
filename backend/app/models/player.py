from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Player(Base):
    __tablename__ = "players"

    account_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("player_accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cash: Mapped[float] = mapped_column(Float, default=1000.0, nullable=False)
    bank_balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reputation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    stamina: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    energy: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    wanted_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_server: Mapped[str | None] = mapped_column(String(100), nullable=True)
    current_region: Mapped[str | None] = mapped_column(String(100), nullable=True)

    account: Mapped["PlayerAccount"] = relationship(
        "PlayerAccount", back_populates="player", uselist=False
    )
    statistics: Mapped[PlayerStatistics | None] = relationship(
        "PlayerStatistics", back_populates="player", uselist=False
    )
    settings: Mapped[PlayerSettings | None] = relationship(
        "PlayerSettings", back_populates="player", uselist=False
    )
    characters: Mapped[list["Character"]] = relationship(
        "Character", back_populates="player"
    )
    inventory: Mapped["Inventory | None"] = relationship(
        "Inventory", back_populates="player", uselist=False
    )
    wallet: Mapped["Wallet | None"] = relationship(
        "Wallet", back_populates="player", uselist=False
    )
    bank_accounts: Mapped[list["BankAccount"]] = relationship(
        "BankAccount", back_populates="player"
    )
    achievements: Mapped[list["PlayerAchievement"]] = relationship(
        "PlayerAchievement", back_populates="player"
    )
    garage: Mapped[list["Garage"]] = relationship(
        "Garage", back_populates="player"
    )

    __table_args__ = (
        {"comment": "Core player profile data"},
    )


class PlayerStatistics(Base):
    __tablename__ = "player_statistics"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    total_play_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    distance_walked: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    distance_driven: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    missions_completed: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    races_won: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vehicles_owned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weapons_owned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    money_earned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    money_spent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    highest_speed: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    highest_wheelie_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    daily_login_streak: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    player: Mapped[Player] = relationship("Player", back_populates="statistics")


class PlayerSettings(Base):
    __tablename__ = "player_settings"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    graphics_quality: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )
    audio_volume: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    music_volume: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    voice_chat: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    control_layout: Mapped[str] = mapped_column(
        String(50), default="default", nullable=False
    )
    camera_mode: Mapped[str] = mapped_column(
        String(50), default="third_person", nullable=False
    )
    theme: Mapped[str] = mapped_column(String(20), default="dark", nullable=False)

    player: Mapped[Player] = relationship("Player", back_populates="settings")
