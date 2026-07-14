from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class WeaponType(StrEnum):
    MELEE = "melee"
    PISTOL = "pistol"
    REVOLVER = "revolver"
    SMG = "smg"
    SHOTGUN = "shotgun"
    ASSAULT_RIFLE = "assault_rifle"
    SNIPER_RIFLE = "sniper_rifle"
    MACHINE_GUN = "machine_gun"
    THROWABLE = "throwable"
    SPECIAL = "special"


class Weapon(Base):
    __tablename__ = "weapons"

    weapon_name: Mapped[str] = mapped_column(String(100), nullable=False)
    weapon_type: Mapped[WeaponType] = mapped_column(
        SAEnum(WeaponType, native_enum=False), nullable=False, index=True
    )
    damage: Mapped[float] = mapped_column(Float, nullable=False)
    range: Mapped[float] = mapped_column(Float, nullable=False)
    fire_rate: Mapped[float] = mapped_column(Float, nullable=False)
    reload_speed: Mapped[float] = mapped_column(Float, nullable=False)
    ammo_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    sell_price: Mapped[float] = mapped_column(Float, nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    player_weapons: Mapped[list[PlayerWeapon]] = relationship(
        "PlayerWeapon", back_populates="weapon"
    )
    upgrades: Mapped[list[WeaponUpgrade]] = relationship(
        "WeaponUpgrade", back_populates="weapon"
    )


class PlayerWeapon(Base):
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
    ammo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    durability: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    skin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    player: Mapped["Player"] = relationship("Player")
    weapon: Mapped[Weapon] = relationship("Weapon", back_populates="player_weapons")

    __table_args__ = (
        {"comment": "Weapons owned by a player"},
    )


class WeaponUpgrade(Base):
    __tablename__ = "weapon_upgrades"

    weapon_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("weapons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scope: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extended_magazine: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    silencer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    laser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    grip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    skin: Mapped[str | None] = mapped_column(String(100), nullable=True)

    weapon: Mapped[Weapon] = relationship("Weapon", back_populates="upgrades")
