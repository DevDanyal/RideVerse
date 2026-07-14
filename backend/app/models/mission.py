from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MissionType(StrEnum):
    STORY = "story"
    DELIVERY = "delivery"
    TAXI = "taxi"
    RACING = "racing"
    WHEELIE = "wheelie"
    TIME_TRIAL = "time_trial"
    POLICE = "police"
    BUSINESS = "business"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL = "special"
    SEASONAL = "seasonal"
    AI_GENERATED = "ai_generated"


class MissionDifficulty(StrEnum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    LEGENDARY = "legendary"


class MissionStatus(StrEnum):
    AVAILABLE = "available"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Mission(Base):
    __tablename__ = "missions"

    mission_name: Mapped[str] = mapped_column(String(200), nullable=False)
    mission_type: Mapped[MissionType] = mapped_column(
        SAEnum(MissionType, native_enum=False), nullable=False, index=True
    )
    difficulty: Mapped[MissionDifficulty] = mapped_column(
        SAEnum(MissionDifficulty, native_enum=False), nullable=False, index=True
    )
    minimum_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reward_cash: Mapped[float] = mapped_column(Float, nullable=False)
    reward_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_time: Mapped[int] = mapped_column(Integer, nullable=False)
    repeatable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    player_missions: Mapped[list[PlayerMission]] = relationship(
        "PlayerMission", back_populates="mission"
    )
    mission_history: Mapped[list[MissionHistory]] = relationship(
        "MissionHistory", back_populates="mission"
    )


class PlayerMission(Base):
    __tablename__ = "player_missions"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[MissionStatus] = mapped_column(
        SAEnum(MissionStatus, native_enum=False),
        default=MissionStatus.AVAILABLE,
        nullable=False,
        index=True,
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reward_claimed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    player: Mapped["Player"] = relationship("Player")
    mission: Mapped[Mission] = relationship("Mission", back_populates="player_missions")

    __table_args__ = (
        {"comment": "Tracks a player's progress on missions"},
    )


class MissionHistory(Base):
    __tablename__ = "mission_history"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    completion_time: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_cash: Mapped[float] = mapped_column(Float, nullable=False)
    reward_experience: Mapped[int] = mapped_column(Integer, nullable=False)

    player: Mapped["Player"] = relationship("Player")
    mission: Mapped[Mission] = relationship("Mission", back_populates="mission_history")
