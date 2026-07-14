"""Car variant model — defines base specifications for each car model."""
from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CarVariant(Base):
    """Template for a car model (e.g. Suzuki Swift, Toyota Hilux).

    Each row defines the stock specifications and upgrade limits
    for a particular car variant that the player can purchase.
    """

    __tablename__ = "car_variants"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="sedan", nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)

    # ── Engine specs ───────────────────────────────────────────────────────
    engine_cc: Mapped[int] = mapped_column(Integer, default=1600, nullable=False)
    horsepower: Mapped[float] = mapped_column(Float, default=120.0, nullable=False)
    torque_nm: Mapped[float] = mapped_column(Float, default=150.0, nullable=False)
    cylinders: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(20), default="gasoline", nullable=False)

    # ── Body specs ─────────────────────────────────────────────────────────
    doors: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    cargo_space_liters: Mapped[float] = mapped_column(Float, default=400.0, nullable=False)

    # ── Performance specs ──────────────────────────────────────────────────
    top_speed_kmh: Mapped[float] = mapped_column(Float, default=180.0, nullable=False)
    acceleration_0_100: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, default=1200.0, nullable=False)
    braking_distance: Mapped[float] = mapped_column(Float, default=40.0, nullable=False)
    handling_rating: Mapped[float] = mapped_column(Float, default=75.0, nullable=False)

    # ── Fuel system specs ──────────────────────────────────────────────────
    fuel_tank_liters: Mapped[float] = mapped_column(Float, default=45.0, nullable=False)
    fuel_consumption_l100km: Mapped[float] = mapped_column(Float, default=7.0, nullable=False)

    # ── Upgrade limits ─────────────────────────────────────────────────────
    max_upgrade_level: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    __table_args__ = (
        {"comment": "Car variant specifications (Suzuki Swift, Toyota Hilux, etc.)"},
    )
