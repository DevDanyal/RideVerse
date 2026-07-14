from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PoliceRecord(Base):
    __tablename__ = "police_records"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    wanted_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_arrests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_fines: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_crime: Mapped[str | None] = mapped_column(String(255), nullable=True)

    player: Mapped["Player"] = relationship("Player")
    crime_history: Mapped[list[CrimeHistory]] = relationship(
        "CrimeHistory", back_populates="police_record"
    )


class CrimeHistory(Base):
    __tablename__ = "crime_history"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    fine_amount: Mapped[float] = mapped_column(Float, nullable=False)
    wanted_level: Mapped[int] = mapped_column(Integer, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    police_record_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("police_records.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    police_record: Mapped[PoliceRecord | None] = relationship(
        "PoliceRecord", back_populates="crime_history"
    )
    player: Mapped["Player"] = relationship("Player")
