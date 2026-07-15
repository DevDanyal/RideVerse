"""Traffic system models — vehicles, routes, lanes, signals, spawn points, density, zones, speed limits, violations, statistics, events, emergency vehicles."""
from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, Float, ForeignKey, Integer, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# ── Enums ──────────────────────────────────────────────────────────────────────


class TrafficVehicleType(StrEnum):
    MOTORCYCLE = "motorcycle"
    SCOOTER = "scooter"
    SEDAN = "sedan"
    SUV = "suv"
    PICKUP = "pickup"
    SPORTS = "sports"
    SUPERCAR = "supercar"
    LUXURY = "luxury"
    BUS = "bus"
    DELIVERY_VAN = "delivery_van"
    CARGO_TRUCK = "cargo_truck"
    FUEL_TANKER = "fuel_tanker"
    CONSTRUCTION = "construction"


class TrafficSignalState(StrEnum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    PEDESTRIAN_CROSSING = "pedestrian_crossing"
    EMERGENCY_OVERRIDE = "emergency_override"
    NIGHT_FLASH = "night_flash"


class TrafficRouteType(StrEnum):
    HIGHWAY = "highway"
    CITY = "city"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    COMMERCIAL = "commercial"


class TrafficDensityLevel(StrEnum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    RUSH_HOUR_MORNING = "rush_hour_morning"
    RUSH_HOUR_EVENING = "rush_hour_evening"


class TrafficEventType(StrEnum):
    ACCIDENT = "accident"
    ROAD_CLOSURE = "road_closure"
    CONSTRUCTION = "construction"
    BREAKDOWN = "breakdown"
    WEATHER_HAZARD = "weather_hazard"
    POLICE_ACTIVITY = "police_activity"
    EMERGENCY_RESPONSE = "emergency_response"


class TrafficViolationType(StrEnum):
    SPEEDING = "speeding"
    RUNNING_RED_LIGHT = "running_red_light"
    WRONG_LANE = "wrong_lane"
    ILLEGAL_U_TURN = "illegal_u_turn"
    ILLEGAL_PARKING = "illegal_parking"
    RECKLESS_DRIVING = "reckless_driving"
    HIT_AND_RUN = "hit_and_run"


class TrafficZoneType(StrEnum):
    HIGHWAY = "highway"
    CITY_CENTER = "city_center"
    RESIDENTIAL = "residential"
    SCHOOL_ZONE = "school_zone"
    CONSTRUCTION_ZONE = "construction_zone"
    PARKING_ZONE = "parking_zone"
    TOLL_ZONE = "toll_zone"


class EmergencyVehicleType(StrEnum):
    POLICE = "police"
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    TOW_TRUCK = "tow_truck"


class SpawnRuleType(StrEnum):
    CONTINUOUS = "continuous"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    DENSITY_BASED = "density_based"


class DespawnRuleType(StrEnum):
    DISTANCE = "distance"
    TIME_BASED = "time_based"
    PLAYER_PROXIMITY = "player_proximity"
    OFF_SCREEN = "off_screen"


# ── Traffic Zone ──────────────────────────────────────────────────────────────


class TrafficZone(Base):
    __tablename__ = "traffic_zones"

    zone_name: Mapped[str] = mapped_column(String(200), nullable=False)
    zone_type: Mapped[TrafficZoneType] = mapped_column(
        SAEnum(TrafficZoneType, native_enum=False), nullable=False, index=True
    )
    center_x: Mapped[float] = mapped_column(Float, nullable=False)
    center_y: Mapped[float] = mapped_column(Float, nullable=False)
    center_z: Mapped[float] = mapped_column(Float, nullable=False)
    radius: Mapped[float] = mapped_column(Float, nullable=False)
    speed_limit_kmh: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    max_vehicles: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    routes: Mapped[list[TrafficRoute]] = relationship("TrafficRoute", back_populates="zone")
    spawn_points: Mapped[list[TrafficSpawnPoint]] = relationship("TrafficSpawnPoint", back_populates="zone")
    densities: Mapped[list[TrafficDensity]] = relationship("TrafficDensity", back_populates="zone")
    speed_limits: Mapped[list[TrafficSpeedLimit]] = relationship("TrafficSpeedLimit", back_populates="zone")
    vehicles: Mapped[list[TrafficVehicle]] = relationship("TrafficVehicle", back_populates="zone")
    statistics: Mapped[list[TrafficStatistics]] = relationship("TrafficStatistics", back_populates="zone")
    violations: Mapped[list[TrafficViolation]] = relationship("TrafficViolation", back_populates="zone")

    __table_args__ = (
        {"comment": "Traffic zones — defined areas with specific traffic rules"},
    )


# ── Traffic Route ────────────────────────────────────────────────────────────


class TrafficRoute(Base):
    __tablename__ = "traffic_routes"

    route_name: Mapped[str] = mapped_column(String(200), nullable=False)
    route_type: Mapped[TrafficRouteType] = mapped_column(
        SAEnum(TrafficRouteType, native_enum=False), nullable=False, index=True
    )
    start_x: Mapped[float] = mapped_column(Float, nullable=False)
    start_y: Mapped[float] = mapped_column(Float, nullable=False)
    start_z: Mapped[float] = mapped_column(Float, nullable=False)
    end_x: Mapped[float] = mapped_column(Float, nullable=False)
    end_y: Mapped[float] = mapped_column(Float, nullable=False)
    end_z: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    speed_limit_kmh: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    lane_count: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    is_bidirectional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_zones.id", ondelete="SET NULL"), nullable=True
    )

    zone: Mapped[TrafficZone | None] = relationship("TrafficZone", back_populates="routes")
    lanes: Mapped[list[TrafficLane]] = relationship("TrafficLane", back_populates="route", cascade="all, delete-orphan")
    signals: Mapped[list[TrafficSignal]] = relationship("TrafficSignal", back_populates="route")
    vehicles: Mapped[list[TrafficVehicle]] = relationship("TrafficVehicle", back_populates="route")
    spawn_points: Mapped[list[TrafficSpawnPoint]] = relationship("TrafficSpawnPoint", back_populates="route")

    __table_args__ = (
        {"comment": "Traffic routes — start/end points, speed limits, lane counts"},
    )


# ── Traffic Lane ─────────────────────────────────────────────────────────────


class TrafficLane(Base):
    __tablename__ = "traffic_lanes"

    route_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("traffic_routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lane_number: Mapped[int] = mapped_column(Integer, nullable=False)
    direction: Mapped[str] = mapped_column(String(20), default="forward", nullable=False)
    speed_limit_kmh: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    width: Mapped[float] = mapped_column(Float, default=3.5, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    route: Mapped[TrafficRoute] = relationship("TrafficRoute", back_populates="lanes")

    __table_args__ = (
        {"comment": "Traffic lanes — direction, speed limit, width per route"},
    )


# ── Traffic Signal ───────────────────────────────────────────────────────────


class TrafficSignal(Base):
    __tablename__ = "traffic_signals"

    signal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    location_x: Mapped[float] = mapped_column(Float, nullable=False)
    location_y: Mapped[float] = mapped_column(Float, nullable=False)
    location_z: Mapped[float] = mapped_column(Float, nullable=False)
    state: Mapped[TrafficSignalState] = mapped_column(
        SAEnum(TrafficSignalState, native_enum=False), default=TrafficSignalState.GREEN, nullable=False, index=True
    )
    cycle_duration_seconds: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    current_phase_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_emergency_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_routes.id", ondelete="SET NULL"), nullable=True
    )

    route: Mapped[TrafficRoute | None] = relationship("TrafficRoute", back_populates="signals")

    __table_args__ = (
        {"comment": "Traffic signals — lights at intersections"},
    )


# ── Traffic Spawn Point ─────────────────────────────────────────────────────


class TrafficSpawnPoint(Base):
    __tablename__ = "traffic_spawn_points"

    spawn_name: Mapped[str] = mapped_column(String(200), nullable=False)
    location_x: Mapped[float] = mapped_column(Float, nullable=False)
    location_y: Mapped[float] = mapped_column(Float, nullable=False)
    location_z: Mapped[float] = mapped_column(Float, nullable=False)
    spawn_type: Mapped[str] = mapped_column(String(20), default="spawn", nullable=False)
    max_vehicles: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    current_vehicles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_routes.id", ondelete="SET NULL"), nullable=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_zones.id", ondelete="SET NULL"), nullable=True
    )

    route: Mapped[TrafficRoute | None] = relationship("TrafficRoute", back_populates="spawn_points")
    zone: Mapped[TrafficZone | None] = relationship("TrafficZone", back_populates="spawn_points")

    __table_args__ = (
        {"comment": "Traffic spawn points — vehicle spawn/despawn locations"},
    )


# ── Traffic Density ─────────────────────────────────────────────────────────


class TrafficDensity(Base):
    __tablename__ = "traffic_densities"

    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_zones.id", ondelete="SET NULL"), nullable=True
    )
    density_level: Mapped[TrafficDensityLevel] = mapped_column(
        SAEnum(TrafficDensityLevel, native_enum=False), nullable=False, index=True
    )
    vehicle_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    spawn_rate: Mapped[float] = mapped_column(Float, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_of_day: Mapped[str | None] = mapped_column(String(30), nullable=True)
    weather_condition: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    zone: Mapped[TrafficZone | None] = relationship("TrafficZone", back_populates="densities")

    __table_args__ = (
        {"comment": "Traffic density configuration — vehicle limits and spawn rates"},
    )


# ── Traffic Spawn Rule ──────────────────────────────────────────────────────


class TrafficSpawnRule(Base):
    __tablename__ = "traffic_spawn_rules"

    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[SpawnRuleType] = mapped_column(
        SAEnum(SpawnRuleType, native_enum=False), nullable=False, index=True
    )
    vehicle_type: Mapped[TrafficVehicleType | None] = mapped_column(
        SAEnum(TrafficVehicleType, native_enum=False), nullable=True
    )
    max_spawn_count: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    spawn_interval_seconds: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    min_distance_from_player: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    max_distance_from_player: Mapped[float] = mapped_column(Float, default=500.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        {"comment": "Traffic spawn rules — when and how to spawn traffic vehicles"},
    )


# ── Traffic Despawn Rule ────────────────────────────────────────────────────


class TrafficDespawnRule(Base):
    __tablename__ = "traffic_despawn_rules"

    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[DespawnRuleType] = mapped_column(
        SAEnum(DespawnRuleType, native_enum=False), nullable=False, index=True
    )
    max_distance_from_player: Mapped[float] = mapped_column(Float, default=800.0, nullable=False)
    max_lifetime_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    despawn_check_interval: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        {"comment": "Traffic despawn rules — when and how to remove traffic vehicles"},
    )


# ── Traffic Vehicle ─────────────────────────────────────────────────────────


class TrafficVehicle(Base):
    __tablename__ = "traffic_vehicles"

    vehicle_type: Mapped[TrafficVehicleType] = mapped_column(
        SAEnum(TrafficVehicleType, native_enum=False), nullable=False, index=True
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    speed_kmh: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_speed_kmh: Mapped[float] = mapped_column(Float, default=120.0, nullable=False)
    health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    fuel_level: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    location_x: Mapped[float] = mapped_column(Float, nullable=False)
    location_y: Mapped[float] = mapped_column(Float, nullable=False)
    location_z: Mapped[float] = mapped_column(Float, nullable=False)
    rotation_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    license_plate: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_routes.id", ondelete="SET NULL"), nullable=True
    )
    lane_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_lanes.id", ondelete="SET NULL"), nullable=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_zones.id", ondelete="SET NULL"), nullable=True
    )
    spawn_point_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_spawn_points.id", ondelete="SET NULL"), nullable=True
    )
    spawned_at: Mapped[str | None] = mapped_column(String(30), nullable=True)

    route: Mapped[TrafficRoute | None] = relationship("TrafficRoute", back_populates="vehicles")
    zone: Mapped[TrafficZone | None] = relationship("TrafficZone", back_populates="vehicles")
    spawn_point: Mapped[TrafficSpawnPoint | None] = relationship("TrafficSpawnPoint")
    emergency_vehicle: Mapped[TrafficEmergencyVehicle | None] = relationship("TrafficEmergencyVehicle", back_populates="vehicle", uselist=False)
    violations: Mapped[list[TrafficViolation]] = relationship("TrafficViolation", back_populates="vehicle")

    __table_args__ = (
        {"comment": "Active traffic vehicles — position, speed, route assignment"},
    )


# ── Traffic Emergency Vehicle ───────────────────────────────────────────────


class TrafficEmergencyVehicle(Base):
    __tablename__ = "traffic_emergency_vehicles"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("traffic_vehicles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    emergency_type: Mapped[EmergencyVehicleType] = mapped_column(
        SAEnum(EmergencyVehicleType, native_enum=False), nullable=False, index=True
    )
    is_active_call: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    siren_on: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    responding_to_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    responding_to_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    responding_to_z: Mapped[float | None] = mapped_column(Float, nullable=True)

    vehicle: Mapped[TrafficVehicle] = relationship("TrafficVehicle", back_populates="emergency_vehicle")

    __table_args__ = (
        {"comment": "Emergency vehicles — siren, active calls, response targets"},
    )


# ── Traffic Statistics ──────────────────────────────────────────────────────


class TrafficStatistics(Base):
    __tablename__ = "traffic_statistics"

    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_zones.id", ondelete="SET NULL"), nullable=True
    )
    total_vehicles_spawned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_vehicles_despawned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_speed_kmh: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    peak_density: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_accidents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_violations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    date_recorded: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    zone: Mapped[TrafficZone | None] = relationship("TrafficZone", back_populates="statistics")

    __table_args__ = (
        {"comment": "Traffic statistics — aggregated daily metrics per zone"},
    )


# ── Traffic Speed Limit ─────────────────────────────────────────────────────


class TrafficSpeedLimit(Base):
    __tablename__ = "traffic_speed_limits"

    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_zones.id", ondelete="SET NULL"), nullable=True
    )
    road_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    speed_limit_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    vehicle_type_restriction: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    zone: Mapped[TrafficZone | None] = relationship("TrafficZone", back_populates="speed_limits")

    __table_args__ = (
        {"comment": "Road speed limits — per zone and road segment"},
    )


# ── Traffic Violation ───────────────────────────────────────────────────────


class TrafficViolation(Base):
    __tablename__ = "traffic_violations"

    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_vehicles.id", ondelete="SET NULL"), nullable=True
    )
    player_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="SET NULL"), nullable=True
    )
    violation_type: Mapped[TrafficViolationType] = mapped_column(
        SAEnum(TrafficViolationType, native_enum=False), nullable=False, index=True
    )
    speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    speed_limit_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    fine_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("traffic_zones.id", ondelete="SET NULL"), nullable=True
    )

    vehicle: Mapped[TrafficVehicle | None] = relationship("TrafficVehicle", back_populates="violations")
    zone: Mapped[TrafficZone | None] = relationship("TrafficZone", back_populates="violations")

    __table_args__ = (
        {"comment": "Traffic violations — type, speed, fine, resolution status"},
    )


# ── Traffic Event (extended) ────────────────────────────────────────────────


class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    event_type: Mapped[TrafficEventType] = mapped_column(
        SAEnum(TrafficEventType, native_enum=False), nullable=False, index=True
    )
    location_x: Mapped[float] = mapped_column(Float, nullable=False)
    location_y: Mapped[float] = mapped_column(Float, nullable=False)
    location_z: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="low", nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reported_by_player_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        {"comment": "Traffic events — accidents, closures, emergencies"},
    )
