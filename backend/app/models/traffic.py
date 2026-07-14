from __future__ import annotations

from enum import StrEnum

from sqlalchemy import Enum as SAEnum, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class TrafficSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    severity: Mapped[TrafficSeverity] = mapped_column(
        SAEnum(TrafficSeverity, native_enum=False),
        default=TrafficSeverity.LOW,
        nullable=False,
        index=True,
    )
