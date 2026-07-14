"""Repository layer for weapon-related database operations."""
from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weapon import (
    PlayerWeapon,
    Weapon,
    WeaponAmmunition,
    WeaponAttachment,
)


class WeaponRepository:
    """Data-access layer for weapon, player_weapon, attachment, and ammo models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Weapon Catalog ────────────────────────────────────────────────────

    async def get_weapon_by_id(self, weapon_id: uuid.UUID) -> Weapon | None:
        stmt = select(Weapon).where(
            Weapon.id == weapon_id,
            Weapon.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_weapons(self, skip: int = 0, limit: int = 50) -> list[Weapon]:
        stmt = (
            select(Weapon)
            .where(Weapon.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_weapons_by_type(
        self, weapon_type: str, skip: int = 0, limit: int = 50
    ) -> list[Weapon]:
        stmt = (
            select(Weapon)
            .where(Weapon.weapon_type == weapon_type, Weapon.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_weapon(self, data: dict) -> Weapon:
        weapon = Weapon(**data)
        self._session.add(weapon)
        await self._session.flush()
        return weapon

    # ── Player Weapons ────────────────────────────────────────────────────

    async def get_player_weapon_by_id(
        self, player_weapon_id: uuid.UUID
    ) -> PlayerWeapon | None:
        stmt = select(PlayerWeapon).where(
            PlayerWeapon.id == player_weapon_id,
            PlayerWeapon.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_player_weapons(
        self, player_id: uuid.UUID
    ) -> list[PlayerWeapon]:
        stmt = (
            select(PlayerWeapon)
            .where(
                PlayerWeapon.player_id == player_id,
                PlayerWeapon.is_deleted.is_(False),
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_equipped_weapon(
        self, player_id: uuid.UUID
    ) -> PlayerWeapon | None:
        stmt = select(PlayerWeapon).where(
            PlayerWeapon.player_id == player_id,
            PlayerWeapon.equipped.is_(True),
            PlayerWeapon.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_player_weapon(self, data: dict) -> PlayerWeapon:
        pw = PlayerWeapon(**data)
        self._session.add(pw)
        await self._session.flush()
        return pw

    async def update_player_weapon(
        self, player_weapon_id: uuid.UUID, data: dict
    ) -> PlayerWeapon | None:
        stmt = (
            update(PlayerWeapon)
            .where(
                PlayerWeapon.id == player_weapon_id,
                PlayerWeapon.is_deleted.is_(False),
            )
            .values(**data)
            .returning(PlayerWeapon)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_player_weapon(
        self, player_weapon_id: uuid.UUID
    ) -> bool:
        stmt = update(PlayerWeapon).where(
            PlayerWeapon.id == player_weapon_id,
            PlayerWeapon.is_deleted.is_(False),
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Attachments ───────────────────────────────────────────────────────

    async def get_attachment(
        self, player_weapon_id: uuid.UUID
    ) -> WeaponAttachment | None:
        stmt = select(WeaponAttachment).where(
            WeaponAttachment.player_weapon_id == player_weapon_id,
            WeaponAttachment.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_attachment(self, data: dict) -> WeaponAttachment:
        att = WeaponAttachment(**data)
        self._session.add(att)
        await self._session.flush()
        return att

    async def update_attachment(
        self, player_weapon_id: uuid.UUID, data: dict
    ) -> WeaponAttachment | None:
        stmt = (
            update(WeaponAttachment)
            .where(
                WeaponAttachment.player_weapon_id == player_weapon_id,
                WeaponAttachment.is_deleted.is_(False),
            )
            .values(**data)
            .returning(WeaponAttachment)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Ammunition ────────────────────────────────────────────────────────

    async def get_ammo(
        self, player_id: uuid.UUID, ammo_type: str
    ) -> WeaponAmmunition | None:
        stmt = select(WeaponAmmunition).where(
            WeaponAmmunition.player_id == player_id,
            WeaponAmmunition.ammo_type == ammo_type,
            WeaponAmmunition.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_ammo(self, player_id: uuid.UUID) -> list[WeaponAmmunition]:
        stmt = select(WeaponAmmunition).where(
            WeaponAmmunition.player_id == player_id,
            WeaponAmmunition.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_or_update_ammo(
        self, player_id: uuid.UUID, ammo_type: str, quantity_delta: int
    ) -> WeaponAmmunition:
        existing = await self.get_ammo(player_id, ammo_type)
        if existing:
            existing.quantity = max(0, existing.quantity + quantity_delta)
            await self._session.flush()
            return existing
        ammo = WeaponAmmunition(
            player_id=player_id,
            ammo_type=ammo_type,
            quantity=max(0, quantity_delta),
        )
        self._session.add(ammo)
        await self._session.flush()
        return ammo
