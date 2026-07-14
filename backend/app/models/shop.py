"""Shop system models — shops, shop items, and shop transaction history."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ShopCategory(StrEnum):
    BIKE_DEALER = "bike_dealer"
    CAR_DEALER = "car_dealer"
    WEAPON_SHOP = "weapon_shop"
    CLOTHING_SHOP = "clothing_shop"
    FOOD_SHOP = "food_shop"
    FUEL_STATION = "fuel_station"
    REPAIR_SHOP = "repair_shop"
    CONVENIENCE_STORE = "convenience_store"


class ShopTransactionType(StrEnum):
    BUY = "buy"
    SELL = "sell"


class Shop(Base):
    """A physical shop in the game world."""

    __tablename__ = "shops"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[ShopCategory] = mapped_column(
        SAEnum(ShopCategory, native_enum=False), nullable=False, index=True
    )
    owner_player_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    min_player_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    items: Mapped[list[ShopItem]] = relationship(
        "ShopItem", back_populates="shop", cascade="all, delete-orphan"
    )
    transactions: Mapped[list[ShopTransaction]] = relationship(
        "ShopTransaction", back_populates="shop"
    )

    __table_args__ = (
        {"comment": "Shops in the game world"},
    )


class ShopItem(Base):
    """An item available for purchase in a shop."""

    __tablename__ = "shop_items"

    shop_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)
    max_stock: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)
    restock_amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    restock_interval_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    last_restock: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_player_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_purchases_per_player: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    shop: Mapped[Shop] = relationship("Shop", back_populates="items")

    __table_args__ = (
        {"comment": "Items available in shops"},
    )


class ShopTransaction(Base):
    """Record of a shop purchase or sale."""

    __tablename__ = "shop_transactions"

    shop_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_applied: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    transaction_type: Mapped[ShopTransactionType] = mapped_column(
        SAEnum(ShopTransactionType, native_enum=False), nullable=False, index=True
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    shop: Mapped[Shop] = relationship("Shop", back_populates="transactions")
    player: Mapped["Player"] = relationship("Player")

    __table_args__ = (
        {"comment": "Shop transaction history"},
    )
