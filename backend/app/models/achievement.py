from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Achievement(Base):
    __tablename__ = "achievements"

    achievement_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reward: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    player_achievements: Mapped[list[PlayerAchievement]] = relationship(
        "PlayerAchievement", back_populates="achievement"
    )


class PlayerAchievement(Base):
    __tablename__ = "player_achievements"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    player: Mapped["Player"] = relationship("Player")
    achievement: Mapped[Achievement] = relationship(
        "Achievement", back_populates="player_achievements"
    )

    __table_args__ = (
        {"comment": "Achievements unlocked by players"},
    )
