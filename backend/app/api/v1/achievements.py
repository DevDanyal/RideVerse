"""Achievement API endpoints."""
from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.achievement import AchievementRepository
from app.repositories.player import PlayerRepository
from app.schemas.achievement import PlayerAchievementResponse
from app.schemas.common import SuccessResponse
from app.services.achievement import AchievementService

router = APIRouter(prefix="/players/me/achievements", tags=["Achievements"])


def _get_achievement_service(session: AsyncSession) -> AchievementService:
    player_repo = PlayerRepository(session)
    achievement_repo = AchievementRepository(session)
    return AchievementService(player_repo, achievement_repo)


# ── Get Player Achievements ────────────────────────────────────────────────────


@router.get("", response_model=SuccessResponse[list[PlayerAchievementResponse]])
async def get_achievements(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[list[PlayerAchievementResponse]]:
    """Get all achievements unlocked by the authenticated player."""
    svc = _get_achievement_service(session)
    achievements = await svc.get_player_achievements(
        account_id=_uuid.UUID(current_user["sub"])
    )
    return SuccessResponse(
        message="Achievements retrieved successfully",
        data=[PlayerAchievementResponse(**a) for a in achievements],
    )
