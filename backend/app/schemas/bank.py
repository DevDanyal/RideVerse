"""Pydantic schemas for the Bank system."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BankAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    player_id: uuid.UUID
    account_number: str
    account_type: str
    balance: float = Field(ge=0)
    interest_rate: float = Field(ge=0, le=100)
    is_active: bool = True
    overdraft_limit: float = Field(ge=0)
    loan_enabled: bool = False
    loan_balance: float = Field(ge=0)
    loan_interest_rate: float = Field(ge=0, le=100)
    loan_max_amount: float = Field(ge=0)
    loan_term_days: int
    tax_rate: float = Field(ge=0, le=1)
    daily_transfer_limit: float = Field(ge=0)
    daily_transferred: float = Field(ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class BankAccountCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    account_type: str = Field(default="checking", min_length=1, max_length=50)
    initial_deposit: float = Field(default=0.0, ge=0)


class BankAccountListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = True
    message: str = "OK"
    data: list[BankAccountResponse] = Field(default_factory=list)
    total: int = 0
