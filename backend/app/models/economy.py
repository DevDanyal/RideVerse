"""Economy models — wallet, transactions, daily rewards, ATM."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TransactionType(StrEnum):
    EARN = "earn"
    SPEND = "spend"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    REWARD = "reward"
    PURCHASE = "purchase"
    SALE = "sale"
    FINE = "fine"
    TAX = "tax"
    SALARY = "salary"
    BUSINESS_INCOME = "business_income"
    LOAN = "loan"
    LOAN_REPAYMENT = "loan_repayment"
    DAILY_REWARD = "daily_reward"
    BANK_INTEREST = "bank_interest"


class Wallet(Base):
    __tablename__ = "wallets"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    cash: Mapped[float] = mapped_column(Float, default=1000.0, nullable=False)
    bank_balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_transaction: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Wallet Limits ─────────────────────────────────────────────────────
    max_cash: Mapped[float] = mapped_column(Float, default=1_000_000.0, nullable=False)
    max_bank_balance: Mapped[float] = mapped_column(
        Float, default=10_000_000.0, nullable=False
    )

    # ── Salary ────────────────────────────────────────────────────────────
    daily_salary: Mapped[float] = mapped_column(Float, default=500.0, nullable=False)
    last_salary_claim: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Lifetime Stats ────────────────────────────────────────────────────
    total_earned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    player: Mapped["Player"] = relationship("Player")


class Transaction(Base):
    __tablename__ = "transactions"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, native_enum=False), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_before: Mapped[float] = mapped_column(Float, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Transfer Tracking ─────────────────────────────────────────────────
    source_player_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
    )
    destination_player_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Anti-duplication ──────────────────────────────────────────────────
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])


class DailyReward(Base):
    __tablename__ = "daily_rewards"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_number: Mapped[int] = mapped_column(nullable=False)
    reward_amount: Mapped[float] = mapped_column(Float, nullable=False)
    claimed: Mapped[bool] = mapped_column(default=False, nullable=False)
    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    player: Mapped["Player"] = relationship("Player")


class ATM(Base):
    """Physical ATM locations in the game world."""

    __tablename__ = "atms"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    is_operational: Mapped[bool] = mapped_column(default=True, nullable=False)
    daily_withdrawal_limit: Mapped[float] = mapped_column(
        Float, default=50_000.0, nullable=False
    )
    daily_withdrawn: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_reset: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    transaction_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    __table_args__ = (
        {"comment": "ATM locations in the game world"},
    )
