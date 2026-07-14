from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NotificationType(StrEnum):
    MISSION = "mission"
    FRIEND = "friend"
    MARKETPLACE = "marketplace"
    CLUB = "club"
    REWARD = "reward"
    SYSTEM = "system"
    WARNING = "warning"
    UPDATE = "update"


class Notification(Base):
    __tablename__ = "notifications"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType, native_enum=False), nullable=False, index=True
    )
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    player: Mapped["Player"] = relationship("Player")

    __table_args__ = (
        {"comment": "Player notifications"},
    )
