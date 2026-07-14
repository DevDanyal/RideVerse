from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PropertyType(StrEnum):
    HOUSE = "house"
    APARTMENT = "apartment"
    COMMERCIAL = "commercial"
    WAREHOUSE = "warehouse"


class Property(Base):
    __tablename__ = "properties"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    property_type: Mapped[PropertyType] = mapped_column(
        SAEnum(PropertyType, native_enum=False), nullable=False, index=True
    )
    property_name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    storage_capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    owner: Mapped["Player"] = relationship("Player")
