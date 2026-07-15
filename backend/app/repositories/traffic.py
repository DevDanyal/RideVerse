"""Repository layer for Traffic-related database operations."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.traffic import (
    TrafficDensity,
    TrafficDespawnRule,
    TrafficEmergencyVehicle,
    TrafficEvent,
    TrafficLane,
    TrafficRoute,
    TrafficSignal,
    TrafficSpawnPoint,
    TrafficSpawnRule,
    TrafficSpeedLimit,
    TrafficStatistics,
    TrafficVehicle,
    TrafficViolation,
    TrafficZone,
)


class TrafficRepository:
    """Data-access layer for all Traffic-related models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Traffic Zone ─────────────────────────────────────────────────────

    async def get_zone_by_id(self, zone_id: uuid.UUID) -> TrafficZone | None:
        stmt = select(TrafficZone).where(
            TrafficZone.id == zone_id, TrafficZone.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_zones(
        self, zone_type: str | None = None, skip: int = 0, limit: int = 50
    ) -> list[TrafficZone]:
        stmt = select(TrafficZone).where(TrafficZone.is_deleted.is_(False))
        if zone_type:
            stmt = stmt.where(TrafficZone.zone_type == zone_type)
        stmt = stmt.order_by(TrafficZone.zone_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_zones(self, zone_type: str | None = None) -> int:
        stmt = select(func.count(TrafficZone.id)).where(TrafficZone.is_deleted.is_(False))
        if zone_type:
            stmt = stmt.where(TrafficZone.zone_type == zone_type)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_zone(self, data: dict) -> TrafficZone:
        zone = TrafficZone(**data)
        self._session.add(zone)
        await self._session.flush()
        return zone

    async def update_zone(self, zone_id: uuid.UUID, data: dict) -> TrafficZone | None:
        stmt = (
            update(TrafficZone)
            .where(TrafficZone.id == zone_id, TrafficZone.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficZone)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_zone(self, zone_id: uuid.UUID) -> bool:
        stmt = update(TrafficZone).where(
            TrafficZone.id == zone_id, TrafficZone.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Route ────────────────────────────────────────────────────

    async def get_route_by_id(self, route_id: uuid.UUID) -> TrafficRoute | None:
        stmt = (
            select(TrafficRoute)
            .options(selectinload(TrafficRoute.lanes))
            .where(TrafficRoute.id == route_id, TrafficRoute.is_deleted.is_(False))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_routes(
        self, route_type: str | None = None, zone_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> list[TrafficRoute]:
        stmt = select(TrafficRoute).where(TrafficRoute.is_deleted.is_(False))
        if route_type:
            stmt = stmt.where(TrafficRoute.route_type == route_type)
        if zone_id:
            stmt = stmt.where(TrafficRoute.zone_id == zone_id)
        stmt = stmt.order_by(TrafficRoute.route_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_routes(self, route_type: str | None = None, zone_id: uuid.UUID | None = None) -> int:
        stmt = select(func.count(TrafficRoute.id)).where(TrafficRoute.is_deleted.is_(False))
        if route_type:
            stmt = stmt.where(TrafficRoute.route_type == route_type)
        if zone_id:
            stmt = stmt.where(TrafficRoute.zone_id == zone_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_route(self, data: dict) -> TrafficRoute:
        route = TrafficRoute(**data)
        self._session.add(route)
        await self._session.flush()
        return route

    async def update_route(self, route_id: uuid.UUID, data: dict) -> TrafficRoute | None:
        stmt = (
            update(TrafficRoute)
            .where(TrafficRoute.id == route_id, TrafficRoute.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficRoute)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_route(self, route_id: uuid.UUID) -> bool:
        stmt = update(TrafficRoute).where(
            TrafficRoute.id == route_id, TrafficRoute.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Lane ─────────────────────────────────────────────────────

    async def get_lane_by_id(self, lane_id: uuid.UUID) -> TrafficLane | None:
        stmt = select(TrafficLane).where(
            TrafficLane.id == lane_id, TrafficLane.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_lanes_for_route(
        self, route_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[TrafficLane]:
        stmt = (
            select(TrafficLane)
            .where(TrafficLane.route_id == route_id, TrafficLane.is_deleted.is_(False))
            .order_by(TrafficLane.lane_number)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_lanes(self, route_id: uuid.UUID | None = None) -> int:
        stmt = select(func.count(TrafficLane.id)).where(TrafficLane.is_deleted.is_(False))
        if route_id:
            stmt = stmt.where(TrafficLane.route_id == route_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_lane(self, data: dict) -> TrafficLane:
        lane = TrafficLane(**data)
        self._session.add(lane)
        await self._session.flush()
        return lane

    async def update_lane(self, lane_id: uuid.UUID, data: dict) -> TrafficLane | None:
        stmt = (
            update(TrafficLane)
            .where(TrafficLane.id == lane_id, TrafficLane.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficLane)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_lane(self, lane_id: uuid.UUID) -> bool:
        stmt = update(TrafficLane).where(
            TrafficLane.id == lane_id, TrafficLane.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Signal ───────────────────────────────────────────────────

    async def get_signal_by_id(self, signal_id: uuid.UUID) -> TrafficSignal | None:
        stmt = select(TrafficSignal).where(
            TrafficSignal.id == signal_id, TrafficSignal.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_signals(
        self, state: str | None = None, route_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> list[TrafficSignal]:
        stmt = select(TrafficSignal).where(TrafficSignal.is_deleted.is_(False))
        if state:
            stmt = stmt.where(TrafficSignal.state == state)
        if route_id:
            stmt = stmt.where(TrafficSignal.route_id == route_id)
        stmt = stmt.order_by(TrafficSignal.signal_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_signals(self, state: str | None = None) -> int:
        stmt = select(func.count(TrafficSignal.id)).where(TrafficSignal.is_deleted.is_(False))
        if state:
            stmt = stmt.where(TrafficSignal.state == state)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_signal(self, data: dict) -> TrafficSignal:
        signal = TrafficSignal(**data)
        self._session.add(signal)
        await self._session.flush()
        return signal

    async def update_signal(self, signal_id: uuid.UUID, data: dict) -> TrafficSignal | None:
        stmt = (
            update(TrafficSignal)
            .where(TrafficSignal.id == signal_id, TrafficSignal.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficSignal)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_signal(self, signal_id: uuid.UUID) -> bool:
        stmt = update(TrafficSignal).where(
            TrafficSignal.id == signal_id, TrafficSignal.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Spawn Point ──────────────────────────────────────────────

    async def get_spawn_point_by_id(self, sp_id: uuid.UUID) -> TrafficSpawnPoint | None:
        stmt = select(TrafficSpawnPoint).where(
            TrafficSpawnPoint.id == sp_id, TrafficSpawnPoint.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_spawn_points(
        self, spawn_type: str | None = None, zone_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> list[TrafficSpawnPoint]:
        stmt = select(TrafficSpawnPoint).where(TrafficSpawnPoint.is_deleted.is_(False))
        if spawn_type:
            stmt = stmt.where(TrafficSpawnPoint.spawn_type == spawn_type)
        if zone_id:
            stmt = stmt.where(TrafficSpawnPoint.zone_id == zone_id)
        stmt = stmt.order_by(TrafficSpawnPoint.spawn_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_spawn_points(self, spawn_type: str | None = None) -> int:
        stmt = select(func.count(TrafficSpawnPoint.id)).where(TrafficSpawnPoint.is_deleted.is_(False))
        if spawn_type:
            stmt = stmt.where(TrafficSpawnPoint.spawn_type == spawn_type)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_spawn_point(self, data: dict) -> TrafficSpawnPoint:
        sp = TrafficSpawnPoint(**data)
        self._session.add(sp)
        await self._session.flush()
        return sp

    async def update_spawn_point(self, sp_id: uuid.UUID, data: dict) -> TrafficSpawnPoint | None:
        stmt = (
            update(TrafficSpawnPoint)
            .where(TrafficSpawnPoint.id == sp_id, TrafficSpawnPoint.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficSpawnPoint)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_spawn_point(self, sp_id: uuid.UUID) -> bool:
        stmt = update(TrafficSpawnPoint).where(
            TrafficSpawnPoint.id == sp_id, TrafficSpawnPoint.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Density ──────────────────────────────────────────────────

    async def get_density_by_id(self, density_id: uuid.UUID) -> TrafficDensity | None:
        stmt = select(TrafficDensity).where(
            TrafficDensity.id == density_id, TrafficDensity.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_densities(
        self, density_level: str | None = None, zone_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> list[TrafficDensity]:
        stmt = select(TrafficDensity).where(TrafficDensity.is_deleted.is_(False))
        if density_level:
            stmt = stmt.where(TrafficDensity.density_level == density_level)
        if zone_id:
            stmt = stmt.where(TrafficDensity.zone_id == zone_id)
        stmt = stmt.order_by(TrafficDensity.density_level).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_densities(self, zone_id: uuid.UUID | None = None) -> int:
        stmt = select(func.count(TrafficDensity.id)).where(TrafficDensity.is_deleted.is_(False))
        if zone_id:
            stmt = stmt.where(TrafficDensity.zone_id == zone_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_density(self, data: dict) -> TrafficDensity:
        density = TrafficDensity(**data)
        self._session.add(density)
        await self._session.flush()
        return density

    async def update_density(self, density_id: uuid.UUID, data: dict) -> TrafficDensity | None:
        stmt = (
            update(TrafficDensity)
            .where(TrafficDensity.id == density_id, TrafficDensity.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficDensity)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Traffic Spawn Rule ───────────────────────────────────────────────

    async def get_spawn_rule_by_id(self, rule_id: uuid.UUID) -> TrafficSpawnRule | None:
        stmt = select(TrafficSpawnRule).where(
            TrafficSpawnRule.id == rule_id, TrafficSpawnRule.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_spawn_rules(
        self, rule_type: str | None = None, skip: int = 0, limit: int = 50
    ) -> list[TrafficSpawnRule]:
        stmt = select(TrafficSpawnRule).where(TrafficSpawnRule.is_deleted.is_(False))
        if rule_type:
            stmt = stmt.where(TrafficSpawnRule.rule_type == rule_type)
        stmt = stmt.order_by(TrafficSpawnRule.rule_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_spawn_rules(self) -> int:
        stmt = select(func.count(TrafficSpawnRule.id)).where(TrafficSpawnRule.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_spawn_rule(self, data: dict) -> TrafficSpawnRule:
        rule = TrafficSpawnRule(**data)
        self._session.add(rule)
        await self._session.flush()
        return rule

    async def update_spawn_rule(self, rule_id: uuid.UUID, data: dict) -> TrafficSpawnRule | None:
        stmt = (
            update(TrafficSpawnRule)
            .where(TrafficSpawnRule.id == rule_id, TrafficSpawnRule.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficSpawnRule)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_spawn_rule(self, rule_id: uuid.UUID) -> bool:
        stmt = update(TrafficSpawnRule).where(
            TrafficSpawnRule.id == rule_id, TrafficSpawnRule.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Despawn Rule ─────────────────────────────────────────────

    async def get_despawn_rule_by_id(self, rule_id: uuid.UUID) -> TrafficDespawnRule | None:
        stmt = select(TrafficDespawnRule).where(
            TrafficDespawnRule.id == rule_id, TrafficDespawnRule.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_despawn_rules(
        self, rule_type: str | None = None, skip: int = 0, limit: int = 50
    ) -> list[TrafficDespawnRule]:
        stmt = select(TrafficDespawnRule).where(TrafficDespawnRule.is_deleted.is_(False))
        if rule_type:
            stmt = stmt.where(TrafficDespawnRule.rule_type == rule_type)
        stmt = stmt.order_by(TrafficDespawnRule.rule_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_despawn_rules(self) -> int:
        stmt = select(func.count(TrafficDespawnRule.id)).where(TrafficDespawnRule.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_despawn_rule(self, data: dict) -> TrafficDespawnRule:
        rule = TrafficDespawnRule(**data)
        self._session.add(rule)
        await self._session.flush()
        return rule

    async def update_despawn_rule(self, rule_id: uuid.UUID, data: dict) -> TrafficDespawnRule | None:
        stmt = (
            update(TrafficDespawnRule)
            .where(TrafficDespawnRule.id == rule_id, TrafficDespawnRule.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficDespawnRule)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_despawn_rule(self, rule_id: uuid.UUID) -> bool:
        stmt = update(TrafficDespawnRule).where(
            TrafficDespawnRule.id == rule_id, TrafficDespawnRule.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Vehicle ──────────────────────────────────────────────────

    async def get_vehicle_by_id(self, vehicle_id: uuid.UUID) -> TrafficVehicle | None:
        stmt = select(TrafficVehicle).where(
            TrafficVehicle.id == vehicle_id, TrafficVehicle.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vehicle_by_plate(self, license_plate: str) -> TrafficVehicle | None:
        stmt = select(TrafficVehicle).where(
            TrafficVehicle.license_plate == license_plate,
            TrafficVehicle.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_vehicles(
        self, vehicle_type: str | None = None, zone_id: uuid.UUID | None = None,
        active_only: bool = False, emergency_only: bool = False,
        skip: int = 0, limit: int = 50,
    ) -> list[TrafficVehicle]:
        stmt = select(TrafficVehicle).where(TrafficVehicle.is_deleted.is_(False))
        if vehicle_type:
            stmt = stmt.where(TrafficVehicle.vehicle_type == vehicle_type)
        if zone_id:
            stmt = stmt.where(TrafficVehicle.zone_id == zone_id)
        if active_only:
            stmt = stmt.where(TrafficVehicle.is_active.is_(True))
        if emergency_only:
            stmt = stmt.where(TrafficVehicle.is_emergency.is_(True))
        stmt = stmt.order_by(TrafficVehicle.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_vehicles(
        self, vehicle_type: str | None = None, zone_id: uuid.UUID | None = None,
        active_only: bool = False, emergency_only: bool = False,
    ) -> int:
        stmt = select(func.count(TrafficVehicle.id)).where(TrafficVehicle.is_deleted.is_(False))
        if vehicle_type:
            stmt = stmt.where(TrafficVehicle.vehicle_type == vehicle_type)
        if zone_id:
            stmt = stmt.where(TrafficVehicle.zone_id == zone_id)
        if active_only:
            stmt = stmt.where(TrafficVehicle.is_active.is_(True))
        if emergency_only:
            stmt = stmt.where(TrafficVehicle.is_emergency.is_(True))
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_vehicle(self, data: dict) -> TrafficVehicle:
        vehicle = TrafficVehicle(**data)
        self._session.add(vehicle)
        await self._session.flush()
        return vehicle

    async def update_vehicle(self, vehicle_id: uuid.UUID, data: dict) -> TrafficVehicle | None:
        stmt = (
            update(TrafficVehicle)
            .where(TrafficVehicle.id == vehicle_id, TrafficVehicle.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficVehicle)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_vehicle(self, vehicle_id: uuid.UUID) -> bool:
        stmt = update(TrafficVehicle).where(
            TrafficVehicle.id == vehicle_id, TrafficVehicle.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Emergency Vehicle ────────────────────────────────────────

    async def get_emergency_by_id(self, ev_id: uuid.UUID) -> TrafficEmergencyVehicle | None:
        stmt = select(TrafficEmergencyVehicle).where(
            TrafficEmergencyVehicle.id == ev_id, TrafficEmergencyVehicle.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_emergency_by_vehicle_id(self, vehicle_id: uuid.UUID) -> TrafficEmergencyVehicle | None:
        stmt = select(TrafficEmergencyVehicle).where(
            TrafficEmergencyVehicle.vehicle_id == vehicle_id,
            TrafficEmergencyVehicle.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_emergency_vehicles(
        self, emergency_type: str | None = None, active_only: bool = False,
        skip: int = 0, limit: int = 50,
    ) -> list[TrafficEmergencyVehicle]:
        stmt = select(TrafficEmergencyVehicle).where(TrafficEmergencyVehicle.is_deleted.is_(False))
        if emergency_type:
            stmt = stmt.where(TrafficEmergencyVehicle.emergency_type == emergency_type)
        if active_only:
            stmt = stmt.where(TrafficEmergencyVehicle.is_active_call.is_(True))
        stmt = stmt.order_by(TrafficEmergencyVehicle.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_emergency_vehicles(self, emergency_type: str | None = None) -> int:
        stmt = select(func.count(TrafficEmergencyVehicle.id)).where(TrafficEmergencyVehicle.is_deleted.is_(False))
        if emergency_type:
            stmt = stmt.where(TrafficEmergencyVehicle.emergency_type == emergency_type)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_emergency_vehicle(self, data: dict) -> TrafficEmergencyVehicle:
        ev = TrafficEmergencyVehicle(**data)
        self._session.add(ev)
        await self._session.flush()
        return ev

    async def update_emergency_vehicle(self, ev_id: uuid.UUID, data: dict) -> TrafficEmergencyVehicle | None:
        stmt = (
            update(TrafficEmergencyVehicle)
            .where(TrafficEmergencyVehicle.id == ev_id, TrafficEmergencyVehicle.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficEmergencyVehicle)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Traffic Statistics ───────────────────────────────────────────────

    async def get_statistics_by_id(self, stats_id: uuid.UUID) -> TrafficStatistics | None:
        stmt = select(TrafficStatistics).where(
            TrafficStatistics.id == stats_id, TrafficStatistics.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_statistics_for_zone(
        self, zone_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[TrafficStatistics]:
        stmt = (
            select(TrafficStatistics)
            .where(TrafficStatistics.zone_id == zone_id, TrafficStatistics.is_deleted.is_(False))
            .order_by(TrafficStatistics.date_recorded.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_statistics_by_date(
        self, date_recorded: str, skip: int = 0, limit: int = 50
    ) -> list[TrafficStatistics]:
        stmt = (
            select(TrafficStatistics)
            .where(TrafficStatistics.date_recorded == date_recorded, TrafficStatistics.is_deleted.is_(False))
            .order_by(TrafficStatistics.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_statistics(self, zone_id: uuid.UUID | None = None) -> int:
        stmt = select(func.count(TrafficStatistics.id)).where(TrafficStatistics.is_deleted.is_(False))
        if zone_id:
            stmt = stmt.where(TrafficStatistics.zone_id == zone_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_statistics(self, data: dict) -> TrafficStatistics:
        stats = TrafficStatistics(**data)
        self._session.add(stats)
        await self._session.flush()
        return stats

    async def update_statistics(self, stats_id: uuid.UUID, data: dict) -> TrafficStatistics | None:
        stmt = (
            update(TrafficStatistics)
            .where(TrafficStatistics.id == stats_id, TrafficStatistics.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficStatistics)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Traffic Speed Limit ──────────────────────────────────────────────

    async def get_speed_limit_by_id(self, sl_id: uuid.UUID) -> TrafficSpeedLimit | None:
        stmt = select(TrafficSpeedLimit).where(
            TrafficSpeedLimit.id == sl_id, TrafficSpeedLimit.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_speed_limits(
        self, zone_id: uuid.UUID | None = None, skip: int = 0, limit: int = 50
    ) -> list[TrafficSpeedLimit]:
        stmt = select(TrafficSpeedLimit).where(TrafficSpeedLimit.is_deleted.is_(False))
        if zone_id:
            stmt = stmt.where(TrafficSpeedLimit.zone_id == zone_id)
        stmt = stmt.order_by(TrafficSpeedLimit.speed_limit_kmh).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_speed_limits(self, zone_id: uuid.UUID | None = None) -> int:
        stmt = select(func.count(TrafficSpeedLimit.id)).where(TrafficSpeedLimit.is_deleted.is_(False))
        if zone_id:
            stmt = stmt.where(TrafficSpeedLimit.zone_id == zone_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_speed_limit(self, data: dict) -> TrafficSpeedLimit:
        sl = TrafficSpeedLimit(**data)
        self._session.add(sl)
        await self._session.flush()
        return sl

    async def update_speed_limit(self, sl_id: uuid.UUID, data: dict) -> TrafficSpeedLimit | None:
        stmt = (
            update(TrafficSpeedLimit)
            .where(TrafficSpeedLimit.id == sl_id, TrafficSpeedLimit.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficSpeedLimit)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_speed_limit(self, sl_id: uuid.UUID) -> bool:
        stmt = update(TrafficSpeedLimit).where(
            TrafficSpeedLimit.id == sl_id, TrafficSpeedLimit.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Traffic Violation ────────────────────────────────────────────────

    async def get_violation_by_id(self, v_id: uuid.UUID) -> TrafficViolation | None:
        stmt = select(TrafficViolation).where(
            TrafficViolation.id == v_id, TrafficViolation.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_violations(
        self, violation_type: str | None = None, player_id: uuid.UUID | None = None,
        resolved: bool | None = None, skip: int = 0, limit: int = 50,
    ) -> list[TrafficViolation]:
        stmt = select(TrafficViolation).where(TrafficViolation.is_deleted.is_(False))
        if violation_type:
            stmt = stmt.where(TrafficViolation.violation_type == violation_type)
        if player_id:
            stmt = stmt.where(TrafficViolation.player_id == player_id)
        if resolved is not None:
            stmt = stmt.where(TrafficViolation.is_resolved == resolved)
        stmt = stmt.order_by(TrafficViolation.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_violations(
        self, violation_type: str | None = None, player_id: uuid.UUID | None = None
    ) -> int:
        stmt = select(func.count(TrafficViolation.id)).where(TrafficViolation.is_deleted.is_(False))
        if violation_type:
            stmt = stmt.where(TrafficViolation.violation_type == violation_type)
        if player_id:
            stmt = stmt.where(TrafficViolation.player_id == player_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_violation(self, data: dict) -> TrafficViolation:
        violation = TrafficViolation(**data)
        self._session.add(violation)
        await self._session.flush()
        return violation

    async def update_violation(self, v_id: uuid.UUID, data: dict) -> TrafficViolation | None:
        stmt = (
            update(TrafficViolation)
            .where(TrafficViolation.id == v_id, TrafficViolation.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficViolation)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Traffic Event ────────────────────────────────────────────────────

    async def get_event_by_id(self, event_id: uuid.UUID) -> TrafficEvent | None:
        stmt = select(TrafficEvent).where(
            TrafficEvent.id == event_id, TrafficEvent.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_events(
        self, event_type: str | None = None, resolved: bool | None = None,
        skip: int = 0, limit: int = 50,
    ) -> list[TrafficEvent]:
        stmt = select(TrafficEvent).where(TrafficEvent.is_deleted.is_(False))
        if event_type:
            stmt = stmt.where(TrafficEvent.event_type == event_type)
        if resolved is not None:
            stmt = stmt.where(TrafficEvent.is_resolved == resolved)
        stmt = stmt.order_by(TrafficEvent.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_events(self, event_type: str | None = None, resolved: bool | None = None) -> int:
        stmt = select(func.count(TrafficEvent.id)).where(TrafficEvent.is_deleted.is_(False))
        if event_type:
            stmt = stmt.where(TrafficEvent.event_type == event_type)
        if resolved is not None:
            stmt = stmt.where(TrafficEvent.is_resolved == resolved)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_event(self, data: dict) -> TrafficEvent:
        event = TrafficEvent(**data)
        self._session.add(event)
        await self._session.flush()
        return event

    async def update_event(self, event_id: uuid.UUID, data: dict) -> TrafficEvent | None:
        stmt = (
            update(TrafficEvent)
            .where(TrafficEvent.id == event_id, TrafficEvent.is_deleted.is_(False))
            .values(**data)
            .returning(TrafficEvent)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
