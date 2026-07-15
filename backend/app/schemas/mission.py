"""Pydantic schemas for the Mission system."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import SuccessResponse


# ── Mission Objective ─────────────────────────────────────────────────────────


class MissionObjectiveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    objective_type: str
    description: str = ""
    target_value: int = Field(ge=1)
    target_location_x: float | None = None
    target_location_y: float | None = None
    target_location_z: float | None = None
    order_index: int = 0
    optional: bool = False


class MissionObjectiveCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    objective_type: str = Field(..., description="Objective type")
    description: str = ""
    target_value: int = Field(default=1, ge=1)
    target_location_x: float | None = None
    target_location_y: float | None = None
    target_location_z: float | None = None
    order_index: int = 0
    optional: bool = False


# ── Mission Response ─────────────────────────────────────────────────────────


class MissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    mission_name: str
    mission_description: str = ""
    category: str
    difficulty: str
    minimum_level: int = Field(ge=1)
    required_vehicle_type: str | None = None
    required_weapon_id: uuid.UUID | None = None
    reward_money: float = Field(ge=0, default=0.0)
    reward_xp: int = Field(ge=0, default=0)
    reward_reputation: float = Field(ge=0, default=0.0)
    reward_items: str | None = None
    reward_vehicles: str | None = None
    time_limit_seconds: int | None = None
    max_attempts: int = Field(ge=0, default=0)
    cooldown_seconds: int = Field(ge=0, default=0)
    repeatable: bool = False
    order_index: int = 0
    is_active: bool = True
    objectives: list[MissionObjectiveResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


# ── Mission List Response ────────────────────────────────────────────────────


class MissionListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[MissionResponse] = Field(default_factory=list)
    total: int = 0


# ── Mission Create / Update ──────────────────────────────────────────────────


class MissionCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_name: str = Field(..., min_length=1, max_length=200)
    mission_description: str = ""
    category: str = Field(..., description="Mission category")
    difficulty: str = Field(default="normal")
    minimum_level: int = Field(default=1, ge=1)
    required_vehicle_type: str | None = None
    required_weapon_id: uuid.UUID | None = None
    reward_money: float = Field(default=0.0, ge=0)
    reward_xp: int = Field(default=0, ge=0)
    reward_reputation: float = Field(default=0.0, ge=0)
    reward_items: str | None = None
    reward_vehicles: str | None = None
    time_limit_seconds: int | None = Field(default=None, gt=0)
    max_attempts: int = Field(default=0, ge=0)
    cooldown_seconds: int = Field(default=0, ge=0)
    repeatable: bool = False
    order_index: int = 0
    objectives: list[MissionObjectiveCreateRequest] = Field(default_factory=list)


class MissionUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_name: str | None = Field(default=None, min_length=1, max_length=200)
    mission_description: str | None = None
    category: str | None = None
    difficulty: str | None = None
    minimum_level: int | None = Field(default=None, ge=1)
    required_vehicle_type: str | None = None
    required_weapon_id: uuid.UUID | None = None
    reward_money: float | None = Field(default=None, ge=0)
    reward_xp: int | None = Field(default=None, ge=0)
    reward_reputation: float | None = Field(default=None, ge=0)
    reward_items: str | None = None
    reward_vehicles: str | None = None
    time_limit_seconds: int | None = None
    max_attempts: int | None = Field(default=None, ge=0)
    cooldown_seconds: int | None = Field(default=None, ge=0)
    repeatable: bool | None = None
    order_index: int | None = None
    is_active: bool | None = None


# ── Player Mission Progress ──────────────────────────────────────────────────


class PlayerObjectiveProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    objective_id: uuid.UUID
    current_value: int = Field(ge=0)
    completed: bool = False


class PlayerMissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    mission_id: uuid.UUID
    mission: MissionResponse | None = None
    status: str
    progress: float = Field(ge=0, le=100)
    objectives_completed: int = 0
    attempts: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    cancelled_at: datetime | None = None
    reward_claimed: bool = False
    objective_progresses: list[PlayerObjectiveProgressResponse] = Field(
        default_factory=list
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


# ── Accept Mission ───────────────────────────────────────────────────────────


class MissionAcceptRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_id: uuid.UUID


# ── Start Mission ────────────────────────────────────────────────────────────


class MissionStartRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_id: uuid.UUID


# ── Update Progress ──────────────────────────────────────────────────────────


class MissionProgressUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    objective_id: uuid.UUID
    value: int = Field(ge=0, description="Increment value to add")


# ── Complete Mission ─────────────────────────────────────────────────────────


class MissionCompleteRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_id: uuid.UUID


# ── Fail Mission ─────────────────────────────────────────────────────────────


class MissionFailRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_id: uuid.UUID
    failure_reason: str | None = Field(
        default=None,
        description="Reason: timeout, vehicle_destroyed, player_defeated, left_area",
    )


# ── Cancel Mission ───────────────────────────────────────────────────────────


class MissionCancelRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_id: uuid.UUID


# ── Claim Rewards ────────────────────────────────────────────────────────────


class MissionClaimRewardsRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_id: uuid.UUID


class MissionRewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    money_earned: float = 0.0
    xp_earned: int = 0
    reputation_earned: float = 0.0
    items_rewarded: list[str] = Field(default_factory=list)
    vehicles_rewarded: list[str] = Field(default_factory=list)
    message: str = ""


# ── Mission History ──────────────────────────────────────────────────────────


class MissionHistoryEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    mission_id: uuid.UUID
    mission_name: str = ""
    outcome: str
    completion_time_seconds: int = 0
    objectives_completed: int = 0
    objectives_total: int = 0
    money_earned: float = 0.0
    xp_earned: int = 0
    reputation_earned: float = 0.0
    failure_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class MissionHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[MissionHistoryEntryResponse] = Field(default_factory=list)
    total: int = 0


# ── Mission Statistics ───────────────────────────────────────────────────────


class MissionStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_completed: int = 0
    total_failed: int = 0
    total_cancelled: int = 0
    total_time_played_seconds: int = 0
    total_money_earned: float = 0.0
    total_xp_earned: int = 0
    longest_streak: int = 0
    current_streak: int = 0
    story_completed: int = 0
    side_completed: int = 0
    daily_completed: int = 0
    weekly_completed: int = 0
    delivery_completed: int = 0
    racing_completed: int = 0
    taxi_completed: int = 0
    police_completed: int = 0
    business_completed: int = 0


# ── Restart Mission ──────────────────────────────────────────────────────────


class MissionRestartRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mission_id: uuid.UUID
