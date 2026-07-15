"""Mission system models — definitions, player progress, objectives, and history."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# ── Enums ─────────────────────────────────────────────────────────────────────


class MissionCategory(StrEnum):
    STORY = "story"
    SIDE = "side"
    DAILY = "daily"
    WEEKLY = "weekly"
    DELIVERY = "delivery"
    RACING = "racing"
    TAXI = "taxi"
    POLICE = "police"
    BUSINESS = "business"


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


class ObjectiveType(StrEnum):
    REACH_LOCATION = "reach_location"
    COLLECT_ITEMS = "collect_items"
    ELIMINATE_TARGETS = "eliminate_targets"
    DELIVER_ITEM = "deliver_item"
    ESCORT_TARGET = "escort_target"
    RACE_CHECKPOINT = "race_checkpoint"
    SURVIVE_TIME = "survive_time"
    EARN_MONEY = "earn_money"
    PERFORM_STUNT = "perform_stunt"
    EVADE_PURSUER = "evade_pursuer"


# ── Mission Definition ────────────────────────────────────────────────────────


class Mission(Base):
    """A mission definition that players can accept and complete."""

    __tablename__ = "missions"

    mission_name: Mapped[str] = mapped_column(String(200), nullable=False)
    mission_description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[MissionCategory] = mapped_column(
        String(20), nullable=False, index=True
    )
    difficulty: Mapped[MissionDifficulty] = mapped_column(
        String(20), nullable=False, index=True
    )

    # Requirements
    minimum_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_vehicle_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    required_weapon_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )

    # Rewards
    reward_money: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reward_reputation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reward_items: Mapped[str | None] = mapped_column(Text, nullable=True)
    reward_vehicles: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Constraints
    time_limit_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repeatable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    objectives: Mapped[list[MissionObjective]] = relationship(
        "MissionObjective", back_populates="mission", cascade="all, delete-orphan"
    )
    player_missions: Mapped[list[PlayerMission]] = relationship(
        "PlayerMission", back_populates="mission"
    )
    history: Mapped[list[MissionHistory]] = relationship(
        "MissionHistory", back_populates="mission"
    )


# ── Mission Objective ─────────────────────────────────────────────────────────


class MissionObjective(Base):
    """An individual objective within a mission."""

    __tablename__ = "mission_objectives"

    mission_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    objective_type: Mapped[ObjectiveType] = mapped_column(
        String(30), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    target_value: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    target_location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    mission: Mapped[Mission] = relationship("Mission", back_populates="objectives")

    __table_args__ = (
        Index("ix_mission_objectives_mission_order", "mission_id", "order_index"),
        {"comment": "Objectives within a mission definition"},
    )


# ── Player Mission (Progress Tracking) ───────────────────────────────────────


class PlayerMission(Base):
    """Tracks a single player's progress on a specific mission instance."""

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
        String(20), default=MissionStatus.AVAILABLE, nullable=False, index=True
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    objectives_completed: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reward_claimed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    last_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_available_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    player: Mapped["Player"] = relationship("Player")
    mission: Mapped[Mission] = relationship("Mission", back_populates="player_missions")
    objective_progresses: Mapped[list[PlayerObjectiveProgress]] = relationship(
        "PlayerObjectiveProgress",
        back_populates="player_mission",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_player_missions_player_mission", "player_id", "mission_id", unique=True),
        {"comment": "Tracks a player's progress on missions"},
    )


# ── Player Objective Progress ─────────────────────────────────────────────────


class PlayerObjectiveProgress(Base):
    """Tracks a player's progress on an individual mission objective."""

    __tablename__ = "player_objective_progress"

    player_mission_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("player_missions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    objective_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("mission_objectives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    player_mission: Mapped[PlayerMission] = relationship(
        "PlayerMission", back_populates="objective_progresses"
    )
    objective: Mapped[MissionObjective] = relationship("MissionObjective")

    __table_args__ = (
        Index(
            "ix_player_objective_progress_unique",
            "player_mission_id",
            "objective_id",
            unique=True,
        ),
        {"comment": "Tracks a player's progress on individual mission objectives"},
    )


# ── Mission History ───────────────────────────────────────────────────────────


class MissionHistory(Base):
    """Permanent record of every mission completion attempt."""

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
    outcome: Mapped[str] = mapped_column(String(20), nullable=False)
    completion_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    objectives_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    objectives_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    money_earned: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reputation_earned: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    failure_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)

    player: Mapped["Player"] = relationship("Player")
    mission: Mapped[Mission] = relationship("Mission", back_populates="history")

    __table_args__ = (
        {"comment": "Permanent record of mission completion attempts"},
    )


# ── Mission Cooldown ──────────────────────────────────────────────────────────


class MissionCooldown(Base):
    """Tracks cooldown state for repeatable missions per player."""

    __tablename__ = "mission_cooldowns"

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
    last_completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    next_available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    player: Mapped["Player"] = relationship("Player")
    mission: Mapped[Mission] = relationship("Mission")

    __table_args__ = (
        Index("ix_mission_cooldowns_player_mission", "player_id", "mission_id", unique=True),
        {"comment": "Tracks cooldown state for repeatable missions per player"},
    )


# ── Mission Statistics ────────────────────────────────────────────────────────


class MissionStatistics(Base):
    """Aggregated mission completion statistics for a player."""

    __tablename__ = "mission_statistics"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    total_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cancelled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_time_played_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_money_earned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    story_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    side_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weekly_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delivery_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    racing_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    taxi_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    police_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    business_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    player: Mapped["Player"] = relationship("Player")

    __table_args__ = (
        Index("ix_mission_statistics_player", "player_id", unique=True),
        {"comment": "Aggregated mission statistics per player"},
    )
