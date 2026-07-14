from __future__ import annotations

import uuid
from datetime import date
from enum import StrEnum

from sqlalchemy import Date, Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class BusinessType(StrEnum):
    RESTAURANT = "restaurant"
    WORKSHOP = "workshop"
    DEALERSHIP = "dealership"
    WAREHOUSE = "warehouse"
    SHOP = "shop"
    OFFICE = "office"
    FACTORY = "factory"


class Business(Base):
    __tablename__ = "businesses"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_type: Mapped[BusinessType] = mapped_column(
        SAEnum(BusinessType, native_enum=False), nullable=False, index=True
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    daily_income: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    employees: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    owner: Mapped["Player"] = relationship("Player")
    income_records: Mapped[list[BusinessIncome]] = relationship(
        "BusinessIncome", back_populates="business", cascade="all, delete-orphan"
    )


class BusinessIncome(Base):
    __tablename__ = "business_income"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    income: Mapped[float] = mapped_column(Float, nullable=False)
    expenses: Mapped[float] = mapped_column(Float, nullable=False)
    net_profit: Mapped[float] = mapped_column(Float, nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)

    business: Mapped[Business] = relationship(
        "Business", back_populates="income_records"
    )
