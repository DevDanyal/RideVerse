from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class WalletResponse(BaseModel):
    """Player wallet summary."""

    id: uuid.UUID
    player_id: uuid.UUID
    cash: float = Field(default=0.0, ge=0)
    bank_balance: float = Field(default=0.0, ge=0)
    last_transaction: datetime | None = None
