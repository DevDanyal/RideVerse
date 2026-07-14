from __future__ import annotations

import uuid
from datetime import datetime, date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Character(Base):
    __tablename__ = "characters"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    current_health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_stamina: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_hunger: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_thirst: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    spawn_location: Mapped[str | None] = mapped_column(String(100), nullable=True)

    player: Mapped["Player"] = relationship("Player", back_populates="characters")
    appearance: Mapped[CharacterAppearance | None] = relationship(
        "CharacterAppearance", back_populates="character", uselist=False
    )

    __table_args__ = ()


class CharacterAppearance(Base):
    __tablename__ = "character_appearances"

    character_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    hair_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hair_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    eye_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    skin_tone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    face_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    beard_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tattoos: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    glasses: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mask: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    helmet: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    character: Mapped[Character] = relationship(
        "Character", back_populates="appearance"
    )
