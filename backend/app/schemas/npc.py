from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NpcType(str, Enum):
    SHOPKEEPER = "shopkeeper"
    QUEST_GIVER = "quest_giver"
    CIVILIAN = "civilian"
    POLICE = "police"
    MECHANIC = "mechanic"
    BANKER = "banker"
    DRIVING_INSTRUCTOR = "driving_instructor"
    VENDOR = "vendor"


class NpcResponse(BaseModel):
    """NPC data returned to clients."""

    id: uuid.UUID
    name: str
    type: NpcType
    location: str
    is_interactive: bool = True
    dialogue_id: uuid.UUID | None = None
    spawn_x: float = 0.0
    spawn_y: float = 0.0
    spawn_z: float = 0.0
    created_at: datetime | None = None


class NpcDialogueLine(BaseModel):
    """A single line of NPC dialogue."""

    id: uuid.UUID
    text: str
    responses: list[str] = Field(default_factory=list)
    next_dialogue_id: uuid.UUID | None = None


class NpcDialogueResponse(BaseModel):
    """NPC dialogue tree."""

    npc_id: uuid.UUID
    dialogues: list[NpcDialogueLine] = Field(default_factory=list)


class InteractRequest(BaseModel):
    """Request to interact with an NPC."""

    npc_id: uuid.UUID
    action: str = Field(..., min_length=1, max_length=64, description="Interaction action name")
