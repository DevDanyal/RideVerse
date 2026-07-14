from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class LeaderboardType(StrEnum):
    SPEED = "speed"
    WHEELIE = "wheelie"
    RACE = "race"
    MONEY = "money"
    LEVEL = "level"
    MISSION = "mission"


class Leaderboard(Base):
    __tablename__ = "leaderboards"

    leaderboard_type: Mapped[LeaderboardType] = mapped_column(
        SAEnum(LeaderboardType, native_enum=False), nullable=False, index=True
    )
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)

    entries: Mapped[list[LeaderboardEntry]] = relationship(
        "LeaderboardEntry", back_populates="leaderboard", cascade="all, delete-orphan"
    )


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    leaderboard_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("leaderboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    leaderboard: Mapped[Leaderboard] = relationship(
        "Leaderboard", back_populates="entries"
    )
    player: Mapped["Player"] = relationship("Player")

    __table_args__ = (
        {"comment": "Individual entries on a leaderboard"},
    )
