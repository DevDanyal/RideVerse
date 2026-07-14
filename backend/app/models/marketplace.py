from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MarketplaceItemType(StrEnum):
    VEHICLE = "vehicle"
    BIKE = "bike"
    CAR = "car"
    WEAPON = "weapon"
    ITEM = "item"
    PART = "part"


class ListingStatus(StrEnum):
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    seller_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_type: Mapped[MarketplaceItemType] = mapped_column(
        SAEnum(MarketplaceItemType, native_enum=False), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    listing_status: Mapped[ListingStatus] = mapped_column(
        SAEnum(ListingStatus, native_enum=False),
        default=ListingStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    seller: Mapped["Player"] = relationship("Player")
    sale: Mapped[MarketplaceSale | None] = relationship(
        "MarketplaceSale", back_populates="listing", uselist=False
    )


class MarketplaceSale(Base):
    __tablename__ = "marketplace_sales"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("marketplace_listings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sale_price: Mapped[float] = mapped_column(Float, nullable=False)
    sold_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    listing: Mapped[MarketplaceListing] = relationship(
        "MarketplaceListing", back_populates="sale"
    )
    buyer: Mapped["Player"] = relationship("Player", foreign_keys=[buyer_id])
    seller: Mapped["Player"] = relationship("Player", foreign_keys=[seller_id])
