"""Vehicle base model — shared across bikes and cars."""
from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class VehicleType(StrEnum):
    BIKE = "bike"
    CAR = "car"


class FuelType(StrEnum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    NONE = "none"


class Vehicle(Base):
    __tablename__ = "vehicles"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SAEnum(VehicleType, native_enum=False), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    vin: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    license_plate: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)

    fuel_type: Mapped[FuelType] = mapped_column(
        SAEnum(FuelType, native_enum=False), default=FuelType.GASOLINE, nullable=False
    )
    fuel_level: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    max_fuel: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    health: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    engine_health: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    body_health: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    wheel_health: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    brake_health: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    suspension_health: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    top_speed: Mapped[float] = mapped_column(Float, default=120.0, nullable=False)
    acceleration: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    braking: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    handling: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)

    mileage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    garage_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("garages.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)
    garage_slot_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("garage_slots.id", ondelete="SET NULL"),
        nullable=True,
    )

    player: Mapped["Player"] = relationship("Player")
    bike: Mapped["Bike | None"] = relationship(
        "Bike", back_populates="vehicle", uselist=False
    )
    car: Mapped["Car | None"] = relationship(
        "Car", back_populates="vehicle", uselist=False
    )
    garage: Mapped["Garage | None"] = relationship("Garage", back_populates="vehicles")

    __table_args__ = (
        {"comment": "Base vehicle record shared by bikes and cars"},
    )
