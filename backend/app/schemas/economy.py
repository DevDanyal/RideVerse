"""Pydantic schemas for the Economy system."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import SuccessResponse


# ---------------------------------------------------------------------------
# Wallet
# ---------------------------------------------------------------------------

class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    cash: float = Field(ge=0)
    bank_balance: float = Field(ge=0)
    max_cash: float = Field(ge=0)
    max_bank_balance: float = Field(ge=0)
    daily_salary: float = Field(ge=0)
    last_salary_claim: datetime | None = None
    total_earned: float = Field(ge=0)
    total_spent: float = Field(ge=0)
    last_transaction: datetime | None = None


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    transaction_type: str
    amount: float
    balance_before: float
    balance_after: float
    reference: str | None = None
    description: str | None = None
    source_player_id: uuid.UUID | None = None
    destination_player_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class TransactionListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[TransactionResponse] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Deposit / Withdraw
# ---------------------------------------------------------------------------

class DepositRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    amount: float = Field(..., gt=0)
    atm_id: uuid.UUID | None = None


class WithdrawRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    amount: float = Field(..., gt=0)
    atm_id: uuid.UUID | None = None


# ---------------------------------------------------------------------------
# Transfer
# ---------------------------------------------------------------------------

class TransferRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    target_player_id: uuid.UUID
    amount: float = Field(..., gt=0)
    description: str | None = Field(default=None, max_length=500)


class TransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    sender_balance_after: float
    receiver_balance_after: float
    amount: float
    fee: float
    message: str


# ---------------------------------------------------------------------------
# Salary
# ---------------------------------------------------------------------------

class SalaryClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    salary_amount: float
    new_cash_balance: float
    message: str


# ---------------------------------------------------------------------------
# Daily Reward
# ---------------------------------------------------------------------------

class DailyRewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    day_number: int
    reward_amount: float
    claimed: bool
    claimed_at: datetime | None = None


class DailyRewardClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    day_number: int
    reward_amount: float
    new_cash_balance: float
    streak: int
    message: str


# ---------------------------------------------------------------------------
# Business Income
# ---------------------------------------------------------------------------

class BusinessIncomeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    business_id: uuid.UUID
    amount: float = Field(..., gt=0)
    description: str | None = None


# ---------------------------------------------------------------------------
# Tax
# ---------------------------------------------------------------------------

class TaxApplyRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    rate: float = Field(..., ge=0, le=1, description="Tax rate as decimal (0.0 - 1.0)")
    description: str | None = None


# ---------------------------------------------------------------------------
# Loan (future-ready, disabled)
# ---------------------------------------------------------------------------

class LoanRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    amount: float = Field(..., gt=0)
    term_days: int = Field(default=30, ge=1, le=365)


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    message: str = "Loan system is not yet enabled"


# ---------------------------------------------------------------------------
# ATM
# ---------------------------------------------------------------------------

class ATMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    name: str
    location: str
    is_operational: bool
    daily_withdrawal_limit: float
    daily_withdrawn: float
    transaction_fee: float
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class ATMListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[ATMResponse] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Economy Summary
# ---------------------------------------------------------------------------

class EconomySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cash: float
    bank_balance: float
    total_wealth: float
    daily_salary: float
    salary_claimed_today: bool
    total_earned: float
    total_spent: float
    net_worth: float
    bank_accounts_count: int
    active_loans: float
