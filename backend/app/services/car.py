"""Business logic for the Car system."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.car import Car
from app.models.car_insurance import CarInsurance
from app.repositories.car import CarRepository
from app.repositories.economy import EconomyRepository
from app.repositories.garage import GarageRepository
from app.repositories.player import PlayerRepository
from app.repositories.vehicle import VehicleRepository

VALID_UPGRADE_COMPONENTS = [
    "engine", "turbo", "exhaust", "transmission", "brake", "suspension",
    "wheel", "tire", "nitrous", "interior", "seat", "steering_wheel",
    "horn", "headlight", "taillight", "spoiler", "hood", "roof", "mirror",
]

INSURANCE_TIERS = {
    "basic": {"monthly_premium": 100, "coverage": 10000, "deductible": 1000},
    "standard": {"monthly_premium": 300, "coverage": 40000, "deductible": 500},
    "premium": {"monthly_premium": 800, "coverage": 150000, "deductible": 0},
}

REPAIR_COST_PER_UNIT = {
    "engine": 30, "body": 12, "brakes": 18, "suspension": 25,
    "wheels": 15, "tires": 10, "full": 60,
}

UPGRADE_MULTIPLIER_PER_LEVEL = 0.05

UPGRADE_FIELDS = [
    "engine", "turbo", "exhaust", "transmission", "brake", "suspension",
    "wheel", "tire", "nitrous", "interior", "seat", "steering_wheel",
    "horn", "headlight", "taillight", "spoiler", "hood", "roof", "mirror",
]

COMPONENT_TO_HEALTH_FIELD = {
    "engine": "engine_health",
    "body": "body_health",
    "brakes": "brake_health",
    "suspension": "suspension_health",
    "wheels": "wheel_health",
    "tires": "wheel_health",
}


class CarService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.car_repo = CarRepository(session)
        self.vehicle_repo = VehicleRepository(session)
        self.economy_repo = EconomyRepository(session)
        self.garage_repo = GarageRepository(session)
        self.player_repo = PlayerRepository(session)

    async def _get_player_or_raise(self, account_id: UUID):
        player = await self.player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def _charge_wallet(self, player_id: UUID, amount: float) -> None:
        wallet = await self.economy_repo.get_wallet(player_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        if wallet.cash < amount:
            raise ValidationError("Insufficient funds")
        wallet.cash -= amount
        await self.session.flush()

    async def _refund_wallet(self, player_id: UUID, amount: float) -> None:
        wallet = await self.economy_repo.get_wallet(player_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        wallet.cash += amount
        await self.session.flush()

    async def _get_wallet_balance(self, player_id: UUID) -> float:
        wallet = await self.economy_repo.get_wallet(player_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        return wallet.cash

    # ── Variants ──────────────────────────────────────────────────────────

    async def get_variants(self, skip: int = 0, limit: int = 50) -> list:
        return await self.car_repo.get_all_variants(skip=skip, limit=limit)

    async def get_variant(self, variant_id: UUID):
        variant = await self.car_repo.get_variant_by_id(variant_id)
        if not variant:
            raise NotFoundError("Car variant not found")
        return variant

    # ── Purchase / Sell ───────────────────────────────────────────────────

    async def purchase_car(self, player_id: UUID, variant_id: UUID, car_name: str) -> dict:
        variant = await self.car_repo.get_variant_by_id(variant_id)
        if not variant:
            raise NotFoundError("Car variant not found")

        await self._charge_wallet(player_id, variant.purchase_price)

        garages = await self.garage_repo.get_by_player_id(player_id)
        if not garages:
            raise NotFoundError("No garage found. Purchase a garage first.")
        garage = garages[0]

        vehicle = await self.vehicle_repo.create(
            player_id=player_id,
            vehicle_type="car",
            name=car_name,
            brand=variant.brand,
            model=variant.model_name,
            year=variant.year,
            vin=f"2HGBH41JXMN{uuid.uuid4().hex[:6].upper()}"[:17],
            license_plate=f"C{uuid.uuid4().hex[:5].upper()}"[:10],
            purchase_price=variant.purchase_price,
            current_value=variant.purchase_price,
            fuel_level=variant.fuel_tank_liters,
            max_fuel=variant.fuel_tank_liters,
            health=100.0,
            engine_health=100.0,
            body_health=100.0,
            wheel_health=100.0,
            brake_health=100.0,
            suspension_health=100.0,
            top_speed=variant.top_speed_kmh,
            acceleration=variant.acceleration_0_100,
            braking=variant.braking_distance,
            handling=variant.handling_rating,
            mileage=0.0,
            is_primary=False,
        )

        car = Car(
            vehicle_id=vehicle.id,
            variant_id=variant.id,
            engine_level=1, turbo_level=0, exhaust_level=1,
            transmission_level=1, brake_level=1, suspension_level=1,
            wheel_level=1, tire_level=1, nitrous_level=0,
            interior_level=1, seat_level=1, steering_wheel_level=1,
            horn_level=1, headlight_level=1, taillight_level=1,
            spoiler_level=0, hood_level=1, roof_level=1, mirror_level=1,
            paint_id=None, window_tint="none", license_plate_text=None,
        )
        self.session.add(car)
        await self.session.flush()

        slots = await self.garage_repo.get_slots(garage.id)
        next_slot_num = len(slots) + 1
        slot = await self.garage_repo.create_slot(
            garage_id=garage.id,
            slot_number=next_slot_num,
            vehicle_id=vehicle.id,
            occupied=True,
        )

        return {
            "vehicle": vehicle,
            "car": car,
            "variant": variant,
            "garage_slot": slot,
        }

    async def sell_car(self, player_id: UUID, vehicle_id: UUID) -> dict:
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle or vehicle.player_id != player_id:
            raise NotFoundError("Car not found")

        car = await self.car_repo.get_by_vehicle_id(vehicle_id)
        if not car:
            raise NotFoundError("Car record not found")

        variant = await self.car_repo.get_variant_by_id(car.variant_id)
        if not variant:
            raise NotFoundError("Car variant not found")

        sold_price = int(variant.purchase_price * 0.70)
        await self._refund_wallet(player_id, sold_price)

        await self.car_repo.delete(car.id)
        await self.vehicle_repo.soft_delete(vehicle_id)

        return {
            "sold_price": sold_price,
            "message": f"Car '{vehicle.name}' sold for ${sold_price}",
        }

    # ── List / Detail ─────────────────────────────────────────────────────

    async def get_player_cars(self, player_id: UUID) -> list[dict]:
        cars = await self.car_repo.get_by_player_id(player_id)
        result = []
        for c in cars:
            variant = await self.car_repo.get_variant_by_id(c.variant_id)
            vehicle = await self.vehicle_repo.get_by_id(c.vehicle_id)
            result.append({
                "vehicle": vehicle,
                "car": c,
                "variant": variant,
            })
        return result

    async def get_car_detail(self, player_id: UUID, vehicle_id: UUID) -> dict:
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle or vehicle.player_id != player_id:
            raise NotFoundError("Car not found")

        car = await self.car_repo.get_by_vehicle_id(vehicle_id)
        if not car:
            raise NotFoundError("Car record not found")

        variant = await self.car_repo.get_variant_by_id(car.variant_id)
        insurance = await self.car_repo.get_insurance(vehicle_id)

        return {
            "vehicle": vehicle,
            "car": car,
            "variant": variant,
            "damage": {
                "health": vehicle.health,
                "engine_health": vehicle.engine_health,
                "body_health": vehicle.body_health,
                "wheel_health": vehicle.wheel_health,
                "brake_health": vehicle.brake_health,
                "suspension_health": vehicle.suspension_health,
            },
            "insurance": insurance,
        }

    # ── Upgrades ──────────────────────────────────────────────────────────

    async def upgrade_component(
        self, player_id: UUID, vehicle_id: UUID,
        component: str, target_level: int,
    ) -> dict:
        if component not in VALID_UPGRADE_COMPONENTS:
            raise ValidationError(f"Invalid component: {component}")

        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle or vehicle.player_id != player_id:
            raise NotFoundError("Car not found")

        car = await self.car_repo.get_by_vehicle_id(vehicle_id)
        if not car:
            raise NotFoundError("Car record not found")

        variant = await self.car_repo.get_variant_by_id(car.variant_id)
        if not variant:
            raise NotFoundError("Car variant not found")

        if target_level < 1 or target_level > variant.max_upgrade_level:
            raise ValidationError(
                f"Target level must be between 1 and {variant.max_upgrade_level}"
            )

        level_field = f"{component}_level"
        current_level = getattr(car, level_field, 1)
        if target_level <= current_level:
            raise ValidationError("Target level must be higher than current level")

        upgrade_cost = int(variant.purchase_price * 0.05) * target_level
        await self._charge_wallet(player_id, upgrade_cost)

        await self.car_repo.update(car.id, {level_field: target_level})

        updated_car = await self.car_repo.get_by_vehicle_id(vehicle_id)
        effective_stats = self._compute_effective_stats(variant, updated_car)
        await self.vehicle_repo.update(vehicle_id, **{
            "top_speed": effective_stats["top_speed"],
            "acceleration": effective_stats["acceleration"],
            "braking": effective_stats["braking"],
            "handling": effective_stats["handling"],
        })

        return {
            "component": component,
            "previous_level": current_level,
            "new_level": target_level,
            "cost": upgrade_cost,
            "effective_stats": effective_stats,
        }

    # ── Customization ─────────────────────────────────────────────────────

    async def update_customization(
        self, player_id: UUID, vehicle_id: UUID,
        customization_data: dict,
    ) -> Car:
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle or vehicle.player_id != player_id:
            raise NotFoundError("Car not found")

        car = await self.car_repo.get_by_vehicle_id(vehicle_id)
        if not car:
            raise NotFoundError("Car record not found")

        allowed_keys = {"paint_id", "window_tint", "license_plate_text"}
        update_data = {k: v for k, v in customization_data.items() if k in allowed_keys}
        if not update_data:
            raise ValidationError("No valid customization fields provided")

        await self.car_repo.update(car.id, update_data)
        return await self.car_repo.get_by_vehicle_id(vehicle_id)

    # ── Performance ───────────────────────────────────────────────────────

    async def get_performance_stats(self, vehicle_id: UUID) -> dict:
        car = await self.car_repo.get_by_vehicle_id(vehicle_id)
        if not car:
            raise NotFoundError("Car not found")

        variant = await self.car_repo.get_variant_by_id(car.variant_id)
        if not variant:
            raise NotFoundError("Car variant not found")

        return self._compute_effective_stats(variant, car)

    # ── Fuel ───────────────────────────────────────────────────────────────

    async def purchase_fuel(
        self, player_id: UUID, vehicle_id: UUID,
        station_id: UUID, fuel_liters: float,
    ) -> dict:
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle or vehicle.player_id != player_id:
            raise NotFoundError("Car not found")

        station = await self.car_repo.get_fuel_station(station_id)
        if not station:
            raise NotFoundError("Fuel station not found")

        fuel_needed = vehicle.max_fuel - vehicle.fuel_level
        if fuel_liters > fuel_needed:
            raise ValidationError(
                f"Cannot add {fuel_liters}L. Tank can only hold {fuel_needed:.2f}L more"
            )

        cost = round(station.fuel_price * fuel_liters, 2)
        await self._charge_wallet(player_id, cost)

        new_fuel_level = vehicle.fuel_level + fuel_liters
        await self.vehicle_repo.update(vehicle_id, fuel_level=new_fuel_level)

        await self.car_repo.add_fuel_transaction({
            "vehicle_id": vehicle_id,
            "station_id": station_id,
            "fuel_amount": fuel_liters,
            "price_paid": cost,
        })

        return {
            "fuel_added": fuel_liters,
            "cost": cost,
            "new_fuel_level": new_fuel_level,
            "max_fuel": vehicle.max_fuel,
            "station_name": station.station_name,
        }

    async def get_fuel_info(self, vehicle_id: UUID) -> dict:
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError("Vehicle not found")

        car = await self.car_repo.get_by_vehicle_id(vehicle_id)
        if not car:
            raise NotFoundError("Car not found")

        fuel_to_fill = vehicle.max_fuel - vehicle.fuel_level

        return {
            "fuel_level": vehicle.fuel_level,
            "max_fuel": vehicle.max_fuel,
            "fuel_price_per_liter": 1.5,
            "cost_for_full_tank": round(fuel_to_fill * 1.5, 2),
        }

    # ── Damage ────────────────────────────────────────────────────────────

    async def get_damage_report(self, vehicle_id: UUID) -> dict:
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError("Vehicle not found")

        return {
            "health": vehicle.health,
            "engine_health": vehicle.engine_health,
            "body_health": vehicle.body_health,
            "wheel_health": vehicle.wheel_health,
            "brake_health": vehicle.brake_health,
            "suspension_health": vehicle.suspension_health,
        }

    async def apply_damage(
        self, player_id: UUID, vehicle_id: UUID,
        damage_type: str, damage_amount: float,
    ) -> dict:
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle or vehicle.player_id != player_id:
            raise NotFoundError("Car not found")

        update_fields: dict = {}

        if damage_type == "full":
            for field in ["engine_health", "body_health", "wheel_health", "brake_health", "suspension_health"]:
                current = getattr(vehicle, field)
                update_fields[field] = max(0.0, current - damage_amount)
        elif damage_type in COMPONENT_TO_HEALTH_FIELD:
            field = COMPONENT_TO_HEALTH_FIELD[damage_type]
            current = getattr(vehicle, field)
            update_fields[field] = max(0.0, current - damage_amount)
        else:
            raise ValidationError(f"Invalid damage type: {damage_type}")

        all_health = [
            update_fields.get("engine_health", vehicle.engine_health),
            update_fields.get("body_health", vehicle.body_health),
            update_fields.get("wheel_health", vehicle.wheel_health),
            update_fields.get("brake_health", vehicle.brake_health),
            update_fields.get("suspension_health", vehicle.suspension_health),
        ]
        update_fields["health"] = round(sum(all_health) / len(all_health), 2)

        await self.vehicle_repo.update(vehicle_id, **update_fields)

        updated = await self.vehicle_repo.get_by_id(vehicle_id)
        return {
            "damage_type": damage_type,
            "damage_amount": damage_amount,
            "new_health": update_fields["health"],
            "damage_report": {
                "engine_health": updated.engine_health,
                "body_health": updated.body_health,
                "wheel_health": updated.wheel_health,
                "brake_health": updated.brake_health,
                "suspension_health": updated.suspension_health,
            },
        }

    # ── Repair ────────────────────────────────────────────────────────────

    async def get_repair_cost(self, vehicle_id: UUID, repair_type: str) -> dict:
        if repair_type not in REPAIR_COST_PER_UNIT:
            raise ValidationError(f"Invalid repair type: {repair_type}")

        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError("Vehicle not found")

        cost_per_unit = REPAIR_COST_PER_UNIT[repair_type]

        if repair_type == "full":
            damage_fields = [
                max(0, 100 - vehicle.engine_health),
                max(0, 100 - vehicle.body_health),
                max(0, 100 - vehicle.wheel_health),
                max(0, 100 - vehicle.brake_health),
                max(0, 100 - vehicle.suspension_health),
            ]
            total_damage = sum(damage_fields)
        else:
            health_field = COMPONENT_TO_HEALTH_FIELD.get(repair_type)
            if health_field:
                total_damage = max(0, 100 - getattr(vehicle, health_field))
            else:
                total_damage = 0

        total_cost = round(total_damage * cost_per_unit, 2)
        return {
            "repair_type": repair_type,
            "estimated_cost": total_cost,
            "current_damage_level": round(total_damage, 2),
            "damage_to_repair": round(total_damage, 2),
        }

    async def repair_car(
        self, player_id: UUID, vehicle_id: UUID, repair_type: str,
    ) -> dict:
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle or vehicle.player_id != player_id:
            raise NotFoundError("Car not found")

        repair_info = await self.get_repair_cost(vehicle_id, repair_type)
        total_cost = repair_info["estimated_cost"]

        if total_cost <= 0:
            raise ValidationError("No damage to repair")

        await self._charge_wallet(player_id, total_cost)

        update_fields: dict = {}
        if repair_type == "full":
            for field in ["engine_health", "body_health", "wheel_health", "brake_health", "suspension_health"]:
                update_fields[field] = 100.0
        elif repair_type in COMPONENT_TO_HEALTH_FIELD:
            update_fields[COMPONENT_TO_HEALTH_FIELD[repair_type]] = 100.0

        update_fields["health"] = 100.0
        await self.vehicle_repo.update(vehicle_id, **update_fields)

        garage_list = await self.garage_repo.get_by_player_id(player_id)
        garage_id = garage_list[0].id if garage_list else None

        await self.car_repo.add_repair_record({
            "vehicle_id": vehicle_id,
            "garage_id": garage_id,
            "repair_type": repair_type,
            "repair_cost": total_cost,
            "description": f"Repaired {repair_type} - cost ${total_cost}",
        })

        updated = await self.vehicle_repo.get_by_id(vehicle_id)
        return {
            "vehicle_id": vehicle_id,
            "repair_type": repair_type,
            "repair_cost": total_cost,
            "new_health_values": {
                "health": updated.health,
                "engine_health": updated.engine_health,
                "body_health": updated.body_health,
                "wheel_health": updated.wheel_health,
                "brake_health": updated.brake_health,
                "suspension_health": updated.suspension_health,
            },
            "message": f"Successfully repaired {repair_type} on {vehicle.name}",
        }

    # ── Insurance ──────────────────────────────────────────────────────────

    async def purchase_insurance(
        self, player_id: UUID, vehicle_id: UUID, tier: str,
    ) -> dict:
        if tier not in INSURANCE_TIERS:
            raise ValidationError(f"Invalid insurance tier: {tier}")

        vehicle = await self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle or vehicle.player_id != player_id:
            raise NotFoundError("Car not found")

        existing = await self.car_repo.get_insurance(vehicle_id)
        if existing and existing.is_active:
            raise ConflictError("Active insurance policy already exists for this car")

        tier_info = INSURANCE_TIERS[tier]
        await self._charge_wallet(player_id, tier_info["monthly_premium"])

        insurance = await self.car_repo.create_insurance({
            "vehicle_id": vehicle_id,
            "tier": tier,
            "monthly_premium": tier_info["monthly_premium"],
            "coverage_amount": tier_info["coverage"],
            "deductible": tier_info["deductible"],
            "is_active": True,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
        })

        return {
            "insurance": insurance,
            "message": f"Insurance '{tier}' purchased successfully",
        }

    async def get_insurance(self, vehicle_id: UUID) -> CarInsurance | None:
        insurance = await self.car_repo.get_insurance(vehicle_id)
        if insurance and insurance.expires_at:
            if insurance.expires_at < datetime.now(timezone.utc):
                await self.car_repo.update(insurance.id, {"is_active": False})
                return None
        return insurance

    # ── Performance Calculation ───────────────────────────────────────────

    def _compute_effective_stats(self, variant, car) -> dict:
        upgrade_levels = []
        for field in UPGRADE_FIELDS:
            level_field = f"{field}_level"
            level = getattr(car, level_field, 1)
            upgrade_levels.append(level)

        upgrade_avg = sum(upgrade_levels) / len(upgrade_levels)
        stat_multiplier = 1.0 + (upgrade_avg - 1) * UPGRADE_MULTIPLIER_PER_LEVEL

        effective_top_speed = round(variant.top_speed_kmh * stat_multiplier, 2)
        effective_acceleration = round(variant.acceleration_0_100 / stat_multiplier, 2)
        effective_braking = round(variant.braking_distance / stat_multiplier, 2)
        effective_handling = round(variant.handling_rating * stat_multiplier, 2)

        return {
            "top_speed": effective_top_speed,
            "acceleration": effective_acceleration,
            "braking": effective_braking,
            "handling": effective_handling,
            "upgrade_avg": round(upgrade_avg, 2),
            "stat_multiplier": round(stat_multiplier, 4),
        }
