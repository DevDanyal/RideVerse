"""Business logic for the Traffic system."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.traffic import (
    DespawnRuleType,
    EmergencyVehicleType,
    SpawnRuleType,
    TrafficDensityLevel,
    TrafficEventType,
    TrafficSignalState,
    TrafficVehicleType,
    TrafficViolationType,
    TrafficZoneType,
    TrafficRouteType,
)
from app.repositories.traffic import TrafficRepository

logger = logging.getLogger(__name__)

VALID_ZONE_TYPES = {v.value for v in TrafficZoneType.__members__.values()}
VALID_ROUTE_TYPES = {v.value for v in TrafficRouteType.__members__.values()}
VALID_SIGNAL_STATES = {v.value for v in TrafficSignalState.__members__.values()}
VALID_DENSITY_LEVELS = {v.value for v in TrafficDensityLevel.__members__.values()}
VALID_VEHICLE_TYPES = {v.value for v in TrafficVehicleType.__members__.values()}
VALID_SPAWN_RULE_TYPES = {v.value for v in SpawnRuleType.__members__.values()}
VALID_DESPAWN_RULE_TYPES = {v.value for v in DespawnRuleType.__members__.values()}
VALID_EMERGENCY_TYPES = {v.value for v in EmergencyVehicleType.__members__.values()}
VALID_VIOLATION_TYPES = {v.value for v in TrafficViolationType.__members__.values()}
VALID_EVENT_TYPES = {v.value for v in TrafficEventType.__members__.values()}

# Fine amounts by violation type
VIOLATION_FINE_AMOUNTS: dict[str, float] = {
    TrafficViolationType.SPEEDING.value: 500.0,
    TrafficViolationType.RUNNING_RED_LIGHT.value: 1000.0,
    TrafficViolationType.WRONG_LANE.value: 750.0,
    TrafficViolationType.ILLEGAL_U_TURN.value: 600.0,
    TrafficViolationType.ILLEGAL_PARKING.value: 300.0,
    TrafficViolationType.RECKLESS_DRIVING.value: 2000.0,
    TrafficViolationType.HIT_AND_RUN.value: 5000.0,
}


class TrafficService:
    """Business logic for Traffic zones, routes, lanes, signals, vehicles, density, violations, events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.traffic_repo = TrafficRepository(session)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _validate_zone_type(self, zone_type: str) -> None:
        if zone_type not in VALID_ZONE_TYPES:
            raise ValidationError(f"Invalid zone type: {zone_type}. Valid: {sorted(VALID_ZONE_TYPES)}")

    def _validate_route_type(self, route_type: str) -> None:
        if route_type not in VALID_ROUTE_TYPES:
            raise ValidationError(f"Invalid route type: {route_type}. Valid: {sorted(VALID_ROUTE_TYPES)}")

    def _validate_signal_state(self, state: str) -> None:
        if state not in VALID_SIGNAL_STATES:
            raise ValidationError(f"Invalid signal state: {state}. Valid: {sorted(VALID_SIGNAL_STATES)}")

    def _validate_density_level(self, level: str) -> None:
        if level not in VALID_DENSITY_LEVELS:
            raise ValidationError(f"Invalid density level: {level}. Valid: {sorted(VALID_DENSITY_LEVELS)}")

    def _validate_vehicle_type(self, vehicle_type: str) -> None:
        if vehicle_type not in VALID_VEHICLE_TYPES:
            raise ValidationError(f"Invalid vehicle type: {vehicle_type}. Valid: {sorted(VALID_VEHICLE_TYPES)}")

    def _validate_spawn_rule_type(self, rule_type: str) -> None:
        if rule_type not in VALID_SPAWN_RULE_TYPES:
            raise ValidationError(f"Invalid spawn rule type: {rule_type}. Valid: {sorted(VALID_SPAWN_RULE_TYPES)}")

    def _validate_despawn_rule_type(self, rule_type: str) -> None:
        if rule_type not in VALID_DESPAWN_RULE_TYPES:
            raise ValidationError(f"Invalid despawn rule type: {rule_type}. Valid: {sorted(VALID_DESPAWN_RULE_TYPES)}")

    def _validate_emergency_type(self, emergency_type: str) -> None:
        if emergency_type not in VALID_EMERGENCY_TYPES:
            raise ValidationError(f"Invalid emergency type: {emergency_type}. Valid: {sorted(VALID_EMERGENCY_TYPES)}")

    def _validate_violation_type(self, violation_type: str) -> None:
        if violation_type not in VALID_VIOLATION_TYPES:
            raise ValidationError(f"Invalid violation type: {violation_type}. Valid: {sorted(VALID_VIOLATION_TYPES)}")

    def _validate_event_type(self, event_type: str) -> None:
        if event_type not in VALID_EVENT_TYPES:
            raise ValidationError(f"Invalid event type: {event_type}. Valid: {sorted(VALID_EVENT_TYPES)}")

    # ── Zone CRUD ────────────────────────────────────────────────────────

    async def create_zone(self, data: dict) -> TrafficZone:
        if "zone_type" in data and data["zone_type"]:
            self._validate_zone_type(data["zone_type"])
        zone = await self.traffic_repo.create_zone(data)
        logger.info("Traffic zone '%s' created (type: %s)", zone.zone_name, zone.zone_type)
        return zone

    async def get_zone(self, zone_id: uuid.UUID) -> TrafficZone:
        zone = await self.traffic_repo.get_zone_by_id(zone_id)
        if not zone:
            raise NotFoundError("Traffic zone not found")
        return zone

    async def list_zones(
        self, zone_type: str | None = None, skip: int = 0, limit: int = 50
    ) -> tuple[list[TrafficZone], int]:
        if zone_type:
            self._validate_zone_type(zone_type)
        zones = await self.traffic_repo.get_all_zones(zone_type, skip, limit)
        total = await self.traffic_repo.count_zones(zone_type)
        return zones, total

    async def update_zone(self, zone_id: uuid.UUID, data: dict) -> TrafficZone:
        await self.get_zone(zone_id)
        if "zone_type" in data and data["zone_type"]:
            self._validate_zone_type(data["zone_type"])
        await self.traffic_repo.update_zone(zone_id, data)
        return await self.traffic_repo.get_zone_by_id(zone_id)

    async def delete_zone(self, zone_id: uuid.UUID) -> bool:
        await self.get_zone(zone_id)
        return await self.traffic_repo.soft_delete_zone(zone_id)

    # ── Route CRUD ───────────────────────────────────────────────────────

    async def create_route(self, data: dict) -> TrafficRoute:
        if "route_type" in data and data["route_type"]:
            self._validate_route_type(data["route_type"])
        if "zone_id" in data and data["zone_id"]:
            zone = await self.traffic_repo.get_zone_by_id(data["zone_id"])
            if not zone:
                raise NotFoundError("Traffic zone not found")
        route = await self.traffic_repo.create_route(data)
        logger.info("Traffic route '%s' created (type: %s)", route.route_name, route.route_type)
        return route

    async def get_route(self, route_id: uuid.UUID) -> TrafficRoute:
        route = await self.traffic_repo.get_route_by_id(route_id)
        if not route:
            raise NotFoundError("Traffic route not found")
        return route

    async def list_routes(
        self, route_type: str | None = None, zone_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[TrafficRoute], int]:
        if route_type:
            self._validate_route_type(route_type)
        routes = await self.traffic_repo.get_all_routes(route_type, zone_id, skip, limit)
        total = await self.traffic_repo.count_routes(route_type, zone_id)
        return routes, total

    async def update_route(self, route_id: uuid.UUID, data: dict) -> TrafficRoute:
        await self.get_route(route_id)
        if "route_type" in data and data["route_type"]:
            self._validate_route_type(data["route_type"])
        await self.traffic_repo.update_route(route_id, data)
        return await self.traffic_repo.get_route_by_id(route_id)

    async def delete_route(self, route_id: uuid.UUID) -> bool:
        await self.get_route(route_id)
        return await self.traffic_repo.soft_delete_route(route_id)

    # ── Lane CRUD ────────────────────────────────────────────────────────

    async def create_lane(self, data: dict) -> TrafficLane:
        route = await self.traffic_repo.get_route_by_id(data["route_id"])
        if not route:
            raise NotFoundError("Traffic route not found")
        lane = await self.traffic_repo.create_lane(data)
        logger.info("Lane %d created on route %s", lane.lane_number, data["route_id"])
        return lane

    async def get_lane(self, lane_id: uuid.UUID) -> TrafficLane:
        lane = await self.traffic_repo.get_lane_by_id(lane_id)
        if not lane:
            raise NotFoundError("Traffic lane not found")
        return lane

    async def list_lanes_for_route(
        self, route_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[TrafficLane], int]:
        lanes = await self.traffic_repo.get_lanes_for_route(route_id, skip, limit)
        total = await self.traffic_repo.count_lanes(route_id=route_id)
        return lanes, total

    async def update_lane(self, lane_id: uuid.UUID, data: dict) -> TrafficLane:
        await self.get_lane(lane_id)
        await self.traffic_repo.update_lane(lane_id, data)
        return await self.traffic_repo.get_lane_by_id(lane_id)

    async def delete_lane(self, lane_id: uuid.UUID) -> bool:
        await self.get_lane(lane_id)
        return await self.traffic_repo.soft_delete_lane(lane_id)

    # ── Signal CRUD ──────────────────────────────────────────────────────

    async def create_signal(self, data: dict) -> TrafficSignal:
        if "state" in data and data["state"]:
            self._validate_signal_state(data["state"])
        signal = await self.traffic_repo.create_signal(data)
        logger.info("Traffic signal '%s' created", signal.signal_name)
        return signal

    async def get_signal(self, signal_id: uuid.UUID) -> TrafficSignal:
        signal = await self.traffic_repo.get_signal_by_id(signal_id)
        if not signal:
            raise NotFoundError("Traffic signal not found")
        return signal

    async def list_signals(
        self, state: str | None = None, route_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[TrafficSignal], int]:
        if state:
            self._validate_signal_state(state)
        signals = await self.traffic_repo.get_all_signals(state, route_id, skip, limit)
        total = await self.traffic_repo.count_signals(state)
        return signals, total

    async def update_signal(self, signal_id: uuid.UUID, data: dict) -> TrafficSignal:
        await self.get_signal(signal_id)
        if "state" in data and data["state"]:
            self._validate_signal_state(data["state"])
        await self.traffic_repo.update_signal(signal_id, data)
        return await self.traffic_repo.get_signal_by_id(signal_id)

    async def change_signal_state(self, signal_id: uuid.UUID, state: str) -> TrafficSignal:
        self._validate_signal_state(state)
        return await self.update_signal(signal_id, {"state": state})

    async def activate_emergency_override(self, signal_id: uuid.UUID) -> TrafficSignal:
        await self.get_signal(signal_id)
        await self.traffic_repo.update_signal(signal_id, {
            "state": "emergency_override",
            "is_emergency_override": True,
        })
        return await self.traffic_repo.get_signal_by_id(signal_id)

    async def deactivate_emergency_override(self, signal_id: uuid.UUID) -> TrafficSignal:
        await self.get_signal(signal_id)
        await self.traffic_repo.update_signal(signal_id, {
            "state": "green",
            "is_emergency_override": False,
        })
        return await self.traffic_repo.get_signal_by_id(signal_id)

    async def delete_signal(self, signal_id: uuid.UUID) -> bool:
        await self.get_signal(signal_id)
        return await self.traffic_repo.soft_delete_signal(signal_id)

    # ── Spawn Point CRUD ─────────────────────────────────────────────────

    async def create_spawn_point(self, data: dict) -> TrafficSpawnPoint:
        sp = await self.traffic_repo.create_spawn_point(data)
        logger.info("Spawn point '%s' created", sp.spawn_name)
        return sp

    async def get_spawn_point(self, sp_id: uuid.UUID) -> TrafficSpawnPoint:
        sp = await self.traffic_repo.get_spawn_point_by_id(sp_id)
        if not sp:
            raise NotFoundError("Traffic spawn point not found")
        return sp

    async def list_spawn_points(
        self, spawn_type: str | None = None, zone_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[TrafficSpawnPoint], int]:
        sps = await self.traffic_repo.get_all_spawn_points(spawn_type, zone_id, skip, limit)
        total = await self.traffic_repo.count_spawn_points(spawn_type)
        return sps, total

    async def update_spawn_point(self, sp_id: uuid.UUID, data: dict) -> TrafficSpawnPoint:
        await self.get_spawn_point(sp_id)
        await self.traffic_repo.update_spawn_point(sp_id, data)
        return await self.traffic_repo.get_spawn_point_by_id(sp_id)

    async def delete_spawn_point(self, sp_id: uuid.UUID) -> bool:
        await self.get_spawn_point(sp_id)
        return await self.traffic_repo.soft_delete_spawn_point(sp_id)

    # ── Density CRUD ─────────────────────────────────────────────────────

    async def create_density(self, data: dict) -> TrafficDensity:
        if "density_level" in data and data["density_level"]:
            self._validate_density_level(data["density_level"])
        density = await self.traffic_repo.create_density(data)
        logger.info("Density config '%s' created", density.density_level)
        return density

    async def get_density(self, density_id: uuid.UUID) -> TrafficDensity:
        density = await self.traffic_repo.get_density_by_id(density_id)
        if not density:
            raise NotFoundError("Traffic density config not found")
        return density

    async def list_densities(
        self, density_level: str | None = None, zone_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[TrafficDensity], int]:
        densities = await self.traffic_repo.get_all_densities(density_level, zone_id, skip, limit)
        total = await self.traffic_repo.count_densities(zone_id)
        return densities, total

    async def update_density(self, density_id: uuid.UUID, data: dict) -> TrafficDensity:
        await self.get_density(density_id)
        if "density_level" in data and data["density_level"]:
            self._validate_density_level(data["density_level"])
        await self.traffic_repo.update_density(density_id, data)
        return await self.traffic_repo.get_density_by_id(density_id)

    # ── Spawn Rule CRUD ──────────────────────────────────────────────────

    async def create_spawn_rule(self, data: dict) -> TrafficSpawnRule:
        if "rule_type" in data and data["rule_type"]:
            self._validate_spawn_rule_type(data["rule_type"])
        if "vehicle_type" in data and data["vehicle_type"]:
            self._validate_vehicle_type(data["vehicle_type"])
        rule = await self.traffic_repo.create_spawn_rule(data)
        logger.info("Spawn rule '%s' created (type: %s)", rule.rule_name, rule.rule_type)
        return rule

    async def get_spawn_rule(self, rule_id: uuid.UUID) -> TrafficSpawnRule:
        rule = await self.traffic_repo.get_spawn_rule_by_id(rule_id)
        if not rule:
            raise NotFoundError("Traffic spawn rule not found")
        return rule

    async def list_spawn_rules(
        self, rule_type: str | None = None, skip: int = 0, limit: int = 50
    ) -> tuple[list[TrafficSpawnRule], int]:
        rules = await self.traffic_repo.get_all_spawn_rules(rule_type, skip, limit)
        total = await self.traffic_repo.count_spawn_rules()
        return rules, total

    async def update_spawn_rule(self, rule_id: uuid.UUID, data: dict) -> TrafficSpawnRule:
        await self.get_spawn_rule(rule_id)
        if "rule_type" in data and data["rule_type"]:
            self._validate_spawn_rule_type(data["rule_type"])
        if "vehicle_type" in data and data["vehicle_type"]:
            self._validate_vehicle_type(data["vehicle_type"])
        await self.traffic_repo.update_spawn_rule(rule_id, data)
        return await self.traffic_repo.get_spawn_rule_by_id(rule_id)

    async def delete_spawn_rule(self, rule_id: uuid.UUID) -> bool:
        await self.get_spawn_rule(rule_id)
        return await self.traffic_repo.soft_delete_spawn_rule(rule_id)

    # ── Despawn Rule CRUD ────────────────────────────────────────────────

    async def create_despawn_rule(self, data: dict) -> TrafficDespawnRule:
        if "rule_type" in data and data["rule_type"]:
            self._validate_despawn_rule_type(data["rule_type"])
        rule = await self.traffic_repo.create_despawn_rule(data)
        logger.info("Despawn rule '%s' created (type: %s)", rule.rule_name, rule.rule_type)
        return rule

    async def get_despawn_rule(self, rule_id: uuid.UUID) -> TrafficDespawnRule:
        rule = await self.traffic_repo.get_despawn_rule_by_id(rule_id)
        if not rule:
            raise NotFoundError("Traffic despawn rule not found")
        return rule

    async def list_despawn_rules(
        self, rule_type: str | None = None, skip: int = 0, limit: int = 50
    ) -> tuple[list[TrafficDespawnRule], int]:
        rules = await self.traffic_repo.get_all_despawn_rules(rule_type, skip, limit)
        total = await self.traffic_repo.count_despawn_rules()
        return rules, total

    async def update_despawn_rule(self, rule_id: uuid.UUID, data: dict) -> TrafficDespawnRule:
        await self.get_despawn_rule(rule_id)
        if "rule_type" in data and data["rule_type"]:
            self._validate_despawn_rule_type(data["rule_type"])
        await self.traffic_repo.update_despawn_rule(rule_id, data)
        return await self.traffic_repo.get_despawn_rule_by_id(rule_id)

    async def delete_despawn_rule(self, rule_id: uuid.UUID) -> bool:
        await self.get_despawn_rule(rule_id)
        return await self.traffic_repo.soft_delete_despawn_rule(rule_id)

    # ── Vehicle CRUD ─────────────────────────────────────────────────────

    async def spawn_vehicle(self, data: dict) -> TrafficVehicle:
        if "vehicle_type" in data and data["vehicle_type"]:
            self._validate_vehicle_type(data["vehicle_type"])
        data["spawned_at"] = datetime.now(timezone.utc).isoformat()
        vehicle = await self.traffic_repo.create_vehicle(data)
        logger.info("Traffic vehicle '%s' spawned (type: %s)", vehicle.model_name, vehicle.vehicle_type)
        return vehicle

    async def get_vehicle(self, vehicle_id: uuid.UUID) -> TrafficVehicle:
        vehicle = await self.traffic_repo.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError("Traffic vehicle not found")
        return vehicle

    async def list_vehicles(
        self, vehicle_type: str | None = None, zone_id: uuid.UUID | None = None,
        active_only: bool = False, emergency_only: bool = False,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[TrafficVehicle], int]:
        if vehicle_type:
            self._validate_vehicle_type(vehicle_type)
        vehicles = await self.traffic_repo.get_all_vehicles(
            vehicle_type, zone_id, active_only, emergency_only, skip, limit
        )
        total = await self.traffic_repo.count_vehicles(vehicle_type, zone_id, active_only, emergency_only)
        return vehicles, total

    async def update_vehicle(self, vehicle_id: uuid.UUID, data: dict) -> TrafficVehicle:
        await self.get_vehicle(vehicle_id)
        if "vehicle_type" in data and data["vehicle_type"]:
            self._validate_vehicle_type(data["vehicle_type"])
        await self.traffic_repo.update_vehicle(vehicle_id, data)
        return await self.traffic_repo.get_vehicle_by_id(vehicle_id)

    async def despawn_vehicle(self, vehicle_id: uuid.UUID) -> bool:
        await self.get_vehicle(vehicle_id)
        return await self.traffic_repo.soft_delete_vehicle(vehicle_id)

    # ── Emergency Vehicle CRUD ───────────────────────────────────────────

    async def register_emergency_vehicle(self, data: dict) -> TrafficEmergencyVehicle:
        if "emergency_type" in data and data["emergency_type"]:
            self._validate_emergency_type(data["emergency_type"])
        vehicle = await self.traffic_repo.get_vehicle_by_id(data["vehicle_id"])
        if not vehicle:
            raise NotFoundError("Traffic vehicle not found")
        existing = await self.traffic_repo.get_emergency_by_vehicle_id(data["vehicle_id"])
        if existing:
            raise ConflictError("Vehicle is already registered as an emergency vehicle")
        ev = await self.traffic_repo.create_emergency_vehicle(data)
        await self.traffic_repo.update_vehicle(data["vehicle_id"], {"is_emergency": True})
        logger.info("Emergency vehicle registered: %s (type: %s)", data["vehicle_id"], data["emergency_type"])
        return ev

    async def get_emergency_vehicle(self, ev_id: uuid.UUID) -> TrafficEmergencyVehicle:
        ev = await self.traffic_repo.get_emergency_by_id(ev_id)
        if not ev:
            raise NotFoundError("Emergency vehicle record not found")
        return ev

    async def list_emergency_vehicles(
        self, emergency_type: str | None = None, active_only: bool = False,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[TrafficEmergencyVehicle], int]:
        if emergency_type:
            self._validate_emergency_type(emergency_type)
        evs = await self.traffic_repo.get_all_emergency_vehicles(emergency_type, active_only, skip, limit)
        total = await self.traffic_repo.count_emergency_vehicles(emergency_type)
        return evs, total

    async def update_emergency_vehicle(self, ev_id: uuid.UUID, data: dict) -> TrafficEmergencyVehicle:
        await self.get_emergency_vehicle(ev_id)
        if "emergency_type" in data and data["emergency_type"]:
            self._validate_emergency_type(data["emergency_type"])
        await self.traffic_repo.update_emergency_vehicle(ev_id, data)
        return await self.traffic_repo.get_emergency_by_id(ev_id)

    async def activate_siren(self, ev_id: uuid.UUID) -> TrafficEmergencyVehicle:
        return await self.update_emergency_vehicle(ev_id, {"siren_on": True, "is_active_call": True})

    async def deactivate_siren(self, ev_id: uuid.UUID) -> TrafficEmergencyVehicle:
        return await self.update_emergency_vehicle(ev_id, {"siren_on": False, "is_active_call": False})

    # ── Statistics CRUD ──────────────────────────────────────────────────

    async def create_statistics(self, data: dict) -> TrafficStatistics:
        stats = await self.traffic_repo.create_statistics(data)
        logger.info("Traffic statistics created for date %s", data.get("date_recorded"))
        return stats

    async def get_statistics(self, stats_id: uuid.UUID) -> TrafficStatistics:
        stats = await self.traffic_repo.get_statistics_by_id(stats_id)
        if not stats:
            raise NotFoundError("Traffic statistics record not found")
        return stats

    async def list_statistics_for_zone(
        self, zone_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[TrafficStatistics], int]:
        stats = await self.traffic_repo.get_statistics_for_zone(zone_id, skip, limit)
        total = await self.traffic_repo.count_statistics(zone_id=zone_id)
        return stats, total

    async def list_statistics_by_date(
        self, date_recorded: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[TrafficStatistics], int]:
        stats = await self.traffic_repo.get_statistics_by_date(date_recorded, skip, limit)
        total = len(stats)
        return stats, total

    async def update_statistics(self, stats_id: uuid.UUID, data: dict) -> TrafficStatistics:
        await self.get_statistics(stats_id)
        await self.traffic_repo.update_statistics(stats_id, data)
        return await self.traffic_repo.get_statistics_by_id(stats_id)

    # ── Speed Limit CRUD ─────────────────────────────────────────────────

    async def create_speed_limit(self, data: dict) -> TrafficSpeedLimit:
        sl = await self.traffic_repo.create_speed_limit(data)
        logger.info("Speed limit %.0f km/h set for road '%s'", sl.speed_limit_kmh, sl.road_name)
        return sl

    async def get_speed_limit(self, sl_id: uuid.UUID) -> TrafficSpeedLimit:
        sl = await self.traffic_repo.get_speed_limit_by_id(sl_id)
        if not sl:
            raise NotFoundError("Speed limit not found")
        return sl

    async def list_speed_limits(
        self, zone_id: uuid.UUID | None = None, skip: int = 0, limit: int = 50
    ) -> tuple[list[TrafficSpeedLimit], int]:
        limits = await self.traffic_repo.get_all_speed_limits(zone_id, skip, limit)
        total = await self.traffic_repo.count_speed_limits(zone_id)
        return limits, total

    async def update_speed_limit(self, sl_id: uuid.UUID, data: dict) -> TrafficSpeedLimit:
        await self.get_speed_limit(sl_id)
        await self.traffic_repo.update_speed_limit(sl_id, data)
        return await self.traffic_repo.get_speed_limit_by_id(sl_id)

    async def delete_speed_limit(self, sl_id: uuid.UUID) -> bool:
        await self.get_speed_limit(sl_id)
        return await self.traffic_repo.soft_delete_speed_limit(sl_id)

    # ── Violation CRUD ───────────────────────────────────────────────────

    async def create_violation(self, data: dict) -> TrafficViolation:
        if "violation_type" in data and data["violation_type"]:
            self._validate_violation_type(data["violation_type"])
        if "fine_amount" not in data or data.get("fine_amount", 0) == 0:
            v_type = data.get("violation_type", "")
            data["fine_amount"] = VIOLATION_FINE_AMOUNTS.get(v_type, 500.0)
        violation = await self.traffic_repo.create_violation(data)
        logger.info("Violation '%s' recorded (fine: $%.2f)", violation.violation_type, violation.fine_amount)
        return violation

    async def get_violation(self, v_id: uuid.UUID) -> TrafficViolation:
        violation = await self.traffic_repo.get_violation_by_id(v_id)
        if not violation:
            raise NotFoundError("Traffic violation not found")
        return violation

    async def list_violations(
        self, violation_type: str | None = None, player_id: uuid.UUID | None = None,
        resolved: bool | None = None, skip: int = 0, limit: int = 50,
    ) -> tuple[list[TrafficViolation], int]:
        if violation_type:
            self._validate_violation_type(violation_type)
        violations = await self.traffic_repo.get_all_violations(violation_type, player_id, resolved, skip, limit)
        total = await self.traffic_repo.count_violations(violation_type, player_id)
        return violations, total

    async def resolve_violation(self, v_id: uuid.UUID) -> TrafficViolation:
        await self.get_violation(v_id)
        await self.traffic_repo.update_violation(v_id, {"is_resolved": True})
        return await self.traffic_repo.get_violation_by_id(v_id)

    # ── Event CRUD ───────────────────────────────────────────────────────

    async def create_event(self, data: dict) -> TrafficEvent:
        if "event_type" in data and data["event_type"]:
            self._validate_event_type(data["event_type"])
        event = await self.traffic_repo.create_event(data)
        logger.info("Traffic event '%s' reported", event.event_type)
        return event

    async def get_event(self, event_id: uuid.UUID) -> TrafficEvent:
        event = await self.traffic_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundError("Traffic event not found")
        return event

    async def list_events(
        self, event_type: str | None = None, resolved: bool | None = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[TrafficEvent], int]:
        if event_type:
            self._validate_event_type(event_type)
        events = await self.traffic_repo.get_all_events(event_type, resolved, skip, limit)
        total = await self.traffic_repo.count_events(event_type, resolved)
        return events, total

    async def resolve_event(self, event_id: uuid.UUID) -> TrafficEvent:
        await self.get_event(event_id)
        await self.traffic_repo.update_event(event_id, {"is_resolved": True})
        return await self.traffic_repo.get_event_by_id(event_id)

    async def update_event(self, event_id: uuid.UUID, data: dict) -> TrafficEvent:
        await self.get_event(event_id)
        if "event_type" in data and data["event_type"]:
            self._validate_event_type(data["event_type"])
        await self.traffic_repo.update_event(event_id, data)
        return await self.traffic_repo.get_event_by_id(event_id)
