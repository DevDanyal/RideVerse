"""Repair history model — tracks all repairs performed on vehicles."""
from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RepairType:
    ENGINE = "engine"
    BODY = "body"
    BRAKES = "brakes"
    SUSPENSION = "suspension"
    WHEELS = "wheels"
    TIRES = "tires"
    FULL = "full"


class RepairHistory(Base):
    """A single repair event for a vehicle."""

    __tablename__ = "repair_history"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    garage_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("garages.id", ondelete="SET NULL"),
        nullable=True,
    )
    repair_type: Mapped[str] = mapped_column(String(50), nullable=False)
    repair_cost: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle")

    __table_args__ = (
        {"comment": "History of repairs for vehicles"},
    )
