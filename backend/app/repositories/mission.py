"""Repository layer for mission-related database operations."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.mission import (
    Mission,
    MissionCooldown,
    MissionHistory,
    MissionObjective,
    MissionStatistics,
    MissionStatus,
    PlayerMission,
    PlayerObjectiveProgress,
)


class MissionRepository:
    """Data-access layer for all mission-related models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Mission Definition ────────────────────────────────────────────────

    async def get_mission_by_id(self, mission_id: uuid.UUID) -> Mission | None:
        stmt = (
            select(Mission)
            .options(selectinload(Mission.objectives))
            .where(Mission.id == mission_id, Mission.is_deleted.is_(False))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_missions(
        self,
        category: str | None = None,
        difficulty: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Mission]:
        stmt = (
            select(Mission)
            .options(selectinload(Mission.objectives))
            .where(Mission.is_deleted.is_(False))
        )
        if category:
            stmt = stmt.where(Mission.category == category)
        if difficulty:
            stmt = stmt.where(Mission.difficulty == difficulty)
        stmt = stmt.order_by(Mission.order_index).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_mission(self, data: dict) -> Mission:
        mission = Mission(**data)
        self._session.add(mission)
        await self._session.flush()
        return mission

    async def update_mission(
        self, mission_id: uuid.UUID, data: dict
    ) -> Mission | None:
        stmt = (
            update(Mission)
            .where(Mission.id == mission_id, Mission.is_deleted.is_(False))
            .values(**data)
            .returning(Mission)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_mission(self, mission_id: uuid.UUID) -> bool:
        stmt = update(Mission).where(
            Mission.id == mission_id, Mission.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def count_missions(
        self, category: str | None = None, difficulty: str | None = None
    ) -> int:
        stmt = select(func.count(Mission.id)).where(Mission.is_deleted.is_(False))
        if category:
            stmt = stmt.where(Mission.category == category)
        if difficulty:
            stmt = stmt.where(Mission.difficulty == difficulty)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    # ── Mission Objective ─────────────────────────────────────────────────

    async def create_objective(self, data: dict) -> MissionObjective:
        obj = MissionObjective(**data)
        self._session.add(obj)
        await self._session.flush()
        return obj

    async def get_objectives_for_mission(
        self, mission_id: uuid.UUID
    ) -> list[MissionObjective]:
        stmt = (
            select(MissionObjective)
            .where(
                MissionObjective.mission_id == mission_id,
                MissionObjective.is_deleted.is_(False),
            )
            .order_by(MissionObjective.order_index)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_objectives_for_mission(self, mission_id: uuid.UUID) -> None:
        stmt = update(MissionObjective).where(
            MissionObjective.mission_id == mission_id,
            MissionObjective.is_deleted.is_(False),
        ).values(is_deleted=True)
        await self._session.execute(stmt)

    # ── Player Mission ────────────────────────────────────────────────────

    async def get_player_mission(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> PlayerMission | None:
        stmt = (
            select(PlayerMission)
            .options(
                selectinload(PlayerMission.mission).selectinload(Mission.objectives),
                selectinload(PlayerMission.objective_progresses),
            )
            .where(
                PlayerMission.player_id == player_id,
                PlayerMission.mission_id == mission_id,
                PlayerMission.is_deleted.is_(False),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_player_mission_by_id(
        self, player_mission_id: uuid.UUID
    ) -> PlayerMission | None:
        stmt = (
            select(PlayerMission)
            .options(
                selectinload(PlayerMission.mission).selectinload(Mission.objectives),
                selectinload(PlayerMission.objective_progresses),
            )
            .where(
                PlayerMission.id == player_mission_id,
                PlayerMission.is_deleted.is_(False),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_player_missions(
        self,
        player_id: uuid.UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PlayerMission]:
        stmt = (
            select(PlayerMission)
            .options(
                selectinload(PlayerMission.mission).selectinload(Mission.objectives),
                selectinload(PlayerMission.objective_progresses),
            )
            .where(
                PlayerMission.player_id == player_id,
                PlayerMission.is_deleted.is_(False),
            )
        )
        if status:
            stmt = stmt.where(PlayerMission.status == status)
        stmt = stmt.order_by(PlayerMission.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_player_missions(
        self, player_id: uuid.UUID, status: str | None = None
    ) -> int:
        stmt = select(func.count(PlayerMission.id)).where(
            PlayerMission.player_id == player_id,
            PlayerMission.is_deleted.is_(False),
        )
        if status:
            stmt = stmt.where(PlayerMission.status == status)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_player_mission(self, data: dict) -> PlayerMission:
        pm = PlayerMission(**data)
        self._session.add(pm)
        await self._session.flush()
        return pm

    async def update_player_mission(
        self, player_mission_id: uuid.UUID, data: dict
    ) -> PlayerMission | None:
        stmt = (
            update(PlayerMission)
            .where(
                PlayerMission.id == player_mission_id,
                PlayerMission.is_deleted.is_(False),
            )
            .values(**data)
            .returning(PlayerMission)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Player Objective Progress ─────────────────────────────────────────

    async def get_objective_progress(
        self, player_mission_id: uuid.UUID, objective_id: uuid.UUID
    ) -> PlayerObjectiveProgress | None:
        stmt = select(PlayerObjectiveProgress).where(
            PlayerObjectiveProgress.player_mission_id == player_mission_id,
            PlayerObjectiveProgress.objective_id == objective_id,
            PlayerObjectiveProgress.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_objective_progresses(
        self, player_mission_id: uuid.UUID
    ) -> list[PlayerObjectiveProgress]:
        stmt = select(PlayerObjectiveProgress).where(
            PlayerObjectiveProgress.player_mission_id == player_mission_id,
            PlayerObjectiveProgress.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_objective_progress(self, data: dict) -> PlayerObjectiveProgress:
        op = PlayerObjectiveProgress(**data)
        self._session.add(op)
        await self._session.flush()
        return op

    async def update_objective_progress(
        self, progress_id: uuid.UUID, data: dict
    ) -> PlayerObjectiveProgress | None:
        stmt = (
            update(PlayerObjectiveProgress)
            .where(
                PlayerObjectiveProgress.id == progress_id,
                PlayerObjectiveProgress.is_deleted.is_(False),
            )
            .values(**data)
            .returning(PlayerObjectiveProgress)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Mission History ───────────────────────────────────────────────────

    async def create_history(self, data: dict) -> MissionHistory:
        history = MissionHistory(**data)
        self._session.add(history)
        await self._session.flush()
        return history

    async def get_player_history(
        self,
        player_id: uuid.UUID,
        mission_id: uuid.UUID | None = None,
        outcome: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[MissionHistory]:
        stmt = select(MissionHistory).where(
            MissionHistory.player_id == player_id,
            MissionHistory.is_deleted.is_(False),
        )
        if mission_id:
            stmt = stmt.where(MissionHistory.mission_id == mission_id)
        if outcome:
            stmt = stmt.where(MissionHistory.outcome == outcome)
        stmt = stmt.order_by(MissionHistory.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_player_history(
        self, player_id: uuid.UUID, outcome: str | None = None
    ) -> int:
        stmt = select(func.count(MissionHistory.id)).where(
            MissionHistory.player_id == player_id,
            MissionHistory.is_deleted.is_(False),
        )
        if outcome:
            stmt = stmt.where(MissionHistory.outcome == outcome)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    # ── Mission Cooldown ──────────────────────────────────────────────────

    async def get_cooldown(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> MissionCooldown | None:
        stmt = select(MissionCooldown).where(
            MissionCooldown.player_id == player_id,
            MissionCooldown.mission_id == mission_id,
            MissionCooldown.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_cooldown(self, data: dict) -> MissionCooldown:
        cd = MissionCooldown(**data)
        self._session.add(cd)
        await self._session.flush()
        return cd

    async def update_cooldown(
        self, cooldown_id: uuid.UUID, data: dict
    ) -> MissionCooldown | None:
        stmt = (
            update(MissionCooldown)
            .where(
                MissionCooldown.id == cooldown_id,
                MissionCooldown.is_deleted.is_(False),
            )
            .values(**data)
            .returning(MissionCooldown)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Mission Statistics ────────────────────────────────────────────────

    async def get_statistics(self, player_id: uuid.UUID) -> MissionStatistics | None:
        stmt = select(MissionStatistics).where(
            MissionStatistics.player_id == player_id,
            MissionStatistics.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_statistics(self, data: dict) -> MissionStatistics:
        stats = MissionStatistics(**data)
        self._session.add(stats)
        await self._session.flush()
        return stats

    async def update_statistics(
        self, player_id: uuid.UUID, data: dict
    ) -> MissionStatistics | None:
        stmt = (
            update(MissionStatistics)
            .where(
                MissionStatistics.player_id == player_id,
                MissionStatistics.is_deleted.is_(False),
            )
            .values(**data)
            .returning(MissionStatistics)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
