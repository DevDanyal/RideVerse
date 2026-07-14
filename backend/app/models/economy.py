from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TransactionType(StrEnum):
    EARN = "earn"
    SPEND = "spend"
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    REWARD = "reward"
    PURCHASE = "purchase"
    SALE = "sale"
    FINE = "fine"
    TAX = "tax"


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

    player: Mapped["Player"] = relationship("Player")


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
