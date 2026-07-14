from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BankAccountResponse(BaseModel):
    """A player's bank account."""

    id: uuid.UUID
    player_id: uuid.UUID
    account_number: str
    account_type: str = "checking"
    balance: float = Field(default=0.0, ge=0)
    interest_rate: float = Field(default=0.0, ge=0, le=100, description="Annual percentage")
    is_active: bool = True
    created_at: datetime | None = None


class BankAccountCreate(BaseModel):
    """Request to create a new bank account."""

    account_type: str = Field(default="checking", min_length=1, max_length=50)
    initial_deposit: float = Field(default=0.0, ge=0)
