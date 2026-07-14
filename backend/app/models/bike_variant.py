"""Bike variant model — defines base specifications for each bike model."""
from __future__ import annotations

import uuid

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BikeVariant(Base):
    """Template for a bike model (e.g. Honda CG125 Standard).

    Each row defines the stock specifications and upgrade limits
    for a particular bike variant that the player can purchase.
    """

    __tablename__ = "bike_variants"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="125cc", nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)

    # ── Engine specs ───────────────────────────────────────────────────────
    engine_cc: Mapped[int] = mapped_column(Integer, default=125, nullable=False)
    horsepower: Mapped[float] = mapped_column(Float, default=11.0, nullable=False)
    torque_nm: Mapped[float] = mapped_column(Float, default=10.5, nullable=False)
    cylinders: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(20), default="gasoline", nullable=False)

    # ── Performance specs ──────────────────────────────────────────────────
    top_speed_kmh: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    acceleration_0_100: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, default=128.0, nullable=False)
    braking_distance: Mapped[float] = mapped_column(Float, default=45.0, nullable=False)
    handling_rating: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)

    # ── Fuel system specs ──────────────────────────────────────────────────
    fuel_tank_liters: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
    fuel_consumption_l100km: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)

    # ── Upgrade limits ─────────────────────────────────────────────────────
    max_upgrade_level: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    __table_args__ = (
        {"comment": "Bike variant specifications (Honda CG125, etc.)"},
    )
