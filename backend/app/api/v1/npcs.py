"""NPC API endpoints — full NPC system."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.common import SuccessResponse
from app.schemas.npc import (
    NpcCreateRequest,
    NpcDialogueCreateRequest,
    NpcDialogueResponse,
    NpcInteractionResponse,
    NpcInteractRequest,
    NpcListResponse,
    NpcProfessionCreateRequest,
    NpcProfessionResponse,
    NpcRelationshipResponse,
    NpcRelationshipUpdateRequest,
    NpcResponse,
    NpcScheduleCreateRequest,
    NpcScheduleResponse,
    NpcSpawnCreateRequest,
    NpcSpawnResponse,
    NpcStatisticsResponse,
    NpcUpdateRequest,
)
from app.services.npc import NpcService

router = APIRouter(prefix="/npcs", tags=["NPCs"])


def _get_npc_service(session: AsyncSession) -> NpcService:
    return NpcService(session)


# ── List NPCs ──────────────────────────────────────────────────────────────────


@router.get("/", response_model=SuccessResponse[list[NpcResponse]])
async def list_npcs(
    category: str | None = None,
    status: str | None = None,
    zone: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    npcs, total = await svc.list_npcs(category, status, zone, skip, limit)
    return SuccessResponse(
        message=f"{len(npcs)} NPCs retrieved",
        data=[NpcResponse.model_validate(n) for n in npcs],
    )


# ── NPC Details ────────────────────────────────────────────────────────────────


@router.get("/{npc_id}", response_model=SuccessResponse[NpcResponse])
async def get_npc(
    npc_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    npc = await svc.get_npc(npc_id)
    return SuccessResponse(
        message="NPC retrieved",
        data=NpcResponse.model_validate(npc),
    )


# ── Create NPC ─────────────────────────────────────────────────────────────────


@router.post("/", status_code=201)
async def create_npc(
    body: NpcCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    npc = await svc.create_npc(body.model_dump())
    return SuccessResponse(
        message="NPC created",
        data=NpcResponse.model_validate(npc),
    )


# ── Update NPC ─────────────────────────────────────────────────────────────────


@router.patch("/{npc_id}")
async def update_npc(
    npc_id: uuid.UUID,
    body: NpcUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    npc = await svc.update_npc(npc_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="NPC updated",
        data=NpcResponse.model_validate(npc),
    )


# ── Delete NPC ─────────────────────────────────────────────────────────────────


@router.delete("/{npc_id}")
async def delete_npc(
    npc_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    await svc.delete_npc(npc_id)
    return SuccessResponse(message="NPC deleted")


# ── Schedule ───────────────────────────────────────────────────────────────────


@router.get("/{npc_id}/schedules")
async def get_schedules(
    npc_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    schedules = await svc.get_schedules(npc_id)
    return SuccessResponse(
        message=f"{len(schedules)} schedules retrieved",
        data=[NpcScheduleResponse.model_validate(s) for s in schedules],
    )


@router.post("/{npc_id}/schedules", status_code=201)
async def add_schedule(
    npc_id: uuid.UUID,
    body: NpcScheduleCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    schedule = await svc.add_schedule(npc_id, body.model_dump())
    return SuccessResponse(
        message="Schedule added",
        data=NpcScheduleResponse.model_validate(schedule),
    )


# ── Dialogue ───────────────────────────────────────────────────────────────────


@router.get("/{npc_id}/dialogues")
async def get_dialogues(
    npc_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    dialogues = await svc.get_dialogues(npc_id)
    return SuccessResponse(
        message=f"{len(dialogues)} dialogues retrieved",
        data=[NpcDialogueResponse.model_validate(d) for d in dialogues],
    )


@router.post("/{npc_id}/dialogues", status_code=201)
async def add_dialogue(
    npc_id: uuid.UUID,
    body: NpcDialogueCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    dialogue = await svc.add_dialogue(npc_id, body.model_dump())
    return SuccessResponse(
        message="Dialogue added",
        data=NpcDialogueResponse.model_validate(dialogue),
    )


# ── Profession ─────────────────────────────────────────────────────────────────


@router.get("/{npc_id}/profession")
async def get_profession(
    npc_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    prof = await svc.get_profession(npc_id)
    return SuccessResponse(
        message="Profession retrieved",
        data=NpcProfessionResponse.model_validate(prof),
    )


@router.post("/{npc_id}/profession", status_code=201)
async def set_profession(
    npc_id: uuid.UUID,
    body: NpcProfessionCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    prof = await svc.set_profession(npc_id, body.model_dump())
    return SuccessResponse(
        message="Profession set",
        data=NpcProfessionResponse.model_validate(prof),
    )


# ── Interaction ────────────────────────────────────────────────────────────────


@router.post("/interact")
async def interact_with_npc(
    body: NpcInteractRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc.player_repo.get_by_account_id(account_id)
    if not player:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Player profile not found")

    result = await svc.interact(
        player.id, body.npc_id, body.interaction_type,
        body.dialogue_key, body.context,
    )

    interaction = result.pop("interaction")
    dialogue = result.pop("dialogue", None)

    return SuccessResponse(
        message=result.pop("message"),
        data={
            "interaction": NpcInteractionResponse.model_validate(interaction),
            "reputation_change": result["reputation_change"],
            "new_reputation_score": result["new_reputation_score"],
            "new_relationship_level": result["new_relationship_level"],
            "dialogue": NpcDialogueResponse.model_validate(dialogue) if dialogue else None,
        },
    )


@router.get("/{npc_id}/interactions")
async def get_npc_interactions(
    npc_id: uuid.UUID,
    player_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    interactions, total = await svc.get_interactions(npc_id, player_id, skip, limit)
    return SuccessResponse(
        message=f"{len(interactions)} interactions retrieved",
        data=[NpcInteractionResponse.model_validate(i) for i in interactions],
    )


# ── Relationship ───────────────────────────────────────────────────────────────


@router.get("/{npc_id}/relationship")
async def get_relationship(
    npc_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc.player_repo.get_by_account_id(account_id)
    if not player:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Player profile not found")

    rel = await svc.get_relationship(player.id, npc_id)
    return SuccessResponse(
        message="Relationship retrieved",
        data=NpcRelationshipResponse.model_validate(rel),
    )


@router.patch("/{npc_id}/relationship")
async def update_relationship(
    npc_id: uuid.UUID,
    body: NpcRelationshipUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc.player_repo.get_by_account_id(account_id)
    if not player:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Player profile not found")

    rel = await svc.update_relationship(player.id, npc_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Relationship updated",
        data=NpcRelationshipResponse.model_validate(rel),
    )


@router.get("/player/relationships")
async def player_relationships(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc.player_repo.get_by_account_id(account_id)
    if not player:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Player profile not found")

    rels = await svc.get_player_relationships(player.id, skip, limit)
    return SuccessResponse(
        message=f"{len(rels)} relationships retrieved",
        data=[NpcRelationshipResponse.model_validate(r) for r in rels],
    )


# ── Statistics ─────────────────────────────────────────────────────────────────


@router.get("/{npc_id}/statistics")
async def get_statistics(
    npc_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    stats = await svc.get_statistics(npc_id)
    return SuccessResponse(
        message="Statistics retrieved",
        data=NpcStatisticsResponse.model_validate(stats),
    )


# ── Spawn Points ───────────────────────────────────────────────────────────────


@router.get("/{npc_id}/spawns")
async def get_spawn_points(
    npc_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    spawns = await svc.get_spawn_points(npc_id)
    return SuccessResponse(
        message=f"{len(spawns)} spawn points retrieved",
        data=[NpcSpawnResponse.model_validate(s) for s in spawns],
    )


@router.post("/{npc_id}/spawns", status_code=201)
async def add_spawn_point(
    npc_id: uuid.UUID,
    body: NpcSpawnCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    spawn = await svc.add_spawn_point(npc_id, body.model_dump())
    return SuccessResponse(
        message="Spawn point added",
        data=NpcSpawnResponse.model_validate(spawn),
    )


@router.get("/zone/{zone_name}")
async def get_npcs_in_zone(
    zone_name: str,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_npc_service(session)
    npcs = await svc.get_npcs_in_zone(zone_name, skip, limit)
    return SuccessResponse(
        message=f"{len(npcs)} NPCs found in zone '{zone_name}'",
        data=[NpcResponse.model_validate(n) for n in npcs],
    )
