"""Economy API endpoints (wallet read-only for TASK 4)."""
from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.economy import EconomyRepository
from app.repositories.player import PlayerRepository
from app.schemas.common import SuccessResponse
from app.schemas.economy import WalletResponse
from app.services.economy import EconomyService

router = APIRouter(prefix="/players/me/economy", tags=["Economy"])


def _get_economy_service(session: AsyncSession) -> EconomyService:
    player_repo = PlayerRepository(session)
    economy_repo = EconomyRepository(session)
    return EconomyService(player_repo, economy_repo)


# ── Get Wallet ─────────────────────────────────────────────────────────────────


@router.get("/wallet", response_model=SuccessResponse[WalletResponse])
async def get_wallet(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[WalletResponse]:
    """Get the authenticated player's wallet."""
    svc = _get_economy_service(session)
    wallet = await svc.get_wallet(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Wallet retrieved successfully",
        data=WalletResponse(**wallet),
    )
