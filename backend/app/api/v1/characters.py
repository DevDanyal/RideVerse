"""Character API endpoints."""
from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.character import CharacterRepository
from app.repositories.player import PlayerRepository
from app.schemas.character import (
    CharacterAppearanceResponse,
    CharacterAppearanceUpdate,
    CharacterResponse,
    CharacterUpdate,
)
from app.schemas.common import SuccessResponse
from app.services.character import CharacterService

router = APIRouter(prefix="/players/me/characters", tags=["Characters"])


def _get_character_service(session: AsyncSession) -> CharacterService:
    player_repo = PlayerRepository(session)
    character_repo = CharacterRepository(session)
    return CharacterService(player_repo, character_repo)


# ── List Characters ────────────────────────────────────────────────────────────


@router.get("", response_model=SuccessResponse[list[CharacterResponse]])
async def list_characters(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[list[CharacterResponse]]:
    """Get all characters belonging to the authenticated player."""
    svc = _get_character_service(session)
    characters = await svc.get_characters(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Characters retrieved successfully",
        data=[CharacterResponse(**c) for c in characters],
    )


# ── Get Character ──────────────────────────────────────────────────────────────


@router.get("/{character_id}", response_model=SuccessResponse[CharacterResponse])
async def get_character(
    character_id: _uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[CharacterResponse]:
    """Get a specific character by ID."""
    svc = _get_character_service(session)
    character = await svc.get_character(
        account_id=_uuid.UUID(current_user["sub"]),
        character_id=character_id,
    )
    return SuccessResponse(
        message="Character retrieved successfully",
        data=CharacterResponse(**character),
    )


# ── Update Character ───────────────────────────────────────────────────────────


@router.patch("/{character_id}", response_model=SuccessResponse[CharacterResponse])
async def update_character(
    character_id: _uuid.UUID,
    body: CharacterUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[CharacterResponse]:
    """Update character fields."""
    svc = _get_character_service(session)
    update_data = body.model_dump(exclude_none=True)
    character = await svc.update_character(
        account_id=_uuid.UUID(current_user["sub"]),
        character_id=character_id,
        **update_data,
    )
    return SuccessResponse(
        message="Character updated successfully",
        data=CharacterResponse(**character),
    )


# ── Update Appearance ──────────────────────────────────────────────────────────


@router.patch(
    "/{character_id}/appearance",
    response_model=SuccessResponse[CharacterAppearanceResponse],
)
async def update_appearance(
    character_id: _uuid.UUID,
    body: CharacterAppearanceUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[CharacterAppearanceResponse]:
    """Update character appearance."""
    svc = _get_character_service(session)
    appearance_data = body.model_dump(exclude_none=True)
    appearance = await svc.update_appearance(
        account_id=_uuid.UUID(current_user["sub"]),
        character_id=character_id,
        **appearance_data,
    )
    return SuccessResponse(
        message="Appearance updated successfully",
        data=CharacterAppearanceResponse(**appearance),
    )
