"""Business logic for garage operations."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.repositories.garage import GarageRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)


class GarageService:
    """Orchestrates garage creation and vehicle storage operations."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        garage_repo: GarageRepository,
    ) -> None:
        self._player_repo = player_repo
        self._garage_repo = garage_repo

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        player = await self._player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def _get_garage_or_raise(self, garage_id: uuid.UUID):
        garage = await self._garage_repo.get_by_id(garage_id)
        if garage is None:
            raise NotFoundError("Garage not found")
        return garage

    def _garage_to_dict(self, garage, slots=None) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": garage.id,
            "player_id": garage.player_id,
            "garage_name": garage.garage_name,
            "capacity": garage.capacity,
            "location": garage.location,
            "purchase_price": garage.purchase_price,
            "created_at": garage.created_at,
        }
        if slots is not None:
            data["slots"] = [
                {
                    "id": s.id,
                    "slot_number": s.slot_number,
                    "vehicle_id": s.vehicle_id,
                    "occupied": s.occupied,
                }
                for s in slots
            ]
        return data

    async def get_garages(self, account_id: uuid.UUID) -> list[dict[str, Any]]:
        player = await self._get_player_or_raise(account_id)
        garages = await self._garage_repo.get_by_player_id(player.id)
        result = []
        for g in garages:
            slots = await self._garage_repo.get_slots(g.id)
            result.append(self._garage_to_dict(g, slots=slots))
        return result

    async def get_garage(
        self, account_id: uuid.UUID, garage_id: uuid.UUID
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)
        garage = await self._get_garage_or_raise(garage_id)

        if garage.player_id != player.id:
            raise NotFoundError("Garage not found")

        slots = await self._garage_repo.get_slots(garage.id)
        return self._garage_to_dict(garage, slots=slots)

    async def create_garage(
        self,
        account_id: uuid.UUID,
        garage_name: str,
        location: str,
        purchase_price: float,
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)

        if not garage_name or len(garage_name) < 2 or len(garage_name) > 100:
            raise ValidationError(
                "Garage name must be between 2 and 100 characters"
            )

        garage = await self._garage_repo.create(
            player_id=player.id,
            garage_name=garage_name,
            location=location,
            purchase_price=purchase_price,
        )

        logger.info(
            "Player %s created garage '%s'",
            player.id,
            garage_name,
        )

        return self._garage_to_dict(garage)

    async def store_vehicle(
        self,
        account_id: uuid.UUID,
        garage_id: uuid.UUID,
        vehicle_id: uuid.UUID,
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)
        garage = await self._get_garage_or_raise(garage_id)

        if garage.player_id != player.id:
            raise NotFoundError("Garage not found")

        from app.repositories.vehicle import VehicleRepository

        vehicle_repo = VehicleRepository(self._garage_repo._session)
        vehicle = await vehicle_repo.get_by_id(vehicle_id)

        if vehicle is None:
            raise NotFoundError("Vehicle not found")
        if vehicle.player_id != player.id:
            raise NotFoundError("Vehicle not found")

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
            self._garage_repo._session.add(new_slot)

        await vehicle_repo.update(vehicle.id, garage_id=garage.id)
        await self._garage_repo._session.flush()

        logger.info(
            "Vehicle %s stored in garage %s",
            vehicle.id,
            garage.id,
        )

        updated_garage = await self._garage_repo.get_by_id(garage.id)
        updated_slots = await self._garage_repo.get_slots(garage.id)
        return self._garage_to_dict(updated_garage, slots=updated_slots)

    async def retrieve_vehicle(
        self,
        account_id: uuid.UUID,
        garage_id: uuid.UUID,
        vehicle_id: uuid.UUID,
    ) -> dict[str, Any]:
        player = await self._get_player_or_raise(account_id)
        garage = await self._get_garage_or_raise(garage_id)

        if garage.player_id != player.id:
            raise NotFoundError("Garage not found")

        from app.repositories.vehicle import VehicleRepository

        vehicle_repo = VehicleRepository(self._garage_repo._session)
        vehicle = await vehicle_repo.get_by_id(vehicle_id)

        if vehicle is None:
            raise NotFoundError("Vehicle not found")
        if vehicle.player_id != player.id:
            raise NotFoundError("Vehicle not found")

        slots = await self._garage_repo.get_slots(garage.id)
        slot = next((s for s in slots if s.vehicle_id == vehicle.id), None)
        if slot is None:
            raise ValidationError("Vehicle is not stored in this garage")

        slot.vehicle_id = None
        slot.occupied = False

        await vehicle_repo.update(vehicle.id, garage_id=None)
        await self._garage_repo._session.flush()

        logger.info(
            "Vehicle %s retrieved from garage %s",
            vehicle.id,
            garage.id,
        )

        updated_vehicle = await vehicle_repo.get_by_id(vehicle.id)
        bike = await vehicle_repo.get_bike(vehicle.id)
        car = await vehicle_repo.get_car(vehicle.id)

        vehicle_data = {
            "id": updated_vehicle.id,
            "player_id": updated_vehicle.player_id,
            "vehicle_type": updated_vehicle.vehicle_type,
            "brand": updated_vehicle.brand,
            "model": updated_vehicle.model,
            "year": updated_vehicle.year,
            "vin": updated_vehicle.vin,
            "license_plate": updated_vehicle.license_plate,
            "purchase_price": updated_vehicle.purchase_price,
            "current_value": updated_vehicle.current_value,
            "fuel_type": updated_vehicle.fuel_type,
            "fuel_level": updated_vehicle.fuel_level,
            "max_fuel": updated_vehicle.max_fuel,
            "health": updated_vehicle.health,
            "engine_health": updated_vehicle.engine_health,
            "body_health": updated_vehicle.body_health,
            "top_speed": updated_vehicle.top_speed,
            "acceleration": updated_vehicle.acceleration,
            "braking": updated_vehicle.braking,
            "handling": updated_vehicle.handling,
            "mileage": updated_vehicle.mileage,
            "garage_id": updated_vehicle.garage_id,
            "created_at": updated_vehicle.created_at,
        }
        if bike is not None:
            vehicle_data["bike"] = {
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
        if car is not None:
            vehicle_data["car"] = {
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

        updated_garage = await self._garage_repo.get_by_id(garage.id)
        updated_slots = await self._garage_repo.get_slots(garage.id)
        return {
            "vehicle": vehicle_data,
            "garage": self._garage_to_dict(updated_garage, slots=updated_slots),
        }
