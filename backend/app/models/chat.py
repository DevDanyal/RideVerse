from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ChannelType(StrEnum):
    GLOBAL = "global"
    LOCAL = "local"
    CLUB = "club"
    FRIEND = "friend"
    PRIVATE = "private"
    SYSTEM = "system"


class ChatChannel(Base):
    __tablename__ = "chat_channels"

    channel_name: Mapped[str] = mapped_column(String(100), nullable=False)
    channel_type: Mapped[ChannelType] = mapped_column(
        SAEnum(ChannelType, native_enum=False), nullable=False, index=True
    )

    messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage", back_populates="channel", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("chat_channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    channel: Mapped[ChatChannel] = relationship("ChatChannel", back_populates="messages")
    player: Mapped["Player"] = relationship("Player")

    __table_args__ = (
        {"comment": "Messages within chat channels"},
    )
