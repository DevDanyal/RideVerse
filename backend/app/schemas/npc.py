"""Pydantic schemas for the NPC system."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── NPC Base Response ──────────────────────────────────────────────────────────


class NpcResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    npc_name: str
    npc_category: str
    npc_status: str = "idle"
    description: str | None = None
    level: int = 1
    health: int = 100
    max_health: int = 100
    spawn_location_x: float | None = None
    spawn_location_y: float | None = None
    spawn_location_z: float | None = None
    current_location_x: float | None = None
    current_location_y: float | None = None
    current_location_z: float | None = None
    home_location_x: float | None = None
    home_location_y: float | None = None
    home_location_z: float | None = None
    appearance_data: dict | None = None
    metadata_json: dict | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


# ── NPC Create / Update ───────────────────────────────────────────────────────


class NpcCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    npc_name: str = Field(..., min_length=1, max_length=100)
    npc_category: str = Field(..., description="NPC category")
    description: str | None = None
    level: int = Field(default=1, ge=1)
    health: int = Field(default=100, ge=1)
    max_health: int = Field(default=100, ge=1)
    spawn_location_x: float | None = None
    spawn_location_y: float | None = None
    spawn_location_z: float | None = None
    home_location_x: float | None = None
    home_location_y: float | None = None
    home_location_z: float | None = None
    appearance_data: dict | None = None
    metadata_json: dict | None = None


class NpcUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    npc_name: str | None = Field(default=None, min_length=1, max_length=100)
    npc_category: str | None = None
    npc_status: str | None = None
    description: str | None = None
    level: int | None = Field(default=None, ge=1)
    health: int | None = Field(default=None, ge=0)
    max_health: int | None = Field(default=None, ge=1)
    spawn_location_x: float | None = None
    spawn_location_y: float | None = None
    spawn_location_z: float | None = None
    current_location_x: float | None = None
    current_location_y: float | None = None
    current_location_z: float | None = None
    home_location_x: float | None = None
    home_location_y: float | None = None
    home_location_z: float | None = None
    appearance_data: dict | None = None
    metadata_json: dict | None = None
    is_active: bool | None = None


# ── NPC List Response ─────────────────────────────────────────────────────────


class NpcListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[NpcResponse] = Field(default_factory=list)
    total: int = 0


# ── Schedule ───────────────────────────────────────────────────────────────────


class NpcScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    npc_id: uuid.UUID
    period: str
    day_of_week: int = -1
    activity: str
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    location_name: str | None = None
    status: str = "idle"


class NpcScheduleCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    period: str = Field(..., description="Schedule period: morning, afternoon, evening, night")
    day_of_week: int = Field(default=-1, ge=-1, le=6)
    activity: str = Field(..., min_length=1, max_length=100)
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    location_name: str | None = None
    status: str = Field(default="idle")


# ── Dialogue ───────────────────────────────────────────────────────────────────


class NpcDialogueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    npc_id: uuid.UUID
    dialogue_key: str
    dialogue_text: str
    context: str | None = None
    required_relationship: str | None = None
    language: str = "en"
    is_greeting: bool = False
    is_farewell: bool = False
    is_mission: bool = False
    priority: int = 0


class NpcDialogueCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    dialogue_key: str = Field(..., min_length=1, max_length=100)
    dialogue_text: str = Field(..., min_length=1)
    context: str | None = None
    required_relationship: str | None = None
    language: str = Field(default="en", max_length=10)
    is_greeting: bool = False
    is_farewell: bool = False
    is_mission: bool = False
    priority: int = Field(default=0, ge=0)


# ── Profession ─────────────────────────────────────────────────────────────────


class NpcProfessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    npc_id: uuid.UUID
    profession_type: str
    skill_level: int = 1
    services_offered: dict | list | None = None
    service_price_multiplier: float = 1.0
    experience: int = 0
    reputation: float = 50.0
    specialty: str | None = None


class NpcProfessionCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    profession_type: str = Field(..., description="Profession category")
    skill_level: int = Field(default=1, ge=1)
    services_offered: dict | list | None = None
    service_price_multiplier: float = Field(default=1.0, gt=0)
    specialty: str | None = None


# ── Relationship ───────────────────────────────────────────────────────────────


class NpcRelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    npc_id: uuid.UUID
    level: str = "neutral"
    reputation_score: float = 0.0
    total_interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    notes: str | None = None


class NpcRelationshipUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    level: str | None = None
    reputation_score: float | None = None
    notes: str | None = None


# ── Interaction ────────────────────────────────────────────────────────────────


class NpcInteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    npc_id: uuid.UUID
    interaction_type: str
    dialogue_key: str | None = None
    context: dict | None = None
    reputation_change: float = 0.0
    was_positive: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class NpcInteractRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    npc_id: uuid.UUID
    interaction_type: str = Field(
        ..., min_length=1, max_length=50,
        description="Type: greet, talk, shop, repair, heal, mission, attack",
    )
    dialogue_key: str | None = None
    context: dict | None = None


# ── Statistics ─────────────────────────────────────────────────────────────────


class NpcStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    npc_id: uuid.UUID
    total_interactions: int = 0
    unique_players: int = 0
    total_dialogues_spoken: int = 0
    total_services_provided: int = 0
    average_rating: float = 0.0
    times_thanked: int = 0
    times_attacked: int = 0
    times_defeated: int = 0
    money_earned: float = 0.0


# ── Spawn Point ────────────────────────────────────────────────────────────────


class NpcSpawnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    npc_id: uuid.UUID
    zone_name: str
    location_x: float
    location_y: float
    location_z: float
    spawn_condition: str = "always"
    min_level: int = 1
    max_players_nearby: int = 10
    respawn_seconds: int = 300
    is_active: bool = True


class NpcSpawnCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    zone_name: str = Field(..., min_length=1, max_length=200)
    location_x: float
    location_y: float
    location_z: float
    spawn_condition: str = Field(default="always")
    min_level: int = Field(default=1, ge=1)
    max_players_nearby: int = Field(default=10, ge=1)
    respawn_seconds: int = Field(default=300, ge=0)
    is_active: bool = True
