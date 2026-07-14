from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NpcType(StrEnum):
    PEDESTRIAN = "pedestrian"
    POLICE = "police"
    MECHANIC = "mechanic"
    DOCTOR = "doctor"
    SHOPKEEPER = "shopkeeper"
    TAXI_DRIVER = "taxi_driver"
    BUSINESS_OWNER = "business_owner"
    GUARD = "guard"
    CONSTRUCTION = "construction"
    DELIVERY = "delivery"
    RACER = "racer"
    MISSION = "mission"


class Npc(Base):
    __tablename__ = "npcs"

    npc_name: Mapped[str] = mapped_column(String(100), nullable=False)
    npc_type: Mapped[NpcType] = mapped_column(
        SAEnum(NpcType, native_enum=False), nullable=False, index=True
    )
    location: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dialogue_set: Mapped[str | None] = mapped_column(String(100), nullable=True)
    schedule_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    dialogues: Mapped[list[NpcDialogue]] = relationship(
        "NpcDialogue", back_populates="npc", cascade="all, delete-orphan"
    )


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
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    npc: Mapped[Npc] = relationship("Npc", back_populates="dialogues")

    __table_args__ = (
        {"comment": "Dialogue lines for NPCs"},
    )
