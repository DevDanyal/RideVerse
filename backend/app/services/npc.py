"""Business logic for the NPC system."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.npc import NpcCategory, NpcStatus, RelationshipLevel
from app.repositories.npc import NpcRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {c.value for c in NpcCategory.__members__.values()}
VALID_STATUSES = {s.value for s in NpcStatus.__members__.values()}
VALID_RELATIONSHIP_LEVELS = {r.value for r in RelationshipLevel.__members__.values()}
VALID_SCHEDULE_PERIODS = {"morning", "afternoon", "evening", "night"}
VALID_SPAWN_CONDITIONS = {"always", "day_only", "night_only", "weather", "mission", "random"}

# Reputation thresholds for relationship level transitions
RELATIONSHIP_THRESHOLDS = {
    RelationshipLevel.HOSTILE: (-100.0, -50.0),
    RelationshipLevel.UNFRIENDLY: (-50.0, -10.0),
    RelationshipLevel.NEUTRAL: (-10.0, 10.0),
    RelationshipLevel.FRIENDLY: (10.0, 50.0),
    RelationshipLevel.TRUSTED: (50.0, 80.0),
    RelationshipLevel.LOVED: (80.0, 100.0),
}

# Interaction reputation changes
INTERACTION_REPUTATION = {
    "greet": 1.0,
    "talk": 0.5,
    "shop": 2.0,
    "repair": 1.5,
    "heal": 2.0,
    "mission": 3.0,
    "attack": -10.0,
    "rob": -20.0,
    "help": 5.0,
    "thank": 2.0,
    "insult": -5.0,
}


class NpcService:
    """Business logic for NPC lifecycle, interactions, relationships, and statistics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.npc_repo = NpcRepository(session)
        self.player_repo = PlayerRepository(session)

    def _validate_category(self, category: str) -> None:
        if category not in VALID_CATEGORIES:
            raise ValidationError(
                f"Invalid category: {category}. Valid: {sorted(VALID_CATEGORIES)}"
            )

    def _validate_status(self, status: str) -> None:
        if status not in VALID_STATUSES:
            raise ValidationError(
                f"Invalid status: {status}. Valid: {sorted(VALID_STATUSES)}"
            )

    def _validate_relationship_level(self, level: str) -> None:
        if level not in VALID_RELATIONSHIP_LEVELS:
            raise ValidationError(
                f"Invalid relationship level: {level}. Valid: {sorted(VALID_RELATIONSHIP_LEVELS)}"
            )

    def _determine_relationship_level(self, score: float) -> RelationshipLevel:
        for level, (low, high) in RELATIONSHIP_THRESHOLDS.items():
            if low <= score < high:
                return level
        if score >= 100.0:
            return RelationshipLevel.LOVED
        return RelationshipLevel.HOSTILE

    def _clamp_reputation(self, score: float) -> float:
        return max(-100.0, min(100.0, score))

    # ── CRUD Operations ───────────────────────────────────────────────────

    async def create_npc(self, data: dict) -> Npc:
        category = data.get("npc_category", "")
        self._validate_category(category)

        npc = await self.npc_repo.create_npc(data)

        await self.npc_repo.create_statistics({"npc_id": npc.id})

        logger.info("NPC '%s' created with category '%s'", npc.npc_name, category)
        return await self.npc_repo.get_npc_by_id(npc.id)

    async def get_npc(self, npc_id: uuid.UUID) -> Npc:
        npc = await self.npc_repo.get_npc_by_id(npc_id)
        if not npc:
            raise NotFoundError("NPC not found")
        return npc

    async def list_npcs(
        self,
        category: str | None = None,
        status: str | None = None,
        zone: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Npc], int]:
        if category:
            self._validate_category(category)
        if status:
            self._validate_status(status)
        npcs = await self.npc_repo.get_all_npcs(category, status, zone, skip, limit)
        total = await self.npc_repo.count_npcs(category, status)
        return npcs, total

    async def update_npc(self, npc_id: uuid.UUID, data: dict) -> Npc:
        await self.get_npc(npc_id)
        if "npc_category" in data and data["npc_category"]:
            self._validate_category(data["npc_category"])
        if "npc_status" in data and data["npc_status"]:
            self._validate_status(data["npc_status"])
        await self.npc_repo.update_npc(npc_id, data)
        return await self.npc_repo.get_npc_by_id(npc_id)

    async def delete_npc(self, npc_id: uuid.UUID) -> bool:
        await self.get_npc(npc_id)
        return await self.npc_repo.soft_delete_npc(npc_id)

    # ── Schedule ──────────────────────────────────────────────────────────

    async def add_schedule(self, npc_id: uuid.UUID, data: dict) -> NpcSchedule:
        await self.get_npc(npc_id)
        data["npc_id"] = npc_id
        return await self.npc_repo.create_schedule(data)

    async def get_schedules(self, npc_id: uuid.UUID) -> list[NpcSchedule]:
        await self.get_npc(npc_id)
        return await self.npc_repo.get_schedules_for_npc(npc_id)

    async def delete_schedules(self, npc_id: uuid.UUID) -> None:
        await self.get_npc(npc_id)
        await self.npc_repo.delete_schedules_for_npc(npc_id)

    # ── Dialogue ──────────────────────────────────────────────────────────

    async def add_dialogue(self, npc_id: uuid.UUID, data: dict) -> NpcDialogue:
        await self.get_npc(npc_id)
        data["npc_id"] = npc_id
        return await self.npc_repo.create_dialogue(data)

    async def get_dialogues(self, npc_id: uuid.UUID) -> list[NpcDialogue]:
        await self.get_npc(npc_id)
        return await self.npc_repo.get_dialogues_for_npc(npc_id)

    async def get_dialogue_by_key(
        self, npc_id: uuid.UUID, dialogue_key: str
    ) -> NpcDialogue:
        dialogue = await self.npc_repo.get_dialogue_by_key(npc_id, dialogue_key)
        if not dialogue:
            raise NotFoundError(f"Dialogue '{dialogue_key}' not found for this NPC")
        return dialogue

    async def delete_dialogues(self, npc_id: uuid.UUID) -> None:
        await self.get_npc(npc_id)
        await self.npc_repo.delete_dialogues_for_npc(npc_id)

    # ── Profession ────────────────────────────────────────────────────────

    async def set_profession(self, npc_id: uuid.UUID, data: dict) -> NpcProfession:
        await self.get_npc(npc_id)
        data["npc_id"] = npc_id
        existing = await self.npc_repo.get_profession_for_npc(npc_id)
        if existing:
            return await self.npc_repo.update_profession(npc_id, data)
        return await self.npc_repo.create_profession(data)

    async def get_profession(self, npc_id: uuid.UUID) -> NpcProfession:
        await self.get_npc(npc_id)
        prof = await self.npc_repo.get_profession_for_npc(npc_id)
        if not prof:
            raise NotFoundError("NPC has no profession")
        return prof

    # ── Relationship ──────────────────────────────────────────────────────

    async def get_relationship(
        self, player_id: uuid.UUID, npc_id: uuid.UUID
    ) -> NpcRelationship:
        await self.get_npc(npc_id)
        rel = await self.npc_repo.get_relationship(player_id, npc_id)
        if not rel:
            rel = await self.npc_repo.create_relationship({
                "player_id": player_id,
                "npc_id": npc_id,
                "level": RelationshipLevel.NEUTRAL,
                "reputation_score": 0.0,
            })
        return rel

    async def get_player_relationships(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[NpcRelationship]:
        return await self.npc_repo.get_relationships_for_player(player_id, skip, limit)

    async def update_relationship(
        self, player_id: uuid.UUID, npc_id: uuid.UUID, data: dict
    ) -> NpcRelationship:
        await self.get_npc(npc_id)
        if "level" in data and data["level"]:
            self._validate_relationship_level(data["level"])
        existing = await self.npc_repo.get_relationship(player_id, npc_id)
        if not existing:
            data.setdefault("player_id", player_id)
            data.setdefault("npc_id", npc_id)
            return await self.npc_repo.create_relationship(data)

        if "reputation_score" in data and data["reputation_score"] is not None:
            new_level = self._determine_relationship_level(data["reputation_score"])
            data["level"] = new_level.value

        return await self.npc_repo.update_relationship(player_id, npc_id, data)

    # ── Interaction ───────────────────────────────────────────────────────

    async def interact(
        self,
        player_id: uuid.UUID,
        npc_id: uuid.UUID,
        interaction_type: str,
        dialogue_key: str | None = None,
        context: dict | None = None,
    ) -> dict:
        npc = await self.get_npc(npc_id)
        player = await self.player_repo.get_by_id(player_id)
        if not player:
            raise NotFoundError("Player not found")

        reputation_change = INTERACTION_REPUTATION.get(interaction_type, 0.0)
        was_positive = reputation_change >= 0

        interaction = await self.npc_repo.create_interaction({
            "player_id": player_id,
            "npc_id": npc_id,
            "interaction_type": interaction_type,
            "dialogue_key": dialogue_key,
            "context": context,
            "reputation_change": reputation_change,
            "was_positive": was_positive,
        })

        rel = await self.npc_repo.get_relationship(player_id, npc_id)
        if not rel:
            rel = await self.npc_repo.create_relationship({
                "player_id": player_id,
                "npc_id": npc_id,
                "level": RelationshipLevel.NEUTRAL,
                "reputation_score": 0.0,
            })

        new_score = self._clamp_reputation(rel.reputation_score + reputation_change)
        new_level = self._determine_relationship_level(new_score)
        await self.npc_repo.update_relationship(player_id, npc_id, {
            "reputation_score": new_score,
            "level": new_level.value,
            "total_interactions": rel.total_interactions + 1,
            "positive_interactions": rel.positive_interactions + (1 if was_positive else 0),
            "negative_interactions": rel.negative_interactions + (0 if was_positive else 1),
        })

        stats = await self.npc_repo.get_statistics(npc_id)
        if stats:
            updates: dict = {
                "total_interactions": stats.total_interactions + 1,
            }
            if interaction_type in ("greet", "talk"):
                updates["total_dialogues_spoken"] = stats.total_dialogues_spoken + 1
            if interaction_type in ("shop", "repair", "heal"):
                updates["total_services_provided"] = stats.total_services_provided + 1
            if interaction_type == "attack":
                updates["times_attacked"] = stats.times_attacked + 1
            if interaction_type == "thank":
                updates["times_thanked"] = stats.times_thanked + 1
            await self.npc_repo.update_statistics(npc_id, updates)

        dialogue = None
        if dialogue_key:
            dialogue = await self.npc_repo.get_dialogue_by_key(npc_id, dialogue_key)
        elif npc.dialogues:
            greetings = [d for d in npc.dialogues if d.is_greeting and not d.is_deleted]
            dialogue = greetings[0] if greetings else None

        return {
            "interaction": interaction,
            "reputation_change": reputation_change,
            "new_reputation_score": new_score,
            "new_relationship_level": new_level.value,
            "dialogue": dialogue,
            "message": f"Interacted with {npc.npc_name}: {interaction_type}",
        }

    async def get_interactions(
        self,
        npc_id: uuid.UUID,
        player_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[NpcInteraction], int]:
        await self.get_npc(npc_id)
        interactions = await self.npc_repo.get_interactions_for_npc(
            npc_id, player_id, skip, limit
        )
        total = await self.npc_repo.count_interactions_for_npc(npc_id, player_id)
        return interactions, total

    # ── Statistics ────────────────────────────────────────────────────────

    async def get_statistics(self, npc_id: uuid.UUID) -> NpcStatistics:
        await self.get_npc(npc_id)
        stats = await self.npc_repo.get_statistics(npc_id)
        if not stats:
            stats = await self.npc_repo.create_statistics({"npc_id": npc_id})
        return stats

    # ── Spawn Points ──────────────────────────────────────────────────────

    async def add_spawn_point(self, npc_id: uuid.UUID, data: dict) -> NpcSpawn:
        await self.get_npc(npc_id)
        data["npc_id"] = npc_id
        return await self.npc_repo.create_spawn_point(data)

    async def get_spawn_points(self, npc_id: uuid.UUID) -> list[NpcSpawn]:
        await self.get_npc(npc_id)
        return await self.npc_repo.get_spawn_points_for_npc(npc_id)

    async def get_npcs_in_zone(
        self, zone_name: str, skip: int = 0, limit: int = 50
    ) -> list[Npc]:
        return await self.npc_repo.get_npcs_in_zone(zone_name, skip, limit)

    async def delete_spawn_points(self, npc_id: uuid.UUID) -> None:
        await self.get_npc(npc_id)
        await self.npc_repo.delete_spawn_points_for_npc(npc_id)
