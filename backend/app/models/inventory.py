from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ItemType(StrEnum):
    WEAPON = "weapon"
    FOOD = "food"
    MEDICAL = "medical"
    VEHICLE_PART = "vehicle_part"
    MISSION_ITEM = "mission_item"
    KEY = "key"
    COLLECTIBLE = "collectible"
    AMMO = "ammo"
    OTHER = "other"


class ItemRarity(StrEnum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class InventoryAction(StrEnum):
    ADD = "add"
    REMOVE = "remove"
    USE = "use"
    EQUIP = "equip"
    UNEQUIP = "unequip"
    TRADE = "trade"
    DROP = "drop"


class Inventory(Base):
    __tablename__ = "inventories"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    max_slots: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    used_slots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_weight: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    player: Mapped["Player"] = relationship("Player")
    items: Mapped[list[InventoryItem]] = relationship(
        "InventoryItem", back_populates="inventory", cascade="all, delete-orphan"
    )

    __table_args__ = ()


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    inventory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_type: Mapped[ItemType] = mapped_column(
        SAEnum(ItemType, native_enum=False), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    rarity: Mapped[ItemRarity] = mapped_column(
        SAEnum(ItemRarity, native_enum=False), nullable=False, index=True
    )
    weight: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    durability: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    stackable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    inventory: Mapped[Inventory] = relationship("Inventory", back_populates="items")

    __table_args__ = (
        {"comment": "Individual items within a player's inventory"},
    )


class InventoryHistory(Base):
    __tablename__ = "inventory_history"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[InventoryAction] = mapped_column(
        SAEnum(InventoryAction, native_enum=False), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        {"comment": "Audit trail for inventory changes"},
    )
