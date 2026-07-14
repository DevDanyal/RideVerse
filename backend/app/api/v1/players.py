"""Player profile, statistics, and settings API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.player import PlayerRepository
from app.schemas.common import SuccessResponse
from app.schemas.player import (
    PlayerProfile,
    PlayerStatisticsResponse,
    PlayerSettingsResponse,
    PlayerSettingsUpdate,
    PlayerUpdate,
)
from app.services.player import PlayerService

router = APIRouter(prefix="/players", tags=["Players"])


def _get_player_service(session: AsyncSession) -> PlayerService:
    repo = PlayerRepository(session)
    return PlayerService(repo)


# ── Profile ────────────────────────────────────────────────────────────────────


@router.get("/me", response_model=SuccessResponse[PlayerProfile])
async def get_profile(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[PlayerProfile]:
    """Get the authenticated player's profile."""
    svc = _get_player_service(session)
    profile = await svc.get_profile(account_id=__import__("uuid").UUID(current_user["sub"]))
    return SuccessResponse(
        message="Profile retrieved successfully",
        data=PlayerProfile(**profile),
    )


@router.patch("/me", response_model=SuccessResponse[PlayerProfile])
async def update_profile(
    body: PlayerUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[PlayerProfile]:
    """Update the authenticated player's profile."""
    import uuid as _uuid

    svc = _get_player_service(session)
    profile = await svc.update_profile(
        account_id=_uuid.UUID(current_user["sub"]),
        display_name=body.display_name,
    )
    return SuccessResponse(
        message="Profile updated successfully",
        data=PlayerProfile(**profile),
    )


# ── Statistics ─────────────────────────────────────────────────────────────────


@router.get("/me/statistics", response_model=SuccessResponse[PlayerStatisticsResponse])
async def get_statistics(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[PlayerStatisticsResponse]:
    """Get the authenticated player's statistics."""
    import uuid as _uuid

    svc = _get_player_service(session)
    stats = await svc.get_statistics(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Statistics retrieved successfully",
        data=PlayerStatisticsResponse(**stats),
    )


# ── Settings ───────────────────────────────────────────────────────────────────


@router.get("/me/settings", response_model=SuccessResponse[PlayerSettingsResponse])
async def get_settings(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[PlayerSettingsResponse]:
    """Get the authenticated player's settings."""
    import uuid as _uuid

    svc = _get_player_service(session)
    settings = await svc.get_settings(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Settings retrieved successfully",
        data=PlayerSettingsResponse(**settings),
    )


@router.patch("/me/settings", response_model=SuccessResponse[PlayerSettingsResponse])
async def update_settings(
    body: PlayerSettingsUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[PlayerSettingsResponse]:
    """Update the authenticated player's settings."""
    import uuid as _uuid

    svc = _get_player_service(session)
    settings_data = body.model_dump(exclude_none=True)
    settings = await svc.update_settings(
        account_id=_uuid.UUID(current_user["sub"]),
        **settings_data,
    )
    return SuccessResponse(
        message="Settings updated successfully",
        data=PlayerSettingsResponse(**settings),
    )
