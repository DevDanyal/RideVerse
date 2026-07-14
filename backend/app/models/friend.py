from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FriendStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class Friend(Base):
    __tablename__ = "friends"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    friend_player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[FriendStatus] = mapped_column(
        SAEnum(FriendStatus, native_enum=False),
        default=FriendStatus.PENDING,
        nullable=False,
        index=True,
    )

    player: Mapped["Player"] = relationship(
        "Player", foreign_keys=[player_id], back_populates=None
    )
    friend: Mapped["Player"] = relationship(
        "Player", foreign_keys=[friend_player_id], back_populates=None
    )

    __table_args__ = (
        {"comment": "Friend relationships between players"},
    )
