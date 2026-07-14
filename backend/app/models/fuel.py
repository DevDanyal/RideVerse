"""Fuel system models — fuel stations and transaction history."""
from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FuelStation(Base):
    """A fuel station in the game world."""

    __tablename__ = "fuel_stations"

    station_name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fuel_price: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)

    __table_args__ = (
        {"comment": "Fuel stations where players can refuel"},
    )


class FuelTransaction(Base):
    """A fuel purchase event."""

    __tablename__ = "fuel_transactions"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    station_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fuel_stations.id", ondelete="SET NULL"),
        nullable=True,
    )
    fuel_amount: Mapped[float] = mapped_column(Float, nullable=False)
    price_paid: Mapped[float] = mapped_column(Float, nullable=False)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle")
    station: Mapped["FuelStation | None"] = relationship("FuelStation")

    __table_args__ = (
        {"comment": "History of fuel purchases per vehicle"},
    )
