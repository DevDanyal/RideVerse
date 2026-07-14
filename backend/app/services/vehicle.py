"""Business logic for vehicle operations."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.vehicle import VehicleType
from app.repositories.garage import GarageRepository
from app.repositories.player import PlayerRepository
from app.repositories.vehicle import VehicleRepository

logger = logging.getLogger(__name__)


class VehicleService:
    """Orchestrates vehicle purchase, sale, modification, and garage storage."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        vehicle_repo: VehicleRepository,
        garage_repo: GarageRepository,
    ) -> None:
        self._player_repo = player_repo
        self._vehicle_repo = vehicle_repo
        self._garage_repo = garage_repo

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        player = await self._player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def _get_vehicle_or_raise(
        self, vehicle_id: uuid.UUID
    ):
        vehicle = await self._vehicle_repo.get_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundError("Vehicle not found")
        return vehicle

    def _vehicle_to_dict(self, vehicle, bike=None, car=None) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": vehicle.id,
            "player_id": vehicle.player_id,
            "vehicle_type": vehicle.vehicle_type,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "vin": vehicle.vin,
            "license_plate": vehicle.license_plate,
            "purchase_price": vehicle.purchase_price,
            "current_value": vehicle.current_value,
            "fuel_type": vehicle.fuel_type,
            "fuel_level": vehicle.fuel_level,
            "max_fuel": vehicle.max_fuel,
            "health": vehicle.health,
            "engine_health": vehicle.engine_health,
            "body_health": vehicle.body_health,
            "top_speed": vehicle.top_speed,
            "acceleration": vehicle.acceleration,
            "braking": vehicle.braking,
            "handling": vehicle.handling,
            "mileage": vehicle.mileage,
            "garage_id": vehicle.garage_id,
            "created_at": vehicle.created_at,
        }
        if bike is not None:
            data["bike"] = {
                "id": bike.id,
                "vehicle_id": bike.vehicle_id,
                "engine_level": bike.engine_level,
                "turbo_level": bike.turbo_level,
                "exhaust_level": bike.exhaust_level,
                "brake_level": bike.brake_level,
                "wheel_level": bike.wheel_level,
                "tire_level": bike.tire_level,
                "seat_level": bike.seat_level,
                "paint_id": bike.paint_id,
                "decal_id": bike.decal_id,
                "headlight_level": bike.headlight_level,
                "horn_level": bike.horn_level,
                "fuel_tank_level": bike.fuel_tank_level,
                "suspension_level": bike.suspension_level,
                "chain_level": bike.chain_level,
                "mirror_level": bike.mirror_level,
                "speedometer_level": bike.speedometer_level,
            }
        else:
            data["bike"] = None
        if car is not None:
            data["car"] = {
                "id": car.id,
                "vehicle_id": car.vehicle_id,
                "engine_level": car.engine_level,
                "transmission_level": car.transmission_level,
                "brake_level": car.brake_level,
                "suspension_level": car.suspension_level,
                "wheel_level": car.wheel_level,
                "tire_level": car.tire_level,
                "paint_id": car.paint_id,
                "interior_level": car.interior_level,
                "spoiler_level": car.spoiler_level,
                "hood_level": car.hood_level,
                "roof_level": car.roof_level,
                "window_tint": car.window_tint,
                "nitrous_level": car.nitrous_level,
                "headlight_level": car.headlight_level,
            }
        else:
            data["car"] = None
        return data

    async def get_vehicles(self, account_id: uuid.UUID) -> list[dict[str, Any]]:
        player = await self._get_player_or_raise(account_id)
        vehicles = await self._vehicle_repo.get_by_player_id(player.id)
        result = []
        for v in vehicles:
            bike = await self._vehicle_repo.get_bike(v.id)
            car = await self._vehicle_repo.get_car(v.id)
            result.append(self._vehicle_to_dict(v, bike=bike, car=car))
        return result

    async def get_vehicle(
        self, account_id: uuid.UUID, vehicle_id: uuid.UUID
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)
        vehicle = await self._get_vehicle_or_raise(vehicle_id)

        if vehicle.player_id != player.id:
            raise NotFoundError("Vehicle not found")

        bike = await self._vehicle_repo.get_bike(vehicle.id)
        car = await self._vehicle_repo.get_car(vehicle.id)
        return self._vehicle_to_dict(vehicle, bike=bike, car=car)

    async def buy_vehicle(
        self,
        account_id: uuid.UUID,
        vehicle_type: str,
        brand: str,
        model: str,
        year: int,
        vin: str,
        license_plate: str,
        purchase_price: float,
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)

        try:
            v_type = VehicleType(vehicle_type)
        except ValueError:
            raise ValidationError(f"Invalid vehicle type: {vehicle_type}")

        if v_type == VehicleType.BIKE:
            pass
        elif v_type == VehicleType.CAR:
            pass
        else:
            raise ValidationError(f"Invalid vehicle type: {vehicle_type}")

        vehicle = await self._vehicle_repo.create(
            player_id=player.id,
            vehicle_type=v_type,
            brand=brand,
            model=model,
            year=year,
            vin=vin,
            license_plate=license_plate,
            purchase_price=purchase_price,
            current_value=purchase_price,
        )

        if v_type == VehicleType.BIKE:
            from app.models.bike import Bike

            bike = Bike(vehicle_id=vehicle.id)
            self._vehicle_repo._session.add(bike)
            await self._vehicle_repo._session.flush()
        elif v_type == VehicleType.CAR:
            from app.models.car import Car

            car = Car(vehicle_id=vehicle.id)
            self._vehicle_repo._session.add(car)
            await self._vehicle_repo._session.flush()

        logger.info(
            "Player %s purchased %s: %s %s %s",
            player.id,
            vehicle_type,
            brand,
            model,
            year,
        )

        bike = await self._vehicle_repo.get_bike(vehicle.id)
        car = await self._vehicle_repo.get_car(vehicle.id)
        return self._vehicle_to_dict(vehicle, bike=bike, car=car)

    async def sell_vehicle(
        self, account_id: uuid.UUID, vehicle_id: uuid.UUID
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)
        vehicle = await self._get_vehicle_or_raise(vehicle_id)

        if vehicle.player_id != player.id:
            raise NotFoundError("Vehicle not found")

        sold_price = vehicle.current_value
        await self._vehicle_repo.soft_delete(vehicle.id)

        logger.info(
            "Player %s sold vehicle %s for $%.2f",
            player.id,
            vehicle.id,
            sold_price,
        )

        return {"vehicle_id": vehicle.id, "sold_price": sold_price}

    async def update_vehicle(
        self, account_id: uuid.UUID, vehicle_id: uuid.UUID, **kwargs
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)
        vehicle = await self._get_vehicle_or_raise(vehicle_id)

        if vehicle.player_id != player.id:
            raise NotFoundError("Vehicle not found")

        allowed_fields = {
            "brand",
            "model",
            "year",
            "license_plate",
            "fuel_type",
            "fuel_level",
            "health",
            "engine_health",
            "body_health",
            "mileage",
        }
        filtered = {k: v for k, v in kwargs.items() if v is not None and k in allowed_fields}

        if not filtered:
            return self._vehicle_to_dict(vehicle)

        updated = await self._vehicle_repo.update(vehicle.id, **filtered)
        if updated is None:
            raise NotFoundError("Vehicle not found")

        logger.info("Vehicle %s updated", vehicle.id)

        bike = await self._vehicle_repo.get_bike(updated.id)
        car = await self._vehicle_repo.get_car(updated.id)
        return self._vehicle_to_dict(updated, bike=bike, car=car)

    async def store_in_garage(
        self,
        account_id: uuid.UUID,
        vehicle_id: uuid.UUID,
        garage_id: uuid.UUID,
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)
        vehicle = await self._get_vehicle_or_raise(vehicle_id)

        if vehicle.player_id != player.id:
            raise NotFoundError("Vehicle not found")

        garage = await self._garage_repo.get_by_id(garage_id)
        if garage is None:
            raise NotFoundError("Garage not found")
        if garage.player_id != player.id:
            raise NotFoundError("Garage not found")

        slots = await self._garage_repo.get_slots(garage.id)
        occupied_count = sum(1 for s in slots if s.occupied)
        if occupied_count >= garage.capacity:
            raise ConflictError("Garage is at full capacity")

        existing_slot = next(
            (s for s in slots if s.vehicle_id == vehicle.id), None
        )
        if existing_slot is not None:
            raise ValidationError("Vehicle is already stored in this garage")

        from app.models.garage import GarageSlot

        free_slot = next((s for s in slots if not s.occupied), None)
        if free_slot is not None:
            free_slot.vehicle_id = vehicle.id
            free_slot.occupied = True
        else:
            new_slot = GarageSlot(
                garage_id=garage.id,
                slot_number=len(slots) + 1,
                vehicle_id=vehicle.id,
                occupied=True,
            )
            self._vehicle_repo._session.add(new_slot)

        await self._vehicle_repo.update(vehicle.id, garage_id=garage.id)
        await self._vehicle_repo._session.flush()

        logger.info(
            "Vehicle %s stored in garage %s",
            vehicle.id,
            garage.id,
        )

        bike = await self._vehicle_repo.get_bike(vehicle.id)
        car = await self._vehicle_repo.get_car(vehicle.id)
        updated_vehicle = await self._vehicle_repo.get_by_id(vehicle.id)
        return self._vehicle_to_dict(updated_vehicle, bike=bike, car=car)

    async def remove_from_garage(
        self, account_id: uuid.UUID, vehicle_id: uuid.UUID
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)
        vehicle = await self._get_vehicle_or_raise(vehicle_id)

        if vehicle.player_id != player.id:
            raise NotFoundError("Vehicle not found")

        if vehicle.garage_id is None:
            raise ValidationError("Vehicle is not stored in a garage")

        await self._vehicle_repo.update(vehicle.id, garage_id=None)

        logger.info("Vehicle %s removed from garage", vehicle.id)

        bike = await self._vehicle_repo.get_bike(vehicle.id)
        car = await self._vehicle_repo.get_car(vehicle.id)
        updated_vehicle = await self._vehicle_repo.get_by_id(vehicle.id)
        return self._vehicle_to_dict(updated_vehicle, bike=bike, car=car)
