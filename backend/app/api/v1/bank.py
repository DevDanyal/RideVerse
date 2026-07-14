"""Bank account API endpoints."""
from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.bank import BankAccountRepository
from app.repositories.player import PlayerRepository
from app.schemas.bank import BankAccountResponse
from app.schemas.common import SuccessResponse
from app.services.bank import BankAccountService

router = APIRouter(prefix="/players/me/bank", tags=["Bank"])


def _get_bank_service(session: AsyncSession) -> BankAccountService:
    player_repo = PlayerRepository(session)
    bank_repo = BankAccountRepository(session)
    return BankAccountService(player_repo, bank_repo)


# ── Get Bank Accounts ──────────────────────────────────────────────────────────


@router.get("", response_model=SuccessResponse[list[BankAccountResponse]])
async def get_bank_accounts(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[list[BankAccountResponse]]:
    """Get all bank accounts belonging to the authenticated player."""
    svc = _get_bank_service(session)
    accounts = await svc.get_accounts(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Bank accounts retrieved successfully",
        data=[BankAccountResponse(**a) for a in accounts],
    )
