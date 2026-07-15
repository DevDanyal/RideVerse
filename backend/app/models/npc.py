"""NPC system models — base NPCs, schedules, dialogues, professions, relationships, interactions, statistics, spawns."""
from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, Float, ForeignKey, JSON, String, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# ── Enums ──────────────────────────────────────────────────────────────────────


class NpcCategory(StrEnum):
    CITIZEN = "citizen"
    SHOPKEEPER = "shopkeeper"
    MECHANIC = "mechanic"
    TAXI_DRIVER = "taxi_driver"
    POLICE_OFFICER = "police_officer"
    DOCTOR = "doctor"
    BUSINESS_OWNER = "business_owner"


class NpcStatus(StrEnum):
    IDLE = "idle"
    WORKING = "working"
    SLEEPING = "sleeping"
    PATROLLING = "patrolling"
    RESTING = "resting"
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"


class NpcSchedulePeriod(StrEnum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


class RelationshipLevel(StrEnum):
    HOSTILE = "hostile"
    UNFRIENDLY = "unfriendly"
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    TRUSTED = "trusted"
    LOVED = "loved"


class SpawnCondition(StrEnum):
    ALWAYS = "always"
    DAY_ONLY = "day_only"
    NIGHT_ONLY = "night_only"
    WEATHER = "weather"
    MISSION = "mission"
    RANDOM = "random"


# ── NPC Base ───────────────────────────────────────────────────────────────────


class Npc(Base):
    __tablename__ = "npcs"

    npc_name: Mapped[str] = mapped_column(String(100), nullable=False)
    npc_category: Mapped[NpcCategory] = mapped_column(
        SAEnum(NpcCategory, native_enum=False), nullable=False, index=True
    )
    npc_status: Mapped[NpcStatus] = mapped_column(
        SAEnum(NpcStatus, native_enum=False), default=NpcStatus.IDLE, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Location / spawning
    spawn_location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    spawn_location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    spawn_location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    home_location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    home_location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    home_location_z: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Appearance / metadata
    appearance_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    schedules: Mapped[list[NpcSchedule]] = relationship(
        "NpcSchedule", back_populates="npc", cascade="all, delete-orphan"
    )
    dialogues: Mapped[list[NpcDialogue]] = relationship(
        "NpcDialogue", back_populates="npc", cascade="all, delete-orphan"
    )
    profession: Mapped[NpcProfession | None] = relationship(
        "NpcProfession", back_populates="npc", uselist=False, cascade="all, delete-orphan"
    )
    statistics: Mapped[NpcStatistics | None] = relationship(
        "NpcStatistics", back_populates="npc", uselist=False, cascade="all, delete-orphan"
    )
    spawn_points: Mapped[list[NpcSpawn]] = relationship(
        "NpcSpawn", back_populates="npc", cascade="all, delete-orphan"
    )

    __table_args__ = (
        {"comment": "Non-Player Characters — core entity"},
    )


# ── NPC Schedule ───────────────────────────────────────────────────────────────


class NpcSchedule(Base):
    __tablename__ = "npc_schedules"

    npc_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("npcs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period: Mapped[NpcSchedulePeriod] = mapped_column(
        SAEnum(NpcSchedulePeriod, native_enum=False), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)
    activity: Mapped[str] = mapped_column(String(100), nullable=False)
    location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[NpcStatus] = mapped_column(
        SAEnum(NpcStatus, native_enum=False), default=NpcStatus.IDLE, nullable=False
    )

    npc: Mapped[Npc] = relationship("Npc", back_populates="schedules")

    __table_args__ = (
        {"comment": "NPC daily schedule entries — period-based activities"},
    )


# ── NPC Dialogue ───────────────────────────────────────────────────────────────


class NpcDialogue(Base):
    __tablename__ = "npc_dialogues"

    npc_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("npcs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dialogue_key: Mapped[str] = mapped_column(String(100), nullable=False)
    dialogue_text: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required_relationship: Mapped[RelationshipLevel | None] = mapped_column(
        SAEnum(RelationshipLevel, native_enum=False), nullable=True
    )
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    is_greeting: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_farewell: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_mission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    npc: Mapped[Npc] = relationship("Npc", back_populates="dialogues")

    __table_args__ = (
        {"comment": "Dialogue lines for NPCs — context-aware and relationship-gated"},
    )


# ── NPC Profession ─────────────────────────────────────────────────────────────


class NpcProfession(Base):
    __tablename__ = "npc_professions"

    npc_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("npcs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    profession_type: Mapped[NpcCategory] = mapped_column(
        SAEnum(NpcCategory, native_enum=False), nullable=False
    )
    skill_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    services_offered: Mapped[str | None] = mapped_column(JSON, nullable=True)
    service_price_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reputation: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(200), nullable=True)

    npc: Mapped[Npc] = relationship("Npc", back_populates="profession")

    __table_args__ = (
        {"comment": "NPC profession details — skills, services, reputation"},
    )


# ── NPC Relationship ──────────────────────────────────────────────────────────


class NpcRelationship(Base):
    __tablename__ = "npc_relationships"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    npc_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("npcs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    level: Mapped[RelationshipLevel] = mapped_column(
        SAEnum(RelationshipLevel, native_enum=False),
        default=RelationshipLevel.NEUTRAL,
        nullable=False,
    )
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_interactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    positive_interactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    negative_interactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_interaction_at: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        {"comment": "Player-NPC relationship tracking"},
    )


# ── NPC Interaction ───────────────────────────────────────────────────────────


class NpcInteraction(Base):
    __tablename__ = "npc_interactions"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    npc_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("npcs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dialogue_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reputation_change: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    was_positive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        {"comment": "History of player-NPC interactions"},
    )


# ── NPC Statistics ─────────────────────────────────────────────────────────────


class NpcStatistics(Base):
    __tablename__ = "npc_statistics"

    npc_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("npcs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    total_interactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_players: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_dialogues_spoken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_services_provided: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    times_thanked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_attacked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_defeated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    money_earned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    npc: Mapped[Npc] = relationship("Npc", back_populates="statistics")

    __table_args__ = (
        {"comment": "NPC-level statistics — interactions, services, ratings"},
    )


# ── NPC Spawn Point ───────────────────────────────────────────────────────────


class NpcSpawn(Base):
    __tablename__ = "npc_spawns"

    npc_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("npcs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    zone_name: Mapped[str] = mapped_column(String(200), nullable=False)
    location_x: Mapped[float] = mapped_column(Float, nullable=False)
    location_y: Mapped[float] = mapped_column(Float, nullable=False)
    location_z: Mapped[float] = mapped_column(Float, nullable=False)
    spawn_condition: Mapped[SpawnCondition] = mapped_column(
        SAEnum(SpawnCondition, native_enum=False),
        default=SpawnCondition.ALWAYS,
        nullable=False,
    )
    min_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_players_nearby: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    respawn_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    npc: Mapped[Npc] = relationship("Npc", back_populates="spawn_points")

    __table_args__ = (
        {"comment": "NPC spawn points — locations, conditions, respawn rules"},
    )
