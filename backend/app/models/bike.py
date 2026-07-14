from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Bike(Base):
    __tablename__ = "bikes"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    engine_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    turbo_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exhaust_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    brake_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    wheel_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    tire_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    seat_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    paint_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    decal_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    headlight_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    horn_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    fuel_tank_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    suspension_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    chain_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    mirror_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    speedometer_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="bike")
