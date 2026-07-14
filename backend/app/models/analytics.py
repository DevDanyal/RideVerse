from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    player_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    event_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    player: Mapped["Player | None"] = relationship("Player")

    __table_args__ = (
        {"comment": "Analytics events for tracking player behavior"},
    )
