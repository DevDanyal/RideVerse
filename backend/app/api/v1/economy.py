"""Economy API endpoints — wallet, transfers, salary, daily rewards, ATMs, transactions."""
from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.common import SuccessResponse
from app.schemas.economy import (
    ATMListResponse,
    ATMResponse,
    BusinessIncomeRequest,
    DailyRewardClaimResponse,
    DailyRewardResponse,
    DepositRequest,
    EconomySummaryResponse,
    LoanRequest,
    LoanResponse,
    SalaryClaimResponse,
    TaxApplyRequest,
    TransactionListResponse,
    TransactionResponse,
    TransferRequest,
    TransferResponse,
    WalletResponse,
    WithdrawRequest,
)
from app.services.economy import EconomyService

router = APIRouter(prefix="/players/me/economy", tags=["Economy"])


def _get_economy_service(session: AsyncSession) -> EconomyService:
    return EconomyService(session)


# ── Wallet ─────────────────────────────────────────────────────────────────────


@router.get("/wallet", response_model=SuccessResponse[WalletResponse])
async def get_wallet(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    wallet = await svc.get_wallet(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Wallet retrieved successfully",
        data=WalletResponse(**wallet),
    )


# ── Summary ────────────────────────────────────────────────────────────────────


@router.get("/summary", response_model=SuccessResponse[EconomySummaryResponse])
async def get_economy_summary(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    summary = await svc.get_economy_summary(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Economy summary retrieved",
        data=EconomySummaryResponse(**summary),
    )


# ── Deposit / Withdraw ─────────────────────────────────────────────────────────


@router.post("/deposit")
async def deposit(
    body: DepositRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    result = await svc.deposit(
        account_id=_uuid.UUID(current_user["sub"]),
        amount=body.amount,
        atm_id=body.atm_id,
    )
    return SuccessResponse(message="Deposit successful", data=result)


@router.post("/withdraw")
async def withdraw(
    body: WithdrawRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    result = await svc.withdraw(
        account_id=_uuid.UUID(current_user["sub"]),
        amount=body.amount,
        atm_id=body.atm_id,
    )
    return SuccessResponse(message="Withdrawal successful", data=result)


# ── Transfer ───────────────────────────────────────────────────────────────────


@router.post("/transfer", response_model=SuccessResponse[TransferResponse])
async def transfer(
    body: TransferRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    result = await svc.transfer(
        account_id=_uuid.UUID(current_user["sub"]),
        target_player_id=body.target_player_id,
        amount=body.amount,
        description=body.description,
    )
    return SuccessResponse(
        message="Transfer successful",
        data=TransferResponse(**result),
    )


# ── Salary ─────────────────────────────────────────────────────────────────────


@router.post("/salary", response_model=SuccessResponse[SalaryClaimResponse])
async def claim_salary(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    result = await svc.claim_salary(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Salary claimed",
        data=SalaryClaimResponse(**result),
    )


# ── Daily Rewards ──────────────────────────────────────────────────────────────


@router.get("/daily-rewards", response_model=SuccessResponse[list[DailyRewardResponse]])
async def get_daily_rewards(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    rewards = await svc.get_daily_reward_status(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Daily reward status retrieved",
        data=[DailyRewardResponse(**r) for r in rewards],
    )


@router.post("/daily-rewards/claim", response_model=SuccessResponse[DailyRewardClaimResponse])
async def claim_daily_reward(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    result = await svc.claim_daily_reward(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Daily reward claimed",
        data=DailyRewardClaimResponse(**result),
    )


# ── Transactions ───────────────────────────────────────────────────────────────


@router.get("/transactions", response_model=SuccessResponse[TransactionListResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    txs = await svc.get_transaction_history(
        account_id=_uuid.UUID(current_user["sub"]),
        skip=skip,
        limit=limit,
    )
    return SuccessResponse(
        message="Transactions retrieved",
        data=TransactionListResponse(
            data=[TransactionResponse.model_validate(tx) for tx in txs],
            total=len(txs),
        ),
    )


@router.get("/transactions/{transaction_type}", response_model=SuccessResponse[TransactionListResponse])
async def get_transactions_by_type(
    transaction_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    txs = await svc.get_transactions_by_type(
        account_id=_uuid.UUID(current_user["sub"]),
        transaction_type=transaction_type,
        skip=skip,
        limit=limit,
    )
    return SuccessResponse(
        message=f"Transactions of type '{transaction_type}' retrieved",
        data=TransactionListResponse(
            data=[TransactionResponse.model_validate(tx) for tx in txs],
            total=len(txs),
        ),
    )


# ── ATMs ───────────────────────────────────────────────────────────────────────


@router.get("/atms", response_model=SuccessResponse[ATMListResponse])
async def get_atms(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    atms = await svc.get_atms()
    return SuccessResponse(
        message="ATMs retrieved",
        data=ATMListResponse(
            data=[ATMResponse.model_validate(a) for a in atms],
        ),
    )


# ── Tax (future-ready) ─────────────────────────────────────────────────────────


@router.post("/tax")
async def apply_tax(
    body: TaxApplyRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    result = await svc.apply_tax(
        account_id=_uuid.UUID(current_user["sub"]),
        rate=body.rate,
        description=body.description,
    )
    return SuccessResponse(message="Tax applied", data=result)


# ── Loan (disabled) ────────────────────────────────────────────────────────────


@router.post("/loan", response_model=SuccessResponse[LoanResponse])
async def request_loan(
    body: LoanRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    result = await svc.request_loan(
        account_id=_uuid.UUID(current_user["sub"]),
        amount=body.amount,
        term_days=body.term_days,
    )
    return SuccessResponse(message="Loan request", data=LoanResponse(**result))


@router.post("/loan/repay", response_model=SuccessResponse[LoanResponse])
async def repay_loan(
    body: LoanRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_economy_service(session)
    result = await svc.repay_loan(
        account_id=_uuid.UUID(current_user["sub"]),
        amount=body.amount,
    )
    return SuccessResponse(message="Loan repay", data=LoanResponse(**result))
