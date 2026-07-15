"""Traffic API endpoints — zones, routes, lanes, signals, spawn points, density, spawn/despawn rules, vehicles, emergency vehicles, statistics, speed limits, violations, events."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.common import SuccessResponse
from app.schemas.traffic import (
    TrafficDensityCreateRequest,
    TrafficDensityListResponse,
    TrafficDensityResponse,
    TrafficDensityUpdateRequest,
    TrafficDespawnRuleCreateRequest,
    TrafficDespawnRuleListResponse,
    TrafficDespawnRuleResponse,
    TrafficDespawnRuleUpdateRequest,
    TrafficEmergencyVehicleCreateRequest,
    TrafficEmergencyVehicleListResponse,
    TrafficEmergencyVehicleResponse,
    TrafficEmergencyVehicleUpdateRequest,
    TrafficEventCreateRequest,
    TrafficEventListResponse,
    TrafficEventResponse,
    TrafficEventUpdateRequest,
    TrafficLaneCreateRequest,
    TrafficLaneListResponse,
    TrafficLaneResponse,
    TrafficLaneUpdateRequest,
    TrafficRouteCreateRequest,
    TrafficRouteListResponse,
    TrafficRouteResponse,
    TrafficRouteUpdateRequest,
    TrafficSignalCreateRequest,
    TrafficSignalListResponse,
    TrafficSignalResponse,
    TrafficSignalUpdateRequest,
    TrafficSpawnPointCreateRequest,
    TrafficSpawnPointListResponse,
    TrafficSpawnPointResponse,
    TrafficSpawnPointUpdateRequest,
    TrafficSpawnRuleCreateRequest,
    TrafficSpawnRuleListResponse,
    TrafficSpawnRuleResponse,
    TrafficSpawnRuleUpdateRequest,
    TrafficSpeedLimitCreateRequest,
    TrafficSpeedLimitListResponse,
    TrafficSpeedLimitResponse,
    TrafficSpeedLimitUpdateRequest,
    TrafficStatisticsCreateRequest,
    TrafficStatisticsListResponse,
    TrafficStatisticsResponse,
    TrafficStatisticsUpdateRequest,
    TrafficVehicleCreateRequest,
    TrafficVehicleListResponse,
    TrafficVehicleResponse,
    TrafficVehicleUpdateRequest,
    TrafficViolationCreateRequest,
    TrafficViolationListResponse,
    TrafficViolationResponse,
    TrafficViolationUpdateRequest,
    TrafficZoneCreateRequest,
    TrafficZoneListResponse,
    TrafficZoneResponse,
    TrafficZoneUpdateRequest,
)
from app.services.traffic import TrafficService

router = APIRouter(prefix="/traffic", tags=["Traffic"])


def _get_traffic_service(session: AsyncSession) -> TrafficService:
    return TrafficService(session)


# ── Traffic Zones ────────────────────────────────────────────────────────────


@router.get("/zones", response_model=TrafficZoneListResponse)
async def list_zones(
    zone_type: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    zones, total = await svc.list_zones(zone_type, skip, limit)
    return TrafficZoneListResponse(
        message=f"{len(zones)} zones retrieved",
        data=[TrafficZoneResponse.model_validate(z) for z in zones],
        total=total,
    )


@router.get("/zones/{zone_id}", response_model=SuccessResponse[TrafficZoneResponse])
async def get_zone(
    zone_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    zone = await svc.get_zone(zone_id)
    return SuccessResponse(
        message="Zone retrieved",
        data=TrafficZoneResponse.model_validate(zone),
    )


@router.post("/zones", status_code=201)
async def create_zone(
    body: TrafficZoneCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    zone = await svc.create_zone(body.model_dump())
    return SuccessResponse(
        message="Zone created",
        data=TrafficZoneResponse.model_validate(zone),
    )


@router.patch("/zones/{zone_id}")
async def update_zone(
    zone_id: uuid.UUID,
    body: TrafficZoneUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    zone = await svc.update_zone(zone_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Zone updated",
        data=TrafficZoneResponse.model_validate(zone),
    )


@router.delete("/zones/{zone_id}")
async def delete_zone(
    zone_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.delete_zone(zone_id)
    return SuccessResponse(message="Zone deleted")


# ── Traffic Routes ───────────────────────────────────────────────────────────


@router.get("/routes", response_model=TrafficRouteListResponse)
async def list_routes(
    route_type: str | None = None,
    zone_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    routes, total = await svc.list_routes(route_type, zone_id, skip, limit)
    return TrafficRouteListResponse(
        message=f"{len(routes)} routes retrieved",
        data=[TrafficRouteResponse.model_validate(r) for r in routes],
        total=total,
    )


@router.get("/routes/{route_id}", response_model=SuccessResponse[TrafficRouteResponse])
async def get_route(
    route_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    route = await svc.get_route(route_id)
    return SuccessResponse(
        message="Route retrieved",
        data=TrafficRouteResponse.model_validate(route),
    )


@router.post("/routes", status_code=201)
async def create_route(
    body: TrafficRouteCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    route = await svc.create_route(body.model_dump())
    return SuccessResponse(
        message="Route created",
        data=TrafficRouteResponse.model_validate(route),
    )


@router.patch("/routes/{route_id}")
async def update_route(
    route_id: uuid.UUID,
    body: TrafficRouteUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    route = await svc.update_route(route_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Route updated",
        data=TrafficRouteResponse.model_validate(route),
    )


@router.delete("/routes/{route_id}")
async def delete_route(
    route_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.delete_route(route_id)
    return SuccessResponse(message="Route deleted")


# ── Traffic Lanes ────────────────────────────────────────────────────────────


@router.get("/routes/{route_id}/lanes", response_model=TrafficLaneListResponse)
async def list_lanes(
    route_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    lanes, total = await svc.list_lanes_for_route(route_id, skip, limit)
    return TrafficLaneListResponse(
        message=f"{len(lanes)} lanes retrieved",
        data=[TrafficLaneResponse.model_validate(l) for l in lanes],
        total=total,
    )


@router.get("/lanes/{lane_id}", response_model=SuccessResponse[TrafficLaneResponse])
async def get_lane(
    lane_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    lane = await svc.get_lane(lane_id)
    return SuccessResponse(
        message="Lane retrieved",
        data=TrafficLaneResponse.model_validate(lane),
    )


@router.post("/lanes", status_code=201)
async def create_lane(
    body: TrafficLaneCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    lane = await svc.create_lane(body.model_dump())
    return SuccessResponse(
        message="Lane created",
        data=TrafficLaneResponse.model_validate(lane),
    )


@router.patch("/lanes/{lane_id}")
async def update_lane(
    lane_id: uuid.UUID,
    body: TrafficLaneUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    lane = await svc.update_lane(lane_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Lane updated",
        data=TrafficLaneResponse.model_validate(lane),
    )


@router.delete("/lanes/{lane_id}")
async def delete_lane(
    lane_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.delete_lane(lane_id)
    return SuccessResponse(message="Lane deleted")


# ── Traffic Signals ──────────────────────────────────────────────────────────


@router.get("/signals", response_model=TrafficSignalListResponse)
async def list_signals(
    state: str | None = None,
    route_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    signals, total = await svc.list_signals(state, route_id, skip, limit)
    return TrafficSignalListResponse(
        message=f"{len(signals)} signals retrieved",
        data=[TrafficSignalResponse.model_validate(s) for s in signals],
        total=total,
    )


@router.get("/signals/{signal_id}", response_model=SuccessResponse[TrafficSignalResponse])
async def get_signal(
    signal_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    signal = await svc.get_signal(signal_id)
    return SuccessResponse(
        message="Signal retrieved",
        data=TrafficSignalResponse.model_validate(signal),
    )


@router.post("/signals", status_code=201)
async def create_signal(
    body: TrafficSignalCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    signal = await svc.create_signal(body.model_dump())
    return SuccessResponse(
        message="Signal created",
        data=TrafficSignalResponse.model_validate(signal),
    )


@router.patch("/signals/{signal_id}")
async def update_signal(
    signal_id: uuid.UUID,
    body: TrafficSignalUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    signal = await svc.update_signal(signal_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Signal updated",
        data=TrafficSignalResponse.model_validate(signal),
    )


@router.post("/signals/{signal_id}/state/{state}")
async def change_signal_state(
    signal_id: uuid.UUID,
    state: str,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    signal = await svc.change_signal_state(signal_id, state)
    return SuccessResponse(
        message="Signal state changed",
        data=TrafficSignalResponse.model_validate(signal),
    )


@router.post("/signals/{signal_id}/emergency-on")
async def activate_emergency_override(
    signal_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    signal = await svc.activate_emergency_override(signal_id)
    return SuccessResponse(
        message="Emergency override activated",
        data=TrafficSignalResponse.model_validate(signal),
    )


@router.post("/signals/{signal_id}/emergency-off")
async def deactivate_emergency_override(
    signal_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    signal = await svc.deactivate_emergency_override(signal_id)
    return SuccessResponse(
        message="Emergency override deactivated",
        data=TrafficSignalResponse.model_validate(signal),
    )


@router.delete("/signals/{signal_id}")
async def delete_signal(
    signal_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.delete_signal(signal_id)
    return SuccessResponse(message="Signal deleted")


# ── Spawn Points ─────────────────────────────────────────────────────────────


@router.get("/spawn-points", response_model=TrafficSpawnPointListResponse)
async def list_spawn_points(
    spawn_type: str | None = None,
    zone_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    sps, total = await svc.list_spawn_points(spawn_type, zone_id, skip, limit)
    return TrafficSpawnPointListResponse(
        message=f"{len(sps)} spawn points retrieved",
        data=[TrafficSpawnPointResponse.model_validate(s) for s in sps],
        total=total,
    )


@router.get("/spawn-points/{sp_id}", response_model=SuccessResponse[TrafficSpawnPointResponse])
async def get_spawn_point(
    sp_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    sp = await svc.get_spawn_point(sp_id)
    return SuccessResponse(
        message="Spawn point retrieved",
        data=TrafficSpawnPointResponse.model_validate(sp),
    )


@router.post("/spawn-points", status_code=201)
async def create_spawn_point(
    body: TrafficSpawnPointCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    sp = await svc.create_spawn_point(body.model_dump())
    return SuccessResponse(
        message="Spawn point created",
        data=TrafficSpawnPointResponse.model_validate(sp),
    )


@router.patch("/spawn-points/{sp_id}")
async def update_spawn_point(
    sp_id: uuid.UUID,
    body: TrafficSpawnPointUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    sp = await svc.update_spawn_point(sp_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Spawn point updated",
        data=TrafficSpawnPointResponse.model_validate(sp),
    )


@router.delete("/spawn-points/{sp_id}")
async def delete_spawn_point(
    sp_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.delete_spawn_point(sp_id)
    return SuccessResponse(message="Spawn point deleted")


# ── Density ─────────────────────────────────────────────────────────────────


@router.get("/density", response_model=TrafficDensityListResponse)
async def list_densities(
    density_level: str | None = None,
    zone_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    densities, total = await svc.list_densities(density_level, zone_id, skip, limit)
    return TrafficDensityListResponse(
        message=f"{len(densities)} density configs retrieved",
        data=[TrafficDensityResponse.model_validate(d) for d in densities],
        total=total,
    )


@router.get("/density/{density_id}", response_model=SuccessResponse[TrafficDensityResponse])
async def get_density(
    density_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    density = await svc.get_density(density_id)
    return SuccessResponse(
        message="Density config retrieved",
        data=TrafficDensityResponse.model_validate(density),
    )


@router.post("/density", status_code=201)
async def create_density(
    body: TrafficDensityCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    density = await svc.create_density(body.model_dump())
    return SuccessResponse(
        message="Density config created",
        data=TrafficDensityResponse.model_validate(density),
    )


@router.patch("/density/{density_id}")
async def update_density(
    density_id: uuid.UUID,
    body: TrafficDensityUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    density = await svc.update_density(density_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Density config updated",
        data=TrafficDensityResponse.model_validate(density),
    )


# ── Spawn Rules ─────────────────────────────────────────────────────────────


@router.get("/spawn-rules", response_model=TrafficSpawnRuleListResponse)
async def list_spawn_rules(
    rule_type: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    rules, total = await svc.list_spawn_rules(rule_type, skip, limit)
    return TrafficSpawnRuleListResponse(
        message=f"{len(rules)} spawn rules retrieved",
        data=[TrafficSpawnRuleResponse.model_validate(r) for r in rules],
        total=total,
    )


@router.get("/spawn-rules/{rule_id}", response_model=SuccessResponse[TrafficSpawnRuleResponse])
async def get_spawn_rule(
    rule_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    rule = await svc.get_spawn_rule(rule_id)
    return SuccessResponse(
        message="Spawn rule retrieved",
        data=TrafficSpawnRuleResponse.model_validate(rule),
    )


@router.post("/spawn-rules", status_code=201)
async def create_spawn_rule(
    body: TrafficSpawnRuleCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    rule = await svc.create_spawn_rule(body.model_dump())
    return SuccessResponse(
        message="Spawn rule created",
        data=TrafficSpawnRuleResponse.model_validate(rule),
    )


@router.patch("/spawn-rules/{rule_id}")
async def update_spawn_rule(
    rule_id: uuid.UUID,
    body: TrafficSpawnRuleUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    rule = await svc.update_spawn_rule(rule_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Spawn rule updated",
        data=TrafficSpawnRuleResponse.model_validate(rule),
    )


@router.delete("/spawn-rules/{rule_id}")
async def delete_spawn_rule(
    rule_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.delete_spawn_rule(rule_id)
    return SuccessResponse(message="Spawn rule deleted")


# ── Despawn Rules ───────────────────────────────────────────────────────────


@router.get("/despawn-rules", response_model=TrafficDespawnRuleListResponse)
async def list_despawn_rules(
    rule_type: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    rules, total = await svc.list_despawn_rules(rule_type, skip, limit)
    return TrafficDespawnRuleListResponse(
        message=f"{len(rules)} despawn rules retrieved",
        data=[TrafficDespawnRuleResponse.model_validate(r) for r in rules],
        total=total,
    )


@router.get("/despawn-rules/{rule_id}", response_model=SuccessResponse[TrafficDespawnRuleResponse])
async def get_despawn_rule(
    rule_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    rule = await svc.get_despawn_rule(rule_id)
    return SuccessResponse(
        message="Despawn rule retrieved",
        data=TrafficDespawnRuleResponse.model_validate(rule),
    )


@router.post("/despawn-rules", status_code=201)
async def create_despawn_rule(
    body: TrafficDespawnRuleCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    rule = await svc.create_despawn_rule(body.model_dump())
    return SuccessResponse(
        message="Despawn rule created",
        data=TrafficDespawnRuleResponse.model_validate(rule),
    )


@router.patch("/despawn-rules/{rule_id}")
async def update_despawn_rule(
    rule_id: uuid.UUID,
    body: TrafficDespawnRuleUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    rule = await svc.update_despawn_rule(rule_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Despawn rule updated",
        data=TrafficDespawnRuleResponse.model_validate(rule),
    )


@router.delete("/despawn-rules/{rule_id}")
async def delete_despawn_rule(
    rule_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.delete_despawn_rule(rule_id)
    return SuccessResponse(message="Despawn rule deleted")


# ── Traffic Vehicles ─────────────────────────────────────────────────────────


@router.get("/vehicles", response_model=TrafficVehicleListResponse)
async def list_vehicles(
    vehicle_type: str | None = None,
    zone_id: uuid.UUID | None = None,
    active_only: bool = False,
    emergency_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    vehicles, total = await svc.list_vehicles(
        vehicle_type, zone_id, active_only, emergency_only, skip, limit
    )
    return TrafficVehicleListResponse(
        message=f"{len(vehicles)} vehicles retrieved",
        data=[TrafficVehicleResponse.model_validate(v) for v in vehicles],
        total=total,
    )


@router.get("/vehicles/{vehicle_id}", response_model=SuccessResponse[TrafficVehicleResponse])
async def get_vehicle(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    vehicle = await svc.get_vehicle(vehicle_id)
    return SuccessResponse(
        message="Vehicle retrieved",
        data=TrafficVehicleResponse.model_validate(vehicle),
    )


@router.post("/vehicles", status_code=201)
async def spawn_vehicle(
    body: TrafficVehicleCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    vehicle = await svc.spawn_vehicle(body.model_dump())
    return SuccessResponse(
        message="Vehicle spawned",
        data=TrafficVehicleResponse.model_validate(vehicle),
    )


@router.patch("/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: uuid.UUID,
    body: TrafficVehicleUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    vehicle = await svc.update_vehicle(vehicle_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Vehicle updated",
        data=TrafficVehicleResponse.model_validate(vehicle),
    )


@router.post("/vehicles/{vehicle_id}/despawn")
async def despawn_vehicle(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.despawn_vehicle(vehicle_id)
    return SuccessResponse(message="Vehicle despawned")


# ── Emergency Vehicles ───────────────────────────────────────────────────────


@router.get("/emergency-vehicles", response_model=TrafficEmergencyVehicleListResponse)
async def list_emergency_vehicles(
    emergency_type: str | None = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    evs, total = await svc.list_emergency_vehicles(emergency_type, active_only, skip, limit)
    return TrafficEmergencyVehicleListResponse(
        message=f"{len(evs)} emergency vehicles retrieved",
        data=[TrafficEmergencyVehicleResponse.model_validate(e) for e in evs],
        total=total,
    )


@router.get("/emergency-vehicles/{ev_id}", response_model=SuccessResponse[TrafficEmergencyVehicleResponse])
async def get_emergency_vehicle(
    ev_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    ev = await svc.get_emergency_vehicle(ev_id)
    return SuccessResponse(
        message="Emergency vehicle retrieved",
        data=TrafficEmergencyVehicleResponse.model_validate(ev),
    )


@router.post("/emergency-vehicles", status_code=201)
async def register_emergency_vehicle(
    body: TrafficEmergencyVehicleCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    ev = await svc.register_emergency_vehicle(body.model_dump())
    return SuccessResponse(
        message="Emergency vehicle registered",
        data=TrafficEmergencyVehicleResponse.model_validate(ev),
    )


@router.patch("/emergency-vehicles/{ev_id}")
async def update_emergency_vehicle(
    ev_id: uuid.UUID,
    body: TrafficEmergencyVehicleUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    ev = await svc.update_emergency_vehicle(ev_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Emergency vehicle updated",
        data=TrafficEmergencyVehicleResponse.model_validate(ev),
    )


@router.post("/emergency-vehicles/{ev_id}/siren-on")
async def activate_siren(
    ev_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    ev = await svc.activate_siren(ev_id)
    return SuccessResponse(
        message="Siren activated",
        data=TrafficEmergencyVehicleResponse.model_validate(ev),
    )


@router.post("/emergency-vehicles/{ev_id}/siren-off")
async def deactivate_siren(
    ev_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    ev = await svc.deactivate_siren(ev_id)
    return SuccessResponse(
        message="Siren deactivated",
        data=TrafficEmergencyVehicleResponse.model_validate(ev),
    )


# ── Statistics ──────────────────────────────────────────────────────────────


@router.get("/statistics", response_model=TrafficStatisticsListResponse)
async def list_statistics(
    zone_id: uuid.UUID | None = None,
    date: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    if date:
        stats, total = await svc.list_statistics_by_date(date, skip, limit)
    elif zone_id:
        stats, total = await svc.list_statistics_for_zone(zone_id, skip, limit)
    else:
        stats, total = [], 0
    return TrafficStatisticsListResponse(
        message=f"{len(stats)} statistics records retrieved",
        data=[TrafficStatisticsResponse.model_validate(s) for s in stats],
        total=total,
    )


@router.get("/statistics/{stats_id}", response_model=SuccessResponse[TrafficStatisticsResponse])
async def get_statistics(
    stats_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    stats = await svc.get_statistics(stats_id)
    return SuccessResponse(
        message="Statistics retrieved",
        data=TrafficStatisticsResponse.model_validate(stats),
    )


@router.post("/statistics", status_code=201)
async def create_statistics(
    body: TrafficStatisticsCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    stats = await svc.create_statistics(body.model_dump())
    return SuccessResponse(
        message="Statistics created",
        data=TrafficStatisticsResponse.model_validate(stats),
    )


@router.patch("/statistics/{stats_id}")
async def update_statistics(
    stats_id: uuid.UUID,
    body: TrafficStatisticsUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    stats = await svc.update_statistics(stats_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Statistics updated",
        data=TrafficStatisticsResponse.model_validate(stats),
    )


# ── Speed Limits ────────────────────────────────────────────────────────────


@router.get("/speed-limits", response_model=TrafficSpeedLimitListResponse)
async def list_speed_limits(
    zone_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    limits, total = await svc.list_speed_limits(zone_id, skip, limit)
    return TrafficSpeedLimitListResponse(
        message=f"{len(limits)} speed limits retrieved",
        data=[TrafficSpeedLimitResponse.model_validate(l) for l in limits],
        total=total,
    )


@router.get("/speed-limits/{sl_id}", response_model=SuccessResponse[TrafficSpeedLimitResponse])
async def get_speed_limit(
    sl_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    sl = await svc.get_speed_limit(sl_id)
    return SuccessResponse(
        message="Speed limit retrieved",
        data=TrafficSpeedLimitResponse.model_validate(sl),
    )


@router.post("/speed-limits", status_code=201)
async def create_speed_limit(
    body: TrafficSpeedLimitCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    sl = await svc.create_speed_limit(body.model_dump())
    return SuccessResponse(
        message="Speed limit created",
        data=TrafficSpeedLimitResponse.model_validate(sl),
    )


@router.patch("/speed-limits/{sl_id}")
async def update_speed_limit(
    sl_id: uuid.UUID,
    body: TrafficSpeedLimitUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    sl = await svc.update_speed_limit(sl_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Speed limit updated",
        data=TrafficSpeedLimitResponse.model_validate(sl),
    )


@router.delete("/speed-limits/{sl_id}")
async def delete_speed_limit(
    sl_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    await svc.delete_speed_limit(sl_id)
    return SuccessResponse(message="Speed limit deleted")


# ── Violations ──────────────────────────────────────────────────────────────


@router.get("/violations", response_model=TrafficViolationListResponse)
async def list_violations(
    violation_type: str | None = None,
    player_id: uuid.UUID | None = None,
    resolved: bool | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    violations, total = await svc.list_violations(violation_type, player_id, resolved, skip, limit)
    return TrafficViolationListResponse(
        message=f"{len(violations)} violations retrieved",
        data=[TrafficViolationResponse.model_validate(v) for v in violations],
        total=total,
    )


@router.get("/violations/{v_id}", response_model=SuccessResponse[TrafficViolationResponse])
async def get_violation(
    v_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    violation = await svc.get_violation(v_id)
    return SuccessResponse(
        message="Violation retrieved",
        data=TrafficViolationResponse.model_validate(violation),
    )


@router.post("/violations", status_code=201)
async def create_violation(
    body: TrafficViolationCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    violation = await svc.create_violation(body.model_dump())
    return SuccessResponse(
        message="Violation recorded",
        data=TrafficViolationResponse.model_validate(violation),
    )


@router.post("/violations/{v_id}/resolve")
async def resolve_violation(
    v_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    violation = await svc.resolve_violation(v_id)
    return SuccessResponse(
        message="Violation resolved",
        data=TrafficViolationResponse.model_validate(violation),
    )


# ── Traffic Events ──────────────────────────────────────────────────────────


@router.get("/events", response_model=TrafficEventListResponse)
async def list_events(
    event_type: str | None = None,
    resolved: bool | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    events, total = await svc.list_events(event_type, resolved, skip, limit)
    return TrafficEventListResponse(
        message=f"{len(events)} events retrieved",
        data=[TrafficEventResponse.model_validate(e) for e in events],
        total=total,
    )


@router.get("/events/{event_id}", response_model=SuccessResponse[TrafficEventResponse])
async def get_event(
    event_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    event = await svc.get_event(event_id)
    return SuccessResponse(
        message="Event retrieved",
        data=TrafficEventResponse.model_validate(event),
    )


@router.post("/events", status_code=201)
async def create_event(
    body: TrafficEventCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    event = await svc.create_event(body.model_dump())
    return SuccessResponse(
        message="Event reported",
        data=TrafficEventResponse.model_validate(event),
    )


@router.patch("/events/{event_id}")
async def update_event(
    event_id: uuid.UUID,
    body: TrafficEventUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    event = await svc.update_event(event_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Event updated",
        data=TrafficEventResponse.model_validate(event),
    )


@router.post("/events/{event_id}/resolve")
async def resolve_event(
    event_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_traffic_service(session)
    event = await svc.resolve_event(event_id)
    return SuccessResponse(
        message="Event resolved",
        data=TrafficEventResponse.model_validate(event),
    )
