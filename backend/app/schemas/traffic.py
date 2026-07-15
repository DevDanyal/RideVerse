"""Pydantic schemas for the Traffic system."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Traffic Zone ──────────────────────────────────────────────────────────────


class TrafficZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    zone_name: str
    zone_type: str
    center_x: float
    center_y: float
    center_z: float
    radius: float
    speed_limit_kmh: float = 50.0
    max_vehicles: int = 20
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficZoneCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    zone_name: str = Field(..., min_length=1, max_length=200)
    zone_type: str = Field(..., description="Type of traffic zone")
    center_x: float
    center_y: float
    center_z: float
    radius: float = Field(..., gt=0)
    speed_limit_kmh: float = Field(default=50.0, gt=0)
    max_vehicles: int = Field(default=20, ge=1)


class TrafficZoneUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    zone_name: str | None = Field(default=None, min_length=1, max_length=200)
    zone_type: str | None = None
    center_x: float | None = None
    center_y: float | None = None
    center_z: float | None = None
    radius: float | None = Field(default=None, gt=0)
    speed_limit_kmh: float | None = Field(default=None, gt=0)
    max_vehicles: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class TrafficZoneListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficZoneResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Route ────────────────────────────────────────────────────────────


class TrafficRouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    route_name: str
    route_type: str
    start_x: float
    start_y: float
    start_z: float
    end_x: float
    end_y: float
    end_z: float
    distance_km: float = 0.0
    speed_limit_kmh: float = 50.0
    lane_count: int = 2
    is_bidirectional: bool = True
    is_active: bool = True
    zone_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficRouteCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    route_name: str = Field(..., min_length=1, max_length=200)
    route_type: str = Field(..., description="Type of route")
    start_x: float
    start_y: float
    start_z: float
    end_x: float
    end_y: float
    end_z: float
    distance_km: float = Field(default=0.0, ge=0)
    speed_limit_kmh: float = Field(default=50.0, gt=0)
    lane_count: int = Field(default=2, ge=1)
    is_bidirectional: bool = True
    zone_id: uuid.UUID | None = None


class TrafficRouteUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    route_name: str | None = Field(default=None, min_length=1, max_length=200)
    route_type: str | None = None
    start_x: float | None = None
    start_y: float | None = None
    start_z: float | None = None
    end_x: float | None = None
    end_y: float | None = None
    end_z: float | None = None
    distance_km: float | None = Field(default=None, ge=0)
    speed_limit_kmh: float | None = Field(default=None, gt=0)
    lane_count: int | None = Field(default=None, ge=1)
    is_bidirectional: bool | None = None
    is_active: bool | None = None
    zone_id: uuid.UUID | None = None


class TrafficRouteListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficRouteResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Lane ─────────────────────────────────────────────────────────────


class TrafficLaneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    route_id: uuid.UUID
    lane_number: int
    direction: str = "forward"
    speed_limit_kmh: float = 50.0
    width: float = 3.5
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficLaneCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    route_id: uuid.UUID
    lane_number: int = Field(..., ge=0)
    direction: str = Field(default="forward", max_length=20)
    speed_limit_kmh: float = Field(default=50.0, gt=0)
    width: float = Field(default=3.5, gt=0)


class TrafficLaneUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    lane_number: int | None = Field(default=None, ge=0)
    direction: str | None = None
    speed_limit_kmh: float | None = Field(default=None, gt=0)
    width: float | None = Field(default=None, gt=0)
    is_active: bool | None = None


class TrafficLaneListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficLaneResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Signal ───────────────────────────────────────────────────────────


class TrafficSignalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    signal_name: str
    location_x: float
    location_y: float
    location_z: float
    state: str = "green"
    cycle_duration_seconds: int = 30
    current_phase_seconds: int = 0
    is_active: bool = True
    is_emergency_override: bool = False
    route_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficSignalCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    signal_name: str = Field(..., min_length=1, max_length=200)
    location_x: float
    location_y: float
    location_z: float
    state: str = Field(default="green")
    cycle_duration_seconds: int = Field(default=30, gt=0)
    route_id: uuid.UUID | None = None


class TrafficSignalUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    signal_name: str | None = Field(default=None, min_length=1, max_length=200)
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    state: str | None = None
    cycle_duration_seconds: int | None = Field(default=None, gt=0)
    current_phase_seconds: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    is_emergency_override: bool | None = None
    route_id: uuid.UUID | None = None


class TrafficSignalListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficSignalResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Spawn Point ─────────────────────────────────────────────────────


class TrafficSpawnPointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    spawn_name: str
    location_x: float
    location_y: float
    location_z: float
    spawn_type: str = "spawn"
    max_vehicles: int = 5
    current_vehicles: int = 0
    is_active: bool = True
    route_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficSpawnPointCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    spawn_name: str = Field(..., min_length=1, max_length=200)
    location_x: float
    location_y: float
    location_z: float
    spawn_type: str = Field(default="spawn", max_length=20)
    max_vehicles: int = Field(default=5, ge=1)
    route_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None


class TrafficSpawnPointUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    spawn_name: str | None = Field(default=None, min_length=1, max_length=200)
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    spawn_type: str | None = None
    max_vehicles: int | None = Field(default=None, ge=1)
    current_vehicles: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    route_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None


class TrafficSpawnPointListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficSpawnPointResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Density ─────────────────────────────────────────────────────────


class TrafficDensityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    zone_id: uuid.UUID | None = None
    density_level: str
    vehicle_limit: int
    spawn_rate: float
    current_count: int = 0
    time_of_day: str | None = None
    weather_condition: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficDensityCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    zone_id: uuid.UUID | None = None
    density_level: str = Field(..., description="Traffic density level")
    vehicle_limit: int = Field(..., gt=0)
    spawn_rate: float = Field(..., gt=0)
    time_of_day: str | None = None
    weather_condition: str | None = None


class TrafficDensityUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    density_level: str | None = None
    vehicle_limit: int | None = Field(default=None, gt=0)
    spawn_rate: float | None = Field(default=None, gt=0)
    current_count: int | None = Field(default=None, ge=0)
    time_of_day: str | None = None
    weather_condition: str | None = None
    is_active: bool | None = None


class TrafficDensityListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficDensityResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Spawn Rule ──────────────────────────────────────────────────────


class TrafficSpawnRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    rule_name: str
    rule_type: str
    vehicle_type: str | None = None
    max_spawn_count: int = 10
    spawn_interval_seconds: int = 5
    min_distance_from_player: float = 100.0
    max_distance_from_player: float = 500.0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficSpawnRuleCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    rule_name: str = Field(..., min_length=1, max_length=200)
    rule_type: str = Field(..., description="Spawn rule type")
    vehicle_type: str | None = None
    max_spawn_count: int = Field(default=10, gt=0)
    spawn_interval_seconds: int = Field(default=5, gt=0)
    min_distance_from_player: float = Field(default=100.0, gt=0)
    max_distance_from_player: float = Field(default=500.0, gt=0)


class TrafficSpawnRuleUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    rule_name: str | None = Field(default=None, min_length=1, max_length=200)
    rule_type: str | None = None
    vehicle_type: str | None = None
    max_spawn_count: int | None = Field(default=None, gt=0)
    spawn_interval_seconds: int | None = Field(default=None, gt=0)
    min_distance_from_player: float | None = Field(default=None, gt=0)
    max_distance_from_player: float | None = Field(default=None, gt=0)
    is_active: bool | None = None


class TrafficSpawnRuleListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficSpawnRuleResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Despawn Rule ────────────────────────────────────────────────────


class TrafficDespawnRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    rule_name: str
    rule_type: str
    max_distance_from_player: float = 800.0
    max_lifetime_seconds: int = 300
    despawn_check_interval: int = 10
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficDespawnRuleCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    rule_name: str = Field(..., min_length=1, max_length=200)
    rule_type: str = Field(..., description="Despawn rule type")
    max_distance_from_player: float = Field(default=800.0, gt=0)
    max_lifetime_seconds: int = Field(default=300, gt=0)
    despawn_check_interval: int = Field(default=10, gt=0)


class TrafficDespawnRuleUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    rule_name: str | None = Field(default=None, min_length=1, max_length=200)
    rule_type: str | None = None
    max_distance_from_player: float | None = Field(default=None, gt=0)
    max_lifetime_seconds: int | None = Field(default=None, gt=0)
    despawn_check_interval: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class TrafficDespawnRuleListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficDespawnRuleResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Vehicle ─────────────────────────────────────────────────────────


class TrafficVehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    vehicle_type: str
    model_name: str
    speed_kmh: float = 0.0
    max_speed_kmh: float = 120.0
    health: int = 100
    fuel_level: float = 100.0
    location_x: float
    location_y: float
    location_z: float
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    is_active: bool = True
    is_emergency: bool = False
    license_plate: str | None = None
    color: str | None = None
    route_id: uuid.UUID | None = None
    lane_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None
    spawn_point_id: uuid.UUID | None = None
    spawned_at: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficVehicleCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vehicle_type: str = Field(..., description="Type of traffic vehicle")
    model_name: str = Field(..., min_length=1, max_length=100)
    location_x: float
    location_y: float
    location_z: float
    max_speed_kmh: float = Field(default=120.0, gt=0)
    color: str | None = None
    license_plate: str | None = None
    is_emergency: bool = False
    route_id: uuid.UUID | None = None
    lane_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None
    spawn_point_id: uuid.UUID | None = None


class TrafficVehicleUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    speed_kmh: float | None = Field(default=None, ge=0)
    max_speed_kmh: float | None = Field(default=None, gt=0)
    health: int | None = Field(default=None, ge=0, le=100)
    fuel_level: float | None = Field(default=None, ge=0, le=100)
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    rotation_x: float | None = None
    rotation_y: float | None = None
    rotation_z: float | None = None
    is_active: bool | None = None
    is_emergency: bool | None = None
    color: str | None = None
    route_id: uuid.UUID | None = None
    lane_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None


class TrafficVehicleListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficVehicleResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Emergency Vehicle ───────────────────────────────────────────────


class TrafficEmergencyVehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    emergency_type: str
    is_active_call: bool = False
    siren_on: bool = False
    responding_to_x: float | None = None
    responding_to_y: float | None = None
    responding_to_z: float | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficEmergencyVehicleCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vehicle_id: uuid.UUID
    emergency_type: str = Field(..., description="Type of emergency vehicle")
    is_active_call: bool = False
    siren_on: bool = False
    responding_to_x: float | None = None
    responding_to_y: float | None = None
    responding_to_z: float | None = None


class TrafficEmergencyVehicleUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    emergency_type: str | None = None
    is_active_call: bool | None = None
    siren_on: bool | None = None
    responding_to_x: float | None = None
    responding_to_y: float | None = None
    responding_to_z: float | None = None


class TrafficEmergencyVehicleListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficEmergencyVehicleResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Statistics ──────────────────────────────────────────────────────


class TrafficStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    zone_id: uuid.UUID | None = None
    total_vehicles_spawned: int = 0
    total_vehicles_despawned: int = 0
    average_speed_kmh: float = 0.0
    peak_density: int = 0
    total_accidents: int = 0
    total_violations: int = 0
    date_recorded: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficStatisticsCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    zone_id: uuid.UUID | None = None
    total_vehicles_spawned: int = Field(default=0, ge=0)
    total_vehicles_despawned: int = Field(default=0, ge=0)
    average_speed_kmh: float = Field(default=0.0, ge=0)
    peak_density: int = Field(default=0, ge=0)
    total_accidents: int = Field(default=0, ge=0)
    total_violations: int = Field(default=0, ge=0)
    date_recorded: str = Field(..., max_length=30)


class TrafficStatisticsUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_vehicles_spawned: int | None = Field(default=None, ge=0)
    total_vehicles_despawned: int | None = Field(default=None, ge=0)
    average_speed_kmh: float | None = Field(default=None, ge=0)
    peak_density: int | None = Field(default=None, ge=0)
    total_accidents: int | None = Field(default=None, ge=0)
    total_violations: int | None = Field(default=None, ge=0)


class TrafficStatisticsListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficStatisticsResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Speed Limit ─────────────────────────────────────────────────────


class TrafficSpeedLimitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    zone_id: uuid.UUID | None = None
    road_name: str | None = None
    speed_limit_kmh: float
    vehicle_type_restriction: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficSpeedLimitCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    zone_id: uuid.UUID | None = None
    road_name: str | None = Field(default=None, max_length=200)
    speed_limit_kmh: float = Field(..., gt=0)
    vehicle_type_restriction: str | None = Field(default=None, max_length=50)


class TrafficSpeedLimitUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    zone_id: uuid.UUID | None = None
    road_name: str | None = None
    speed_limit_kmh: float | None = Field(default=None, gt=0)
    vehicle_type_restriction: str | None = None
    is_active: bool | None = None


class TrafficSpeedLimitListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficSpeedLimitResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Violation ───────────────────────────────────────────────────────


class TrafficViolationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    violation_type: str
    speed_kmh: float | None = None
    speed_limit_kmh: float | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    fine_amount: float = 0.0
    is_resolved: bool = False
    zone_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficViolationCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vehicle_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    violation_type: str = Field(..., description="Type of traffic violation")
    speed_kmh: float | None = Field(default=None, ge=0)
    speed_limit_kmh: float | None = Field(default=None, ge=0)
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    fine_amount: float = Field(default=0.0, ge=0)
    zone_id: uuid.UUID | None = None


class TrafficViolationUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    fine_amount: float | None = Field(default=None, ge=0)
    is_resolved: bool | None = None


class TrafficViolationListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficViolationResponse] = Field(default_factory=list)
    total: int = 0


# ── Traffic Event ───────────────────────────────────────────────────────────


class TrafficEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    event_type: str
    location_x: float
    location_y: float
    location_z: float
    severity: str = "low"
    description: str | None = None
    is_resolved: bool = False
    reported_by_player_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class TrafficEventCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    event_type: str = Field(..., description="Type of traffic event")
    location_x: float
    location_y: float
    location_z: float
    severity: str = Field(default="low")
    description: str | None = None
    reported_by_player_id: uuid.UUID | None = None


class TrafficEventUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    event_type: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    severity: str | None = None
    description: str | None = None
    is_resolved: bool | None = None


class TrafficEventListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TrafficEventResponse] = Field(default_factory=list)
    total: int = 0
