from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Car(Base):
    __tablename__ = "cars"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    engine_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    transmission_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    brake_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    suspension_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    wheel_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    tire_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    paint_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    interior_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    spoiler_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hood_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    roof_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    window_tint: Mapped[str] = mapped_column(String(20), default="none", nullable=False)
    nitrous_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    headlight_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="car")
