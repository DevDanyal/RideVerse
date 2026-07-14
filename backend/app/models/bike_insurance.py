"""Bike insurance model — tracks insurance policies for bikes."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class InsuranceTier:
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class BikeInsurance(Base):
    """Insurance policy attached to a specific vehicle (bike)."""

    __tablename__ = "bike_insurance"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    tier: Mapped[str] = mapped_column(String(20), default=InsuranceTier.BASIC, nullable=False)
    monthly_premium: Mapped[float] = mapped_column(Float, nullable=False)
    coverage_amount: Mapped[float] = mapped_column(Float, nullable=False)
    deductible: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    vehicle: Mapped["Vehicle"] = relationship("Vehicle")

    __table_args__ = (
        {"comment": "Insurance policy for a bike"},
    )
