from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Garage(Base):
    __tablename__ = "garages"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    garage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)

    player: Mapped["Player"] = relationship("Player")
    slots: Mapped[list[GarageSlot]] = relationship(
        "GarageSlot", back_populates="garage", cascade="all, delete-orphan"
    )
    vehicles: Mapped[list["Vehicle"]] = relationship("Vehicle", back_populates="garage")


class GarageSlot(Base):
    __tablename__ = "garage_slots"

    garage_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("garages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    slot_number: Mapped[int] = mapped_column(Integer, nullable=False)
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
    )
    occupied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    garage: Mapped[Garage] = relationship("Garage", back_populates="slots")
    vehicle: Mapped["Vehicle | None"] = relationship(
        "Vehicle", back_populates="garage_slot"
    )

    __table_args__ = (
        {"comment": "Individual parking slots within a garage"},
    )
