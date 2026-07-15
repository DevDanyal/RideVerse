"""Repository layer for NPC-related database operations."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.npc import (
    Npc,
    NpcDialogue,
    NpcInteraction,
    NpcProfession,
    NpcRelationship,
    NpcSchedule,
    NpcSpawn,
    NpcStatistics,
)


class NpcRepository:
    """Data-access layer for all NPC-related models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── NPC Base ────────────────────────────────────────────────────────────

    async def get_npc_by_id(self, npc_id: uuid.UUID) -> Npc | None:
        stmt = (
            select(Npc)
            .options(
                selectinload(Npc.schedules),
                selectinload(Npc.dialogues),
                selectinload(Npc.profession),
                selectinload(Npc.statistics),
                selectinload(Npc.spawn_points),
            )
            .where(Npc.id == npc_id, Npc.is_deleted.is_(False))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_npcs(
        self,
        category: str | None = None,
        status: str | None = None,
        zone: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Npc]:
        stmt = select(Npc).where(Npc.is_deleted.is_(False))
        if category:
            stmt = stmt.where(Npc.npc_category == category)
        if status:
            stmt = stmt.where(Npc.npc_status == status)
        stmt = stmt.order_by(Npc.npc_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_npcs(
        self,
        category: str | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(Npc.id)).where(Npc.is_deleted.is_(False))
        if category:
            stmt = stmt.where(Npc.npc_category == category)
        if status:
            stmt = stmt.where(Npc.npc_status == status)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_npc(self, data: dict) -> Npc:
        npc = Npc(**data)
        self._session.add(npc)
        await self._session.flush()
        return npc

    async def update_npc(self, npc_id: uuid.UUID, data: dict) -> Npc | None:
        stmt = (
            update(Npc)
            .where(Npc.id == npc_id, Npc.is_deleted.is_(False))
            .values(**data)
            .returning(Npc)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_npc(self, npc_id: uuid.UUID) -> bool:
        stmt = update(Npc).where(
            Npc.id == npc_id, Npc.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_npcs_by_category(
        self, category: str, skip: int = 0, limit: int = 50
    ) -> list[Npc]:
        stmt = (
            select(Npc)
            .where(Npc.npc_category == category, Npc.is_deleted.is_(False))
            .order_by(Npc.npc_name)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_npcs_in_zone(
        self, zone_name: str, skip: int = 0, limit: int = 50
    ) -> list[Npc]:
        stmt = (
            select(Npc)
            .join(NpcSpawn, NpcSpawn.npc_id == Npc.id)
            .where(
                NpcSpawn.zone_name == zone_name,
                NpcSpawn.is_active.is_(True),
                Npc.is_deleted.is_(False),
            )
            .order_by(Npc.npc_name)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ── Schedule ────────────────────────────────────────────────────────────

    async def get_schedules_for_npc(self, npc_id: uuid.UUID) -> list[NpcSchedule]:
        stmt = (
            select(NpcSchedule)
            .where(
                NpcSchedule.npc_id == npc_id,
                NpcSchedule.is_deleted.is_(False),
            )
            .order_by(NpcSchedule.period)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_schedule(self, data: dict) -> NpcSchedule:
        schedule = NpcSchedule(**data)
        self._session.add(schedule)
        await self._session.flush()
        return schedule

    async def delete_schedules_for_npc(self, npc_id: uuid.UUID) -> None:
        stmt = update(NpcSchedule).where(
            NpcSchedule.npc_id == npc_id,
            NpcSchedule.is_deleted.is_(False),
        ).values(is_deleted=True)
        await self._session.execute(stmt)

    # ── Dialogue ────────────────────────────────────────────────────────────

    async def get_dialogues_for_npc(self, npc_id: uuid.UUID) -> list[NpcDialogue]:
        stmt = (
            select(NpcDialogue)
            .where(
                NpcDialogue.npc_id == npc_id,
                NpcDialogue.is_deleted.is_(False),
            )
            .order_by(NpcDialogue.priority.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_dialogue_by_key(
        self, npc_id: uuid.UUID, dialogue_key: str
    ) -> NpcDialogue | None:
        stmt = select(NpcDialogue).where(
            NpcDialogue.npc_id == npc_id,
            NpcDialogue.dialogue_key == dialogue_key,
            NpcDialogue.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_dialogue(self, data: dict) -> NpcDialogue:
        dialogue = NpcDialogue(**data)
        self._session.add(dialogue)
        await self._session.flush()
        return dialogue

    async def delete_dialogues_for_npc(self, npc_id: uuid.UUID) -> None:
        stmt = update(NpcDialogue).where(
            NpcDialogue.npc_id == npc_id,
            NpcDialogue.is_deleted.is_(False),
        ).values(is_deleted=True)
        await self._session.execute(stmt)

    # ── Profession ──────────────────────────────────────────────────────────

    async def get_profession_for_npc(
        self, npc_id: uuid.UUID
    ) -> NpcProfession | None:
        stmt = select(NpcProfession).where(
            NpcProfession.npc_id == npc_id,
            NpcProfession.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_profession(self, data: dict) -> NpcProfession:
        prof = NpcProfession(**data)
        self._session.add(prof)
        await self._session.flush()
        return prof

    async def update_profession(
        self, npc_id: uuid.UUID, data: dict
    ) -> NpcProfession | None:
        stmt = (
            update(NpcProfession)
            .where(
                NpcProfession.npc_id == npc_id,
                NpcProfession.is_deleted.is_(False),
            )
            .values(**data)
            .returning(NpcProfession)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Relationship ────────────────────────────────────────────────────────

    async def get_relationship(
        self, player_id: uuid.UUID, npc_id: uuid.UUID
    ) -> NpcRelationship | None:
        stmt = select(NpcRelationship).where(
            NpcRelationship.player_id == player_id,
            NpcRelationship.npc_id == npc_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_relationships_for_player(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[NpcRelationship]:
        stmt = (
            select(NpcRelationship)
            .where(NpcRelationship.player_id == player_id)
            .order_by(NpcRelationship.reputation_score.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_relationship(self, data: dict) -> NpcRelationship:
        rel = NpcRelationship(**data)
        self._session.add(rel)
        await self._session.flush()
        return rel

    async def update_relationship(
        self, player_id: uuid.UUID, npc_id: uuid.UUID, data: dict
    ) -> NpcRelationship | None:
        stmt = (
            update(NpcRelationship)
            .where(
                NpcRelationship.player_id == player_id,
                NpcRelationship.npc_id == npc_id,
            )
            .values(**data)
            .returning(NpcRelationship)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Interaction ─────────────────────────────────────────────────────────

    async def create_interaction(self, data: dict) -> NpcInteraction:
        interaction = NpcInteraction(**data)
        self._session.add(interaction)
        await self._session.flush()
        return interaction

    async def get_interactions_for_npc(
        self,
        npc_id: uuid.UUID,
        player_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[NpcInteraction]:
        stmt = select(NpcInteraction).where(
            NpcInteraction.npc_id == npc_id,
            NpcInteraction.is_deleted.is_(False),
        )
        if player_id:
            stmt = stmt.where(NpcInteraction.player_id == player_id)
        stmt = stmt.order_by(NpcInteraction.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_interactions_for_npc(
        self, npc_id: uuid.UUID, player_id: uuid.UUID | None = None
    ) -> int:
        stmt = select(func.count(NpcInteraction.id)).where(
            NpcInteraction.npc_id == npc_id,
            NpcInteraction.is_deleted.is_(False),
        )
        if player_id:
            stmt = stmt.where(NpcInteraction.player_id == player_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_unique_player_count(self, npc_id: uuid.UUID) -> int:
        stmt = select(func.count(func.distinct(NpcInteraction.player_id))).where(
            NpcInteraction.npc_id == npc_id,
            NpcInteraction.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    # ── Statistics ──────────────────────────────────────────────────────────

    async def get_statistics(self, npc_id: uuid.UUID) -> NpcStatistics | None:
        stmt = select(NpcStatistics).where(
            NpcStatistics.npc_id == npc_id,
            NpcStatistics.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_statistics(self, data: dict) -> NpcStatistics:
        stats = NpcStatistics(**data)
        self._session.add(stats)
        await self._session.flush()
        return stats

    async def update_statistics(
        self, npc_id: uuid.UUID, data: dict
    ) -> NpcStatistics | None:
        stmt = (
            update(NpcStatistics)
            .where(
                NpcStatistics.npc_id == npc_id,
                NpcStatistics.is_deleted.is_(False),
            )
            .values(**data)
            .returning(NpcStatistics)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Spawn Points ────────────────────────────────────────────────────────

    async def get_spawn_points_for_npc(
        self, npc_id: uuid.UUID
    ) -> list[NpcSpawn]:
        stmt = (
            select(NpcSpawn)
            .where(
                NpcSpawn.npc_id == npc_id,
                NpcSpawn.is_deleted.is_(False),
            )
            .order_by(NpcSpawn.zone_name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_spawn_point(self, data: dict) -> NpcSpawn:
        spawn = NpcSpawn(**data)
        self._session.add(spawn)
        await self._session.flush()
        return spawn

    async def delete_spawn_points_for_npc(self, npc_id: uuid.UUID) -> None:
        stmt = update(NpcSpawn).where(
            NpcSpawn.npc_id == npc_id,
            NpcSpawn.is_deleted.is_(False),
        ).values(is_deleted=True)
        await self._session.execute(stmt)

    async def get_spawn_points_in_zone(
        self, zone_name: str
    ) -> list[NpcSpawn]:
        stmt = (
            select(NpcSpawn)
            .where(
                NpcSpawn.zone_name == zone_name,
                NpcSpawn.is_active.is_(True),
                NpcSpawn.is_deleted.is_(False),
            )
            .order_by(NpcSpawn.location_x)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
