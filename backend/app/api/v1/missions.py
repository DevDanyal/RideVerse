"""Mission API endpoints — full mission system."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.common import SuccessResponse
from app.schemas.mission import (
    MissionAcceptRequest,
    MissionCancelRequest,
    MissionClaimRewardsRequest,
    MissionCompleteRequest,
    MissionCreateRequest,
    MissionFailRequest,
    MissionHistoryEntryResponse,
    MissionListResponse,
    MissionProgressUpdateRequest,
    MissionResponse,
    MissionRestartRequest,
    MissionStartRequest,
    MissionStatisticsResponse,
    MissionUpdateRequest,
    PlayerMissionResponse,
    MissionRewardResponse,
)
from app.services.mission import MissionService

router = APIRouter(prefix="/missions", tags=["Missions"])


def _get_mission_service(session: AsyncSession) -> MissionService:
    return MissionService(session)


# ── List Missions ─────────────────────────────────────────────────────────────


@router.get("/", response_model=SuccessResponse[list[MissionResponse]])
async def list_missions(
    category: str | None = None,
    difficulty: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    missions, total = await svc.list_missions(category, difficulty, skip, limit)
    return SuccessResponse(
        message=f"{len(missions)} missions retrieved",
        data=[MissionResponse.model_validate(m) for m in missions],
    )


# ── Mission Details ───────────────────────────────────────────────────────────


@router.get("/{mission_id}", response_model=SuccessResponse[MissionResponse])
async def get_mission(
    mission_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    mission = await svc.get_mission(mission_id)
    return SuccessResponse(
        message="Mission retrieved",
        data=MissionResponse.model_validate(mission),
    )


# ── Accept Mission ────────────────────────────────────────────────────────────


@router.post("/accept", status_code=201)
async def accept_mission(
    body: MissionAcceptRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    pm = await svc.accept_mission(player.id, body.mission_id)
    return SuccessResponse(
        message="Mission accepted",
        data=PlayerMissionResponse.model_validate(pm),
    )


# ── Start Mission ─────────────────────────────────────────────────────────────


@router.post("/start", status_code=201)
async def start_mission(
    body: MissionStartRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    pm = await svc.start_mission(player.id, body.mission_id)
    return SuccessResponse(
        message="Mission started",
        data=PlayerMissionResponse.model_validate(pm),
    )


# ── Update Progress ───────────────────────────────────────────────────────────


@router.post("/progress")
async def update_progress(
    mission_id: uuid.UUID,
    body: MissionProgressUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    pm = await svc.update_progress(
        player.id, mission_id, body.objective_id, body.value
    )
    return SuccessResponse(
        message="Progress updated",
        data=PlayerMissionResponse.model_validate(pm),
    )


# ── Complete Mission ──────────────────────────────────────────────────────────


@router.post("/complete")
async def complete_mission(
    body: MissionCompleteRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.complete_mission(player.id, body.mission_id)
    pm = result.pop("player_mission")
    message = result.pop("message")
    return SuccessResponse(
        message=message,
        data={
            "player_mission": PlayerMissionResponse.model_validate(pm),
            **result,
        },
    )


# ── Fail Mission ──────────────────────────────────────────────────────────────


@router.post("/fail")
async def fail_mission(
    body: MissionFailRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.fail_mission(
        player.id, body.mission_id, body.failure_reason
    )
    pm = result.pop("player_mission")
    message = result.pop("message")
    return SuccessResponse(
        message=message,
        data={
            "player_mission": PlayerMissionResponse.model_validate(pm),
            **result,
        },
    )


# ── Cancel Mission ────────────────────────────────────────────────────────────


@router.post("/cancel")
async def cancel_mission(
    body: MissionCancelRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.cancel_mission(player.id, body.mission_id)
    pm = result.pop("player_mission")
    message = result.pop("message")
    return SuccessResponse(
        message=message,
        data=PlayerMissionResponse.model_validate(pm),
    )


# ── Claim Rewards ─────────────────────────────────────────────────────────────


@router.post("/claim-rewards")
async def claim_rewards(
    body: MissionClaimRewardsRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.claim_rewards(player.id, body.mission_id)
    message = result.pop("message")
    return SuccessResponse(
        message=message,
        data=MissionRewardResponse(**result),
    )


# ── Restart Mission ───────────────────────────────────────────────────────────


@router.post("/restart", status_code=201)
async def restart_mission(
    body: MissionRestartRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    pm = await svc.restart_mission(player.id, body.mission_id)
    return SuccessResponse(
        message="Mission restarted",
        data=PlayerMissionResponse.model_validate(pm),
    )


# ── Mission History ───────────────────────────────────────────────────────────


@router.get("/history/list")
async def mission_history(
    mission_id: uuid.UUID | None = None,
    outcome: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    history, total = await svc.get_history(
        player.id, mission_id, outcome, skip, limit
    )
    entries = []
    for h in history:
        mission = await svc.get_mission(h.mission_id) if h.mission_id else None
        entry = MissionHistoryEntryResponse(
            id=h.id,
            mission_id=h.mission_id,
            mission_name=mission.mission_name if mission else "",
            outcome=h.outcome,
            completion_time_seconds=h.completion_time_seconds,
            objectives_completed=h.objectives_completed,
            objectives_total=h.objectives_total,
            money_earned=h.money_earned,
            xp_earned=h.xp_earned,
            reputation_earned=h.reputation_earned,
            failure_reason=h.failure_reason,
            created_at=h.created_at,
        )
        entries.append(entry)
    return SuccessResponse(
        message=f"{len(entries)} history entries retrieved",
        data=entries,
    )


# ── Player Active Missions ───────────────────────────────────────────────────


@router.get("/player/active")
async def player_active_missions(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    active = await svc.get_active_missions(player.id)
    accepted = await svc.get_accepted_missions(player.id)
    return SuccessResponse(
        message="Active missions retrieved",
        data={
            "in_progress": [PlayerMissionResponse.model_validate(pm) for pm in active],
            "accepted": [PlayerMissionResponse.model_validate(pm) for pm in accepted],
        },
    )


# ── Player Mission Progress ──────────────────────────────────────────────────


@router.get("/player/{mission_id}/progress")
async def player_mission_progress(
    mission_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    pm = await svc.get_progress(player.id, mission_id)
    if not pm:
        return SuccessResponse(message="No progress found", data=None)
    return SuccessResponse(
        message="Progress retrieved",
        data=PlayerMissionResponse.model_validate(pm),
    )


# ── Mission Statistics ───────────────────────────────────────────────────────


@router.get("/player/statistics")
async def player_mission_statistics(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_mission_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    stats = await svc.get_statistics(player.id)
    return SuccessResponse(
        message="Statistics retrieved",
        data=MissionStatisticsResponse.model_validate(stats),
    )
