"""Weapon models — catalog, player-owned instances, attachments, and ammunition."""
from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class WeaponType(StrEnum):
    PISTOL = "pistol"
    REVOLVER = "revolver"
    SMG = "smg"
    SHOTGUN = "shotgun"
    ASSAULT_RIFLE = "assault_rifle"
    SNIPER_RIFLE = "sniper_rifle"
    LMG = "lmg"
    MELEE = "melee"


class AmmoType(StrEnum):
    CAL_9MM = "9mm"
    CAL_45 = "45acp"
    CAL_556 = "5.56"
    CAL_762 = "7.62"
    CAL_12GAUGE = "12gauge"
    CAL_50 = "50cal"
    NONE = "none"


class Weapon(Base):
    """Catalog weapon — what the player can purchase from a shop."""

    __tablename__ = "weapons"

    weapon_name: Mapped[str] = mapped_column(String(100), nullable=False)
    weapon_type: Mapped[WeaponType] = mapped_column(
        String(20), nullable=False, index=True
    )
    damage: Mapped[float] = mapped_column(Float, nullable=False)
    fire_rate: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    range_distance: Mapped[float] = mapped_column(Float, nullable=False)
    magazine_size: Mapped[int] = mapped_column(Integer, nullable=False)
    reload_time: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    max_durability: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    sell_price: Mapped[float] = mapped_column(Float, nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ammo_type: Mapped[str] = mapped_column(String(20), default="none", nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    player_weapons: Mapped[list[PlayerWeapon]] = relationship(
        "PlayerWeapon", back_populates="weapon"
    )


class PlayerWeapon(Base):
    """A weapon owned by a player instance."""

    __tablename__ = "player_weapons"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    weapon_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("weapons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_ammo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserve_ammo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    durability: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    skin: Mapped[str | None] = mapped_column(String(100), nullable=True)

    player: Mapped["Player"] = relationship("Player")
    weapon: Mapped[Weapon] = relationship("Weapon", back_populates="player_weapons")
    attachment: Mapped[WeaponAttachment | None] = relationship(
        "WeaponAttachment", back_populates="player_weapon", uselist=False
    )

    __table_args__ = (
        {"comment": "Weapons owned by a player"},
    )


class WeaponAttachment(Base):
    """Attachments for a player's specific weapon instance."""

    __tablename__ = "weapon_attachments"

    player_weapon_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("player_weapons.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    scope: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    silencer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extended_magazine: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    grip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    laser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    flashlight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    player_weapon: Mapped[PlayerWeapon] = relationship(
        "PlayerWeapon", back_populates="attachment"
    )

    __table_args__ = (
        {"comment": "Weapon attachments for a player's weapon instance"},
    )


class WeaponAmmunition(Base):
    """Player's ammunition inventory by ammo type."""

    __tablename__ = "weapon_ammunition"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ammo_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    player: Mapped["Player"] = relationship("Player")

    __table_args__ = (
        {"comment": "Player ammunition inventory by type"},
    )
