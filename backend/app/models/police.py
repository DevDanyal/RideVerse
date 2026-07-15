"""Police system models — officers, stations, crimes, wanted levels, arrests, fines, jail, reports, dispatch, records, equipment, vehicles."""
from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum, Float, ForeignKey, Integer, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# ── Enums ──────────────────────────────────────────────────────────────────────


class OfficerRank(StrEnum):
    CADET = "cadet"
    PATROL_OFFICER = "patrol_officer"
    SERGEANT = "sergeant"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    DEPUTY_CHIEF = "deputy_chief"
    CHIEF = "chief"


class OfficerStatus(StrEnum):
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"


class DepartmentType(StrEnum):
    CITY_POLICE = "city_police"
    HIGHWAY_PATROL = "highway_patrol"
    TRAFFIC_POLICE = "traffic_police"
    SPECIAL_RESPONSE = "special_response"


class CrimeType(StrEnum):
    SPEEDING = "speeding"
    DANGEROUS_DRIVING = "dangerous_driving"
    HIT_AND_RUN = "hit_and_run"
    VEHICLE_THEFT = "vehicle_theft"
    PROPERTY_DAMAGE = "property_damage"
    WEAPON_POSSESSION = "weapon_possession"
    ASSAULT = "assault"
    ROBBERY = "robbery"
    BUSINESS_THEFT = "business_theft"
    ILLEGAL_RACING = "illegal_racing"
    POLICE_ASSAULT = "police_assault"
    MURDER = "murder"


class WantedLevelValue(StrEnum):
    NONE = "none"
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    LEVEL_4 = "level_4"
    LEVEL_5 = "level_5"
    LEVEL_6 = "level_6"


class ArrestStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"


class FineStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    WAIVED = "waived"
    CONTESTED = "contested"


class JailStatus(StrEnum):
    SERVING = "serving"
    RELEASED = "released"
    ESCAPED = "escaped"
    PARDONED = "pardoned"


class ReportStatus(StrEnum):
    FILED = "filed"
    UNDER_INVESTIGATION = "under_investigation"
    CLOSED = "closed"
    DISMISSED = "dismissed"


class DispatchPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DispatchStatus(StrEnum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EquipmentType(StrEnum):
    PISTOL = "pistol"
    SHOTGUN = "shotgun"
    SMG = "smg"
    ASSAULT_RIFLE = "assault_rifle"
    TASER = "taser"
    FLASHLIGHT = "flashlight"
    HANDCUFFS = "handcuffs"
    BATON = "baton"
    BODY_ARMOR = "body_armor"
    RADIO = "radio"


class PoliceVehicleType(StrEnum):
    POLICE_BIKE = "police_bike"
    POLICE_CAR = "police_car"
    SUV = "suv"
    ARMORED = "armored"


# ── Police Officer ─────────────────────────────────────────────────────────────


class PoliceOfficer(Base):
    __tablename__ = "police_officers"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    badge_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    rank: Mapped[OfficerRank] = mapped_column(
        SAEnum(OfficerRank, native_enum=False), default=OfficerRank.CADET, nullable=False
    )
    status: Mapped[OfficerStatus] = mapped_column(
        SAEnum(OfficerStatus, native_enum=False), default=OfficerStatus.OFF_DUTY, nullable=False
    )
    department: Mapped[DepartmentType] = mapped_column(
        SAEnum(DepartmentType, native_enum=False), default=DepartmentType.CITY_POLICE, nullable=False
    )
    station_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("police_stations.id", ondelete="SET NULL"), nullable=True
    )
    hire_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    years_of_service: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_arrests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_fines_issued: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_crimes_resolved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reputation: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    station: Mapped[PoliceStation | None] = relationship("PoliceStation", back_populates="officers")
    arrests: Mapped[list[Arrest]] = relationship("Arrest", back_populates="officer", cascade="all, delete-orphan")
    dispatches: Mapped[list[Dispatch]] = relationship("Dispatch", back_populates="officer", cascade="all, delete-orphan")
    equipment: Mapped[list[PoliceEquipment]] = relationship("PoliceEquipment", back_populates="officer", cascade="all, delete-orphan")
    vehicles: Mapped[list[PoliceVehicle]] = relationship("PoliceVehicle", back_populates="officer", cascade="all, delete-orphan")
    crimes_reported: Mapped[list[Crime]] = relationship("Crime", back_populates="reporting_officer", foreign_keys="Crime.reporting_officer_id")

    __table_args__ = (
        {"comment": "Police officers — badge, rank, department, station assignment"},
    )


# ── Police Station ────────────────────────────────────────────────────────────


class PoliceStation(Base):
    __tablename__ = "police_stations"

    station_name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[DepartmentType] = mapped_column(
        SAEnum(DepartmentType, native_enum=False), default=DepartmentType.CITY_POLICE, nullable=False
    )
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_officers: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    current_officers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    has_jail: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_holding_cell: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_evidence_room: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    officers: Mapped[list[PoliceOfficer]] = relationship("PoliceOfficer", back_populates="station")

    __table_args__ = (
        {"comment": "Police stations — locations, capacity, facilities"},
    )


# ── Crime ─────────────────────────────────────────────────────────────────────


class Crime(Base):
    __tablename__ = "police_crimes"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crime_type: Mapped[CrimeType] = mapped_column(
        SAEnum(CrimeType, native_enum=False), nullable=False, index=True
    )
    wanted_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    fine_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reporting_officer_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("police_officers.id", ondelete="SET NULL"), nullable=True
    )
    is_witnessed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    reporting_officer: Mapped[PoliceOfficer | None] = relationship("PoliceOfficer", back_populates="crimes_reported", foreign_keys=[reporting_officer_id])
    arrests: Mapped[list[Arrest]] = relationship("Arrest", back_populates="crime")

    __table_args__ = (
        {"comment": "Crimes committed by players — type, location, severity"},
    )


# ── Wanted Level ──────────────────────────────────────────────────────────────


class WantedLevel(Base):
    __tablename__ = "police_wanted_levels"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    current_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    previous_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    police_response: Mapped[str | None] = mapped_column(String(200), nullable=True)
    bounty_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_crime_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("police_crimes.id", ondelete="SET NULL"), nullable=True
    )
    first_offense_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    last_escalation_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        {"comment": "Player wanted levels — 0–6 star system, response tiers"},
    )


# ── Arrest ────────────────────────────────────────────────────────────────────


class Arrest(Base):
    __tablename__ = "police_arrests"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    officer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_officers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crime_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_crimes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ArrestStatus] = mapped_column(
        SAEnum(ArrestStatus, native_enum=False), default=ArrestStatus.PENDING, nullable=False
    )
    wanted_level_at_arrest: Mapped[int] = mapped_column(Integer, nullable=False)
    fine_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_z: Mapped[float | None] = mapped_column(Float, nullable=True)

    officer: Mapped[PoliceOfficer] = relationship("PoliceOfficer", back_populates="arrests")
    crime: Mapped[Crime] = relationship("Crime", back_populates="arrests")
    fine: Mapped[Fine | None] = relationship("Fine", back_populates="arrest", uselist=False)
    jail: Mapped[Jail | None] = relationship("Jail", back_populates="arrest", uselist=False)

    __table_args__ = (
        {"comment": "Arrests — officer, player, crime, outcome"},
    )


# ── Fine ──────────────────────────────────────────────────────────────────────


class Fine(Base):
    __tablename__ = "police_fines"

    arrest_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_arrests.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[FineStatus] = mapped_column(
        SAEnum(FineStatus, native_enum=False), default=FineStatus.PENDING, nullable=False
    )
    due_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    paid_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    waived_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    arrest: Mapped[Arrest] = relationship("Arrest", back_populates="fine")

    __table_args__ = (
        {"comment": "Fines — amount, reason, payment status"},
    )


# ── Jail ──────────────────────────────────────────────────────────────────────


class Jail(Base):
    __tablename__ = "police_jail"

    arrest_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_arrests.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sentence_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[JailStatus] = mapped_column(
        SAEnum(JailStatus, native_enum=False), default=JailStatus.SERVING, nullable=False
    )
    sentence_start: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sentence_end: Mapped[str | None] = mapped_column(String(30), nullable=True)
    released_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    release_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cell_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    arrest: Mapped[Arrest] = relationship("Arrest", back_populates="jail")

    __table_args__ = (
        {"comment": "Jail sentences — duration, status, release"},
    )


# ── Crime Report ──────────────────────────────────────────────────────────────


class CrimeReport(Base):
    __tablename__ = "police_crime_reports"

    crime_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_crimes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reporter_player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        SAEnum(ReportStatus, native_enum=False), default=ReportStatus.FILED, nullable=False
    )
    assigned_officer_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("police_officers.id", ondelete="SET NULL"), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        {"comment": "Crime reports — filed by players, assigned to officers"},
    )


# ── Dispatch ──────────────────────────────────────────────────────────────────


class Dispatch(Base):
    __tablename__ = "police_dispatches"

    crime_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_crimes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    officer_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_officers.id", ondelete="SET NULL"),
        nullable=True,
    )
    priority: Mapped[DispatchPriority] = mapped_column(
        SAEnum(DispatchPriority, native_enum=False), default=DispatchPriority.MEDIUM, nullable=False
    )
    status: Mapped[DispatchStatus] = mapped_column(
        SAEnum(DispatchStatus, native_enum=False), default=DispatchStatus.PENDING, nullable=False
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_z: Mapped[float | None] = mapped_column(Float, nullable=True)

    crime: Mapped[Crime] = relationship("Crime")
    officer: Mapped[PoliceOfficer | None] = relationship("PoliceOfficer", back_populates="dispatches")

    __table_args__ = (
        {"comment": "Dispatch calls — priority, status, officer assignment"},
    )


# ── Police Equipment ──────────────────────────────────────────────────────────


class PoliceEquipment(Base):
    __tablename__ = "police_equipment"

    officer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_officers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    equipment_type: Mapped[EquipmentType] = mapped_column(
        SAEnum(EquipmentType, native_enum=False), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    is_issued: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    condition: Mapped[str] = mapped_column(String(50), default="good", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    officer: Mapped[PoliceOfficer] = relationship("PoliceOfficer", back_populates="equipment")

    __table_args__ = (
        {"comment": "Police equipment — issued gear per officer"},
    )


# ── Police Vehicle ────────────────────────────────────────────────────────────


class PoliceVehicle(Base):
    __tablename__ = "police_vehicles"

    officer_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_officers.id", ondelete="SET NULL"),
        nullable=True,
    )
    vehicle_type: Mapped[PoliceVehicleType] = mapped_column(
        SAEnum(PoliceVehicleType, native_enum=False), nullable=False, index=True
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    call_sign: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    license_plate: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    department: Mapped[DepartmentType] = mapped_column(
        SAEnum(DepartmentType, native_enum=False), default=DepartmentType.CITY_POLICE, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    fuel_level: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    officer: Mapped[PoliceOfficer | None] = relationship("PoliceOfficer", back_populates="vehicles")

    __table_args__ = (
        {"comment": "Police vehicles — patrol cars, SUVs, bikes"},
    )


# ── Police Record ─────────────────────────────────────────────────────────────


class PoliceRecord(Base):
    __tablename__ = "police_records"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    wanted_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_arrests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_fines: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_crime: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        {"comment": "Player criminal record — wanted level, arrest count, fines"},
    )


# ── Crime History ─────────────────────────────────────────────────────────────


class CrimeHistory(Base):
    __tablename__ = "crime_history"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    fine_amount: Mapped[float] = mapped_column(Float, nullable=False)
    wanted_level: Mapped[int] = mapped_column(Integer, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    police_record_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_records.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        {"comment": "Crime history records for players"},
    )
