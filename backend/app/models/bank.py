"""Bank account model — checking, savings, and loan support."""
from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AccountType(StrEnum):
    CHECKING = "checking"
    SAVINGS = "savings"


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    account_type: Mapped[AccountType] = mapped_column(
        SAEnum(AccountType, native_enum=False),
        default=AccountType.CHECKING,
        nullable=False,
    )
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Float, default=0.01, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # ── Overdraft ─────────────────────────────────────────────────────────
    overdraft_limit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # ── Loan (future-ready, disabled by default) ──────────────────────────
    loan_enabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    loan_balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    loan_interest_rate: Mapped[float] = mapped_column(Float, default=0.05, nullable=False)
    loan_max_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    loan_term_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    # ── Tax (future-ready) ────────────────────────────────────────────────
    tax_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # ── Limits ────────────────────────────────────────────────────────────
    daily_transfer_limit: Mapped[float] = mapped_column(
        Float, default=100_000.0, nullable=False
    )
    daily_transferred: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    player: Mapped["Player"] = relationship("Player", back_populates="bank_accounts")

    __table_args__ = (
        {"comment": "Bank accounts for players"},
    )
