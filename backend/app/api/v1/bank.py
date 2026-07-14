"""Bank account API endpoints — list, create, deposit, withdraw, close."""
from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.bank import BankAccountCreate, BankAccountResponse
from app.schemas.common import SuccessResponse
from app.services.bank import BankAccountService

router = APIRouter(prefix="/players/me/bank", tags=["Bank"])


def _get_bank_service(session: AsyncSession) -> BankAccountService:
    return BankAccountService(session)


# ── List ───────────────────────────────────────────────────────────────────────


@router.get("", response_model=SuccessResponse[list[BankAccountResponse]])
async def get_bank_accounts(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bank_service(session)
    accounts = await svc.get_accounts(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Bank accounts retrieved successfully",
        data=[BankAccountResponse.model_validate(a) for a in accounts],
    )


# ── Create ─────────────────────────────────────────────────────────────────────


@router.post("", status_code=201, response_model=SuccessResponse[BankAccountResponse])
async def create_bank_account(
    body: BankAccountCreate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bank_service(session)
    account = await svc.create_account(
        account_id=_uuid.UUID(current_user["sub"]),
        account_type=body.account_type,
        initial_deposit=body.initial_deposit,
    )
    return SuccessResponse(
        message="Bank account created",
        data=BankAccountResponse.model_validate(account),
    )


# ── Deposit ────────────────────────────────────────────────────────────────────


@router.post("/{bank_account_id}/deposit")
async def deposit_to_account(
    bank_account_id: _uuid.UUID,
    amount: float,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bank_service(session)
    result = await svc.deposit_to_account(
        account_id=_uuid.UUID(current_user["sub"]),
        bank_account_id=bank_account_id,
        amount=amount,
    )
    return SuccessResponse(message="Deposit successful", data=result)


# ── Withdraw ───────────────────────────────────────────────────────────────────


@router.post("/{bank_account_id}/withdraw")
async def withdraw_from_account(
    bank_account_id: _uuid.UUID,
    amount: float,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bank_service(session)
    result = await svc.withdraw_from_account(
        account_id=_uuid.UUID(current_user["sub"]),
        bank_account_id=bank_account_id,
        amount=amount,
    )
    return SuccessResponse(message="Withdrawal successful", data=result)


# ── Close ──────────────────────────────────────────────────────────────────────


@router.delete("/{bank_account_id}")
async def close_account(
    bank_account_id: _uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bank_service(session)
    result = await svc.close_account(
        account_id=_uuid.UUID(current_user["sub"]),
        bank_account_id=bank_account_id,
    )
    return SuccessResponse(message=result["message"], data=result)
