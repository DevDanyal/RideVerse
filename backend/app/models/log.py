from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class LogSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    actor: Mapped["Player | None"] = relationship("Player")

    __table_args__ = (
        {"comment": "Audit trail for important system actions"},
    )


class ErrorLog(Base):
    __tablename__ = "error_logs"

    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[LogSeverity] = mapped_column(
        SAEnum(LogSeverity, native_enum=False),
        default=LogSeverity.MEDIUM,
        nullable=False,
        index=True,
    )

    __table_args__ = (
        {"comment": "Error logs from various services"},
    )
