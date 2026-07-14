from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ClubMemberRole(StrEnum):
    LEADER = "leader"
    OFFICER = "officer"
    MEMBER = "member"


class Club(Base):
    __tablename__ = "clubs"

    club_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    member_limit: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    club_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    owner: Mapped["Player"] = relationship("Player")
    members: Mapped[list[ClubMember]] = relationship(
        "ClubMember", back_populates="club", cascade="all, delete-orphan"
    )


class ClubMember(Base):
    __tablename__ = "club_members"

    club_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[ClubMemberRole] = mapped_column(
        SAEnum(ClubMemberRole, native_enum=False),
        default=ClubMemberRole.MEMBER,
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    club: Mapped[Club] = relationship("Club", back_populates="members")
    player: Mapped["Player"] = relationship("Player")

    __table_args__ = (
        {"comment": "Members of a club with their roles"},
    )
