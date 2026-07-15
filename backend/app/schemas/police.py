"""Pydantic schemas for the Police system."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Police Officer ─────────────────────────────────────────────────────────────


class PoliceOfficerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    badge_number: str
    rank: str = "cadet"
    status: str = "off_duty"
    department: str = "city_police"
    station_id: uuid.UUID | None = None
    hire_date: str | None = None
    years_of_service: int = 0
    total_arrests: int = 0
    total_fines_issued: float = 0.0
    total_crimes_resolved: int = 0
    reputation: float = 50.0
    notes: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class PoliceOfficerCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_id: uuid.UUID
    badge_number: str = Field(..., min_length=1, max_length=50)
    rank: str = Field(default="cadet")
    department: str = Field(default="city_police")
    station_id: uuid.UUID | None = None
    hire_date: str | None = None


class PoliceOfficerUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    rank: str | None = None
    status: str | None = None
    department: str | None = None
    station_id: uuid.UUID | None = None
    years_of_service: int | None = None
    reputation: float | None = None
    notes: str | None = None
    is_active: bool | None = None


class PoliceOfficerListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[PoliceOfficerResponse] = Field(default_factory=list)
    total: int = 0


# ── Police Station ────────────────────────────────────────────────────────────


class PoliceStationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    station_name: str
    department: str = "city_police"
    address: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    max_officers: int = 50
    current_officers: int = 0
    has_jail: bool = True
    has_holding_cell: bool = True
    has_evidence_room: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class PoliceStationCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    station_name: str = Field(..., min_length=1, max_length=200)
    department: str = Field(default="city_police")
    address: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    max_officers: int = Field(default=50, ge=1)
    has_jail: bool = True
    has_holding_cell: bool = True
    has_evidence_room: bool = False


class PoliceStationUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    station_name: str | None = Field(default=None, min_length=1, max_length=200)
    department: str | None = None
    address: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    max_officers: int | None = Field(default=None, ge=1)
    has_jail: bool | None = None
    has_holding_cell: bool | None = None
    has_evidence_room: bool | None = None
    is_active: bool | None = None


class PoliceStationListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[PoliceStationResponse] = Field(default_factory=list)
    total: int = 0


# ── Crime ─────────────────────────────────────────────────────────────────────


class CrimeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    crime_type: str
    wanted_level: int = 1
    fine_amount: float = 0.0
    description: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    location_name: str | None = None
    reporting_officer_id: uuid.UUID | None = None
    is_witnessed: bool = False
    is_resolved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class CrimeCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_id: uuid.UUID
    crime_type: str = Field(..., description="Type of crime committed")
    wanted_level: int = Field(default=1, ge=0, le=6)
    fine_amount: float = Field(default=0.0, ge=0)
    description: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    location_name: str | None = None
    reporting_officer_id: uuid.UUID | None = None
    is_witnessed: bool = False


class CrimeUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    wanted_level: int | None = Field(default=None, ge=0, le=6)
    fine_amount: float | None = Field(default=None, ge=0)
    description: str | None = None
    is_witnessed: bool | None = None
    is_resolved: bool | None = None


class CrimeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[CrimeResponse] = Field(default_factory=list)
    total: int = 0


# ── Wanted Level ──────────────────────────────────────────────────────────────


class WantedLevelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    current_level: int = 0
    previous_level: int = 0
    reason: str | None = None
    police_response: str | None = None
    bounty_amount: float = 0.0
    last_crime_id: uuid.UUID | None = None
    first_offense_at: str | None = None
    last_escalation_at: str | None = None
    cooldown_seconds: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class WantedLevelUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    current_level: int = Field(..., ge=0, le=6)
    reason: str | None = None
    crime_id: uuid.UUID | None = None


class WantedLevelSetRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_id: uuid.UUID
    current_level: int = Field(..., ge=0, le=6)
    reason: str | None = None


# ── Arrest ────────────────────────────────────────────────────────────────────


class ArrestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    officer_id: uuid.UUID
    crime_id: uuid.UUID
    status: str = "pending"
    wanted_level_at_arrest: int = 0
    fine_amount: float = 0.0
    notes: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class ArrestCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    player_id: uuid.UUID
    officer_id: uuid.UUID
    crime_id: uuid.UUID
    wanted_level_at_arrest: int = Field(..., ge=0, le=6)
    fine_amount: float = Field(default=0.0, ge=0)
    notes: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None


class ArrestUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    status: str | None = None
    fine_amount: float | None = Field(default=None, ge=0)
    notes: str | None = None


class ArrestListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[ArrestResponse] = Field(default_factory=list)
    total: int = 0


# ── Fine ──────────────────────────────────────────────────────────────────────


class FineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    arrest_id: uuid.UUID
    player_id: uuid.UUID
    amount: float
    reason: str
    status: str = "pending"
    due_date: str | None = None
    paid_at: str | None = None
    waived_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class FineCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    arrest_id: uuid.UUID
    player_id: uuid.UUID
    amount: float = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=500)
    due_date: str | None = None


class FinePayRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    pass


class FineWaiveRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    waived_reason: str = Field(..., min_length=1, max_length=500)


class FineListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[FineResponse] = Field(default_factory=list)
    total: int = 0


# ── Jail ──────────────────────────────────────────────────────────────────────


class JailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    arrest_id: uuid.UUID
    player_id: uuid.UUID
    sentence_seconds: int
    status: str = "serving"
    sentence_start: str | None = None
    sentence_end: str | None = None
    released_at: str | None = None
    release_reason: str | None = None
    cell_number: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class JailCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    arrest_id: uuid.UUID
    player_id: uuid.UUID
    sentence_seconds: int = Field(..., gt=0)
    cell_number: int | None = None


class JailReleaseRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    release_reason: str = Field(default="Sentence completed")


class JailListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[JailResponse] = Field(default_factory=list)
    total: int = 0


# ── Crime Report ──────────────────────────────────────────────────────────────


class CrimeReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    crime_id: uuid.UUID
    reporter_player_id: uuid.UUID
    description: str
    status: str = "filed"
    assigned_officer_id: uuid.UUID | None = None
    resolution_notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class CrimeReportCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    crime_id: uuid.UUID
    reporter_player_id: uuid.UUID
    description: str = Field(..., min_length=1)


class CrimeReportUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    status: str | None = None
    assigned_officer_id: uuid.UUID | None = None
    resolution_notes: str | None = None


class CrimeReportListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[CrimeReportResponse] = Field(default_factory=list)
    total: int = 0


# ── Dispatch ──────────────────────────────────────────────────────────────────


class DispatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    crime_id: uuid.UUID
    officer_id: uuid.UUID | None = None
    priority: str = "medium"
    status: str = "pending"
    message: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class DispatchCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    crime_id: uuid.UUID
    officer_id: uuid.UUID | None = None
    priority: str = Field(default="medium")
    message: str | None = None
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None


class DispatchUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    officer_id: uuid.UUID | None = None
    status: str | None = None
    priority: str | None = None
    message: str | None = None


class DispatchListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[DispatchResponse] = Field(default_factory=list)
    total: int = 0


# ── Police Record ─────────────────────────────────────────────────────────────


class PoliceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    wanted_level: int = 0
    total_arrests: int = 0
    total_fines: float = 0.0
    last_crime: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class PoliceRecordListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[PoliceRecordResponse] = Field(default_factory=list)
    total: int = 0


# ── Crime History ─────────────────────────────────────────────────────────────


class CrimeHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    crime_type: str
    fine_amount: float
    wanted_level: int
    resolved: bool = False
    police_record_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class CrimeHistoryListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[CrimeHistoryResponse] = Field(default_factory=list)
    total: int = 0


# ── Police Equipment ──────────────────────────────────────────────────────────


class PoliceEquipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    officer_id: uuid.UUID
    equipment_type: str
    name: str
    serial_number: str | None = None
    is_issued: bool = True
    condition: str = "good"
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class PoliceEquipmentCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    equipment_type: str = Field(..., description="Type of equipment")
    name: str = Field(..., min_length=1, max_length=100)
    serial_number: str | None = None
    is_issued: bool = True
    condition: str = Field(default="good", max_length=50)
    notes: str | None = None


class PoliceEquipmentUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    is_issued: bool | None = None
    condition: str | None = None
    notes: str | None = None


class PoliceEquipmentListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[PoliceEquipmentResponse] = Field(default_factory=list)
    total: int = 0


# ── Police Vehicle ────────────────────────────────────────────────────────────


class PoliceVehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    officer_id: uuid.UUID | None = None
    vehicle_type: str
    model_name: str
    call_sign: str | None = None
    license_plate: str | None = None
    department: str = "city_police"
    is_active: bool = True
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    fuel_level: float = 100.0
    health: int = 100
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class PoliceVehicleCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vehicle_type: str = Field(..., description="Type of police vehicle")
    model_name: str = Field(..., min_length=1, max_length=100)
    call_sign: str | None = None
    license_plate: str | None = None
    department: str = Field(default="city_police")
    officer_id: uuid.UUID | None = None


class PoliceVehicleUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    officer_id: uuid.UUID | None = None
    is_active: bool | None = None
    fuel_level: float | None = Field(default=None, ge=0, le=100)
    health: int | None = Field(default=None, ge=0, le=100)
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None


class PoliceVehicleListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[PoliceVehicleResponse] = Field(default_factory=list)
    total: int = 0
