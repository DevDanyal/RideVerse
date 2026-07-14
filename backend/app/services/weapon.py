"""Business logic for the Weapon system."""
from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.repositories.economy import EconomyRepository
from app.repositories.inventory import InventoryRepository
from app.repositories.player import PlayerRepository
from app.repositories.weapon import WeaponRepository

VALID_ATTACHMENT_TYPES = [
    "scope", "silencer", "extended_magazine", "grip", "laser", "flashlight",
]

AMMO_PRICE_PER_ROUND = {
    "9mm": 5.0,
    "45acp": 8.0,
    "5.56": 12.0,
    "7.62": 18.0,
    "12gauge": 10.0,
    "50cal": 30.0,
}

REPAIR_COST_PER_UNIT = 2.5

ATTACHMENT_MODIFIERS = {
    "scope": {"accuracy": 1.15, "range": 1.10},
    "silencer": {"damage": 0.95, "accuracy": 1.05},
    "extended_magazine": {},
    "grip": {"accuracy": 1.08, "fire_rate": 1.05},
    "laser": {"accuracy": 1.12},
    "flashlight": {},
}


class WeaponService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.weapon_repo = WeaponRepository(session)
        self.economy_repo = EconomyRepository(session)
        self.player_repo = PlayerRepository(session)
        self.inventory_repo = InventoryRepository(session)

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        player = await self.player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def _charge_wallet(self, player_id: uuid.UUID, amount: float) -> None:
        wallet = await self.economy_repo.get_wallet(player_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        if wallet.cash < amount:
            raise ValidationError("Insufficient funds")
        wallet.cash -= amount
        await self.session.flush()

    async def _refund_wallet(self, player_id: uuid.UUID, amount: float) -> None:
        wallet = await self.economy_repo.get_wallet(player_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        wallet.cash += amount
        await self.session.flush()

    # ── Catalog ───────────────────────────────────────────────────────────

    async def get_all_weapons(
        self, weapon_type: str | None = None, skip: int = 0, limit: int = 50
    ) -> list:
        if weapon_type:
            return await self.weapon_repo.get_weapons_by_type(weapon_type, skip, limit)
        return await self.weapon_repo.get_all_weapons(skip, limit)

    async def get_weapon(self, weapon_id: uuid.UUID):
        weapon = await self.weapon_repo.get_weapon_by_id(weapon_id)
        if not weapon:
            raise NotFoundError("Weapon not found")
        return weapon

    # ── Purchase ──────────────────────────────────────────────────────────

    async def buy_weapon(
        self, player_id: uuid.UUID, weapon_id: uuid.UUID
    ) -> dict:
        weapon = await self.get_weapon(weapon_id)

        player = await self.player_repo.get_by_id(player_id)
        if player and player.level < weapon.required_level:
            raise ValidationError(
                f"Required level: {weapon.required_level}, your level: {player.level}"
            )

        await self._charge_wallet(player_id, weapon.purchase_price)

        magazine = weapon.magazine_size
        pw = await self.weapon_repo.create_player_weapon({
            "player_id": player_id,
            "weapon_id": weapon.id,
            "current_ammo": magazine,
            "reserve_ammo": magazine,
            "durability": weapon.max_durability,
            "equipped": False,
        })

        return {
            "player_weapon": pw,
            "cost": weapon.purchase_price,
            "message": f"{weapon.weapon_name} purchased successfully",
        }

    # ── Sell ──────────────────────────────────────────────────────────────

    async def sell_weapon(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID
    ) -> dict:
        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        if not weapon:
            raise NotFoundError("Weapon catalog entry not found")

        durability_factor = pw.durability / weapon.max_durability
        sold_price = int(weapon.sell_price * durability_factor)

        await self._refund_wallet(player_id, sold_price)
        await self.weapon_repo.soft_delete_player_weapon(player_weapon_id)

        return {
            "sold_price": sold_price,
            "message": f"{weapon.weapon_name} sold for ${sold_price}",
        }

    # ── Equip / Unequip ───────────────────────────────────────────────────

    async def equip_weapon(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID, equip: bool = True
    ) -> dict:
        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        if equip:
            current = await self.weapon_repo.get_equipped_weapon(player_id)
            if current and current.id != player_weapon_id:
                await self.weapon_repo.update_player_weapon(
                    current.id, {"equipped": False}
                )

        await self.weapon_repo.update_player_weapon(
            player_weapon_id, {"equipped": equip}
        )

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        action = "equipped" if equip else "unequipped"
        return {
            "player_weapon_id": player_weapon_id,
            "equipped": equip,
            "message": f"{weapon.weapon_name} {action}",
        }

    # ── Ammunition ────────────────────────────────────────────────────────

    async def get_ammo_inventory(self, player_id: uuid.UUID) -> list:
        return await self.weapon_repo.get_all_ammo(player_id)

    async def purchase_ammo(
        self, player_id: uuid.UUID, ammo_type: str, quantity: int
    ) -> dict:
        if ammo_type not in AMMO_PRICE_PER_ROUND:
            raise ValidationError(
                f"Invalid ammo type: {ammo_type}. Valid: {list(AMMO_PRICE_PER_ROUND.keys())}"
            )
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        price_per = AMMO_PRICE_PER_ROUND[ammo_type]
        total_cost = price_per * quantity
        await self._charge_wallet(player_id, total_cost)

        ammo = await self.weapon_repo.create_or_update_ammo(
            player_id, ammo_type, quantity
        )

        return {
            "ammo_type": ammo_type,
            "quantity_purchased": quantity,
            "total_cost": total_cost,
            "new_quantity": ammo.quantity,
        }

    # ── Reload ────────────────────────────────────────────────────────────

    async def reload_weapon(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID
    ) -> dict:
        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        if not weapon:
            raise NotFoundError("Weapon catalog entry not found")

        if weapon.ammo_type == "none":
            raise ValidationError("This weapon does not use ammunition")

        if pw.current_ammo >= weapon.magazine_size:
            raise ValidationError("Magazine is already full")

        needed = weapon.magazine_size - pw.current_ammo

        ammo_inv = await self.weapon_repo.get_ammo(player_id, weapon.ammo_type)
        available = ammo_inv.quantity if ammo_inv else 0

        if available <= 0:
            raise ValidationError(
                f"No {weapon.ammo_type} ammunition available. Purchase some first."
            )

        to_load = min(needed, available)
        new_current = pw.current_ammo + to_load
        new_reserve = available - to_load

        await self.weapon_repo.update_player_weapon(
            player_weapon_id,
            {"current_ammo": new_current, "reserve_ammo": new_reserve},
        )
        await self.weapon_repo.create_or_update_ammo(
            player_id, weapon.ammo_type, -to_load
        )

        return {
            "weapon_name": weapon.weapon_name,
            "ammo_loaded": to_load,
            "current_ammo": new_current,
            "reserve_ammo": new_reserve,
            "message": f"Loaded {to_load} rounds of {weapon.ammo_type}",
        }

    # ── Durability ────────────────────────────────────────────────────────

    async def reduce_durability(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID, amount: float = 1.0
    ) -> dict:
        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        if not weapon:
            raise NotFoundError("Weapon catalog entry not found")

        new_durability = max(0.0, pw.durability - amount)
        await self.weapon_repo.update_player_weapon(
            player_weapon_id, {"durability": new_durability}
        )

        return {
            "weapon_name": weapon.weapon_name,
            "previous_durability": pw.durability,
            "new_durability": new_durability,
            "message": f"{weapon.weapon_name} durability reduced by {amount}",
        }

    # ── Repair ────────────────────────────────────────────────────────────

    async def get_repair_cost(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID
    ) -> dict:
        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        if not weapon:
            raise NotFoundError("Weapon catalog entry not found")

        durability_to_repair = weapon.max_durability - pw.durability
        repair_cost = round(durability_to_repair * REPAIR_COST_PER_UNIT, 2)

        return {
            "current_durability": pw.durability,
            "max_durability": weapon.max_durability,
            "durability_to_repair": round(durability_to_repair, 2),
            "repair_cost": repair_cost,
        }

    async def repair_weapon(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID
    ) -> dict:
        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        if not weapon:
            raise NotFoundError("Weapon catalog entry not found")

        durability_to_repair = weapon.max_durability - pw.durability
        if durability_to_repair <= 0:
            raise ValidationError("Weapon is already at maximum durability")

        repair_cost = round(durability_to_repair * REPAIR_COST_PER_UNIT, 2)
        await self._charge_wallet(player_id, repair_cost)

        await self.weapon_repo.update_player_weapon(
            player_weapon_id, {"durability": weapon.max_durability}
        )

        return {
            "player_weapon_id": player_weapon_id,
            "repair_cost": repair_cost,
            "new_durability": weapon.max_durability,
            "message": f"{weapon.weapon_name} repaired to full durability",
        }

    # ── Attachments ───────────────────────────────────────────────────────

    async def get_attachments(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID
    ) -> WeaponAttachment | None:
        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        return await self.weapon_repo.get_attachment(player_weapon_id)

    async def add_attachment(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID, attachment_type: str
    ) -> dict:
        if attachment_type not in VALID_ATTACHMENT_TYPES:
            raise ValidationError(
                f"Invalid attachment: {attachment_type}. Valid: {VALID_ATTACHMENT_TYPES}"
            )

        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        if not weapon:
            raise NotFoundError("Weapon catalog entry not found")

        attachment_cost = int(weapon.purchase_price * 0.15)
        await self._charge_wallet(player_id, attachment_cost)

        existing = await self.weapon_repo.get_attachment(player_weapon_id)
        if existing:
            if getattr(existing, attachment_type, False):
                raise ConflictError(f"Attachment '{attachment_type}' already installed")
            await self.weapon_repo.update_attachment(
                player_weapon_id, {attachment_type: True}
            )
        else:
            await self.weapon_repo.create_attachment({
                "player_weapon_id": player_weapon_id,
                attachment_type: True,
            })

        return {
            "attachment_type": attachment_type,
            "cost": attachment_cost,
            "message": f"{attachment_type} installed on {weapon.weapon_name}",
        }

    async def remove_attachment(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID, attachment_type: str
    ) -> dict:
        if attachment_type not in VALID_ATTACHMENT_TYPES:
            raise ValidationError(f"Invalid attachment: {attachment_type}")

        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        if not weapon:
            raise NotFoundError("Weapon catalog entry not found")

        existing = await self.weapon_repo.get_attachment(player_weapon_id)
        if not existing or not getattr(existing, attachment_type, False):
            raise NotFoundError(f"Attachment '{attachment_type}' not installed")

        await self.weapon_repo.update_attachment(
            player_weapon_id, {attachment_type: False}
        )

        refund = int(weapon.purchase_price * 0.05)
        await self._refund_wallet(player_id, refund)

        return {
            "attachment_type": attachment_type,
            "refund": refund,
            "message": f"{attachment_type} removed from {weapon.weapon_name}",
        }

    # ── Stats ─────────────────────────────────────────────────────────────

    async def get_weapon_stats(
        self, player_id: uuid.UUID, player_weapon_id: uuid.UUID
    ) -> dict:
        pw = await self.weapon_repo.get_player_weapon_by_id(player_weapon_id)
        if not pw or pw.player_id != player_id:
            raise NotFoundError("Player weapon not found")

        weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
        if not weapon:
            raise NotFoundError("Weapon catalog entry not found")

        attachment = await self.weapon_repo.get_attachment(player_weapon_id)

        effective_damage = weapon.damage
        effective_fire_rate = weapon.fire_rate
        effective_accuracy = weapon.accuracy
        effective_range = weapon.range_distance
        attached_names = []

        if attachment:
            for att_name in VALID_ATTACHMENT_TYPES:
                if getattr(attachment, att_name, False):
                    attached_names.append(att_name)
                    mods = ATTACHMENT_MODIFIERS.get(att_name, {})
                    effective_damage *= mods.get("damage", 1.0)
                    effective_fire_rate *= mods.get("fire_rate", 1.0)
                    effective_accuracy *= mods.get("accuracy", 1.0)
                    effective_range *= mods.get("range", 1.0)

        return {
            "weapon_name": weapon.weapon_name,
            "weapon_type": weapon.weapon_type,
            "base_damage": weapon.damage,
            "effective_damage": round(effective_damage, 2),
            "base_fire_rate": weapon.fire_rate,
            "effective_fire_rate": round(effective_fire_rate, 2),
            "base_accuracy": weapon.accuracy,
            "effective_accuracy": round(min(100.0, effective_accuracy), 2),
            "base_range": weapon.range_distance,
            "effective_range": round(effective_range, 2),
            "magazine_size": weapon.magazine_size,
            "reload_time": weapon.reload_time,
            "weight": weapon.weight,
            "durability": pw.durability,
            "attachments": attached_names,
        }

    # ── Player Weapons List ───────────────────────────────────────────────

    async def get_player_weapons(self, player_id: uuid.UUID) -> list:
        pws = await self.weapon_repo.get_player_weapons(player_id)
        result = []
        for pw in pws:
            weapon = await self.weapon_repo.get_weapon_by_id(pw.weapon_id)
            attachment = await self.weapon_repo.get_attachment(pw.id)
            result.append({
                "player_weapon": pw,
                "weapon": weapon,
                "attachment": attachment,
            })
        return result
