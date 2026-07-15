"""Business logic for the Mission system."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone


def _utcnow() -> datetime:
    """Return UTC now as a timezone-naive datetime for SQLite compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.mission import MissionStatus, ObjectiveType
from app.repositories.economy import EconomyRepository
from app.repositories.mission import MissionRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)

VALID_MISSION_CATEGORIES = {c.value for c in ObjectiveType.__members__.values()}  # wrong
VALID_MISSION_CATEGORIES = {
    "story", "side", "daily", "weekly", "delivery", "racing", "taxi", "police", "business",
}
VALID_DIFFICULTIES = {"easy", "normal", "hard", "expert", "legendary"}

DIFFICULTY_MULTIPLIERS = {
    "easy": 0.8,
    "normal": 1.0,
    "hard": 1.5,
    "expert": 2.0,
    "legendary": 3.0,
}

STREAK_BONUS_THRESHOLD = 3
STREAK_BONUS_XP = 50
STREAK_BONUS_MONEY = 100.0


class MissionService:
    """Business logic for mission lifecycle, progress tracking, and rewards."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.mission_repo = MissionRepository(session)
        self.player_repo = PlayerRepository(session)
        self.economy_repo = EconomyRepository(session)

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        player = await self.player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def _ensure_statistics(self, player_id: uuid.UUID):
        stats = await self.mission_repo.get_statistics(player_id)
        if not stats:
            stats = await self.mission_repo.create_statistics({"player_id": player_id})
        return stats

    def _validate_category(self, category: str) -> None:
        if category not in VALID_MISSION_CATEGORIES:
            raise ValidationError(
                f"Invalid category: {category}. Valid: {sorted(VALID_MISSION_CATEGORIES)}"
            )

    def _validate_difficulty(self, difficulty: str) -> None:
        if difficulty not in VALID_DIFFICULTIES:
            raise ValidationError(
                f"Invalid difficulty: {difficulty}. Valid: {sorted(VALID_DIFFICULTIES)}"
            )

    def _validate_status_transition(self, current: str, target: str) -> None:
        valid = {
            "available": {"accepted"},
            "accepted": {"in_progress", "cancelled"},
            "in_progress": {"completed", "failed", "paused"},
            "paused": {"in_progress", "cancelled"},
        }
        allowed = valid.get(current, set())
        if target not in allowed:
            raise ValidationError(
                f"Cannot transition from '{current}' to '{target}'"
            )

    async def _calculate_total_objectives(self, mission_id: uuid.UUID) -> int:
        objectives = await self.mission_repo.get_objectives_for_mission(mission_id)
        required = [o for o in objectives if not o.optional]
        return len(required) if required else len(objectives)

    async def _update_progress_from_objectives(
        self, player_mission_id: uuid.UUID, mission_id: uuid.UUID
    ) -> float:
        objectives = await self.mission_repo.get_objectives_for_mission(mission_id)
        if not objectives:
            return 100.0

        total = len(objectives)
        completed_count = 0
        for obj in objectives:
            progress = await self.mission_repo.get_objective_progress(
                player_mission_id, obj.id
            )
            if progress and progress.completed:
                completed_count += 1

        return round((completed_count / total) * 100.0, 2) if total > 0 else 100.0

    async def _award_rewards(
        self, player_id: uuid.UUID, mission
    ) -> dict:
        wallet = await self.economy_repo.get_wallet(player_id)
        money = mission.reward_money
        xp = mission.reward_xp
        reputation = mission.reward_reputation

        if wallet:
            wallet.cash += money
            await self.session.flush()

        player = await self.player_repo.get_by_id(player_id)
        if player:
            player.experience += xp
            player.reputation += reputation
            await self.session.flush()

        items = []
        if mission.reward_items:
            try:
                items = json.loads(mission.reward_items)
            except (json.JSONDecodeError, TypeError):
                items = []

        vehicles = []
        if mission.reward_vehicles:
            try:
                vehicles = json.loads(mission.reward_vehicles)
            except (json.JSONDecodeError, TypeError):
                vehicles = []

        return {
            "money_earned": money,
            "xp_earned": xp,
            "reputation_earned": reputation,
            "items_rewarded": items,
            "vehicles_rewarded": vehicles,
        }

    async def _update_statistics(
        self, player_id: uuid.UUID, category: str, outcome: str, time_seconds: int
    ) -> None:
        stats = await self._ensure_statistics(player_id)

        updates: dict = {}
        if outcome == "completed":
            updates["total_completed"] = stats.total_completed + 1
            updates["total_time_played_seconds"] = (
                stats.total_time_played_seconds + time_seconds
            )
            cat_key = f"{category}_completed"
            if hasattr(stats, cat_key):
                current = getattr(stats, cat_key)
                setattr(stats, cat_key, current + 1)
            updates["current_streak"] = stats.current_streak + 1
            if stats.current_streak + 1 > stats.longest_streak:
                updates["longest_streak"] = stats.current_streak + 1
        elif outcome == "failed":
            updates["total_failed"] = stats.total_failed + 1
            updates["current_streak"] = 0
        elif outcome == "cancelled":
            updates["total_cancelled"] = stats.total_cancelled + 1
            updates["current_streak"] = 0

        if updates:
            await self.mission_repo.update_statistics(player_id, updates)

    # ── CRUD Operations ───────────────────────────────────────────────────

    async def create_mission(self, data: dict) -> Mission:
        category = data.get("category", "")
        difficulty = data.get("difficulty", "normal")
        self._validate_category(category)
        self._validate_difficulty(difficulty)

        objectives_data = data.pop("objectives", [])

        mission = await self.mission_repo.create_mission(data)

        for idx, obj_data in enumerate(objectives_data):
            obj_data["mission_id"] = mission.id
            if "order_index" not in obj_data:
                obj_data["order_index"] = idx
            await self.mission_repo.create_objective(obj_data)

        return await self.mission_repo.get_mission_by_id(mission.id)

    async def get_mission(self, mission_id: uuid.UUID) -> Mission:
        mission = await self.mission_repo.get_mission_by_id(mission_id)
        if not mission:
            raise NotFoundError("Mission not found")
        return mission

    async def list_missions(
        self,
        category: str | None = None,
        difficulty: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Mission], int]:
        if category:
            self._validate_category(category)
        if difficulty:
            self._validate_difficulty(difficulty)
        missions = await self.mission_repo.get_all_missions(
            category, difficulty, skip, limit
        )
        total = await self.mission_repo.count_missions(category, difficulty)
        return missions, total

    async def update_mission(self, mission_id: uuid.UUID, data: dict) -> Mission:
        mission = await self.get_mission(mission_id)
        if "category" in data and data["category"]:
            self._validate_category(data["category"])
        if "difficulty" in data and data["difficulty"]:
            self._validate_difficulty(data["difficulty"])
        updated = await self.mission_repo.update_mission(mission_id, data)
        return updated

    async def delete_mission(self, mission_id: uuid.UUID) -> bool:
        await self.get_mission(mission_id)
        return await self.mission_repo.soft_delete_mission(mission_id)

    # ── Accept Mission ────────────────────────────────────────────────────

    async def accept_mission(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> PlayerMission:
        mission = await self.get_mission(mission_id)

        player = await self.player_repo.get_by_id(player_id)
        if player and player.level < mission.minimum_level:
            raise ValidationError(
                f"Required level: {mission.minimum_level}, your level: {player.level}"
            )

        existing = await self.mission_repo.get_player_mission(player_id, mission_id)
        if existing:
            if existing.status in ("accepted", "in_progress"):
                raise ConflictError("Mission already active")
            if existing.status == "completed" and not mission.repeatable:
                raise ConflictError("Mission already completed and not repeatable")

        if not mission.repeatable and existing and existing.status == "completed":
            raise ConflictError("Mission already completed")

        if existing:
            await self.mission_repo.update_player_mission(
                existing.id,
                {
                    "status": MissionStatus.ACCEPTED,
                    "progress": 0.0,
                    "objectives_completed": 0,
                    "started_at": None,
                    "completed_at": None,
                    "failed_at": None,
                    "cancelled_at": None,
                    "reward_claimed": False,
                },
            )
            await self.mission_repo.delete_objectives_for_mission(mission_id)
            pm = await self.mission_repo.get_player_mission(player_id, mission_id)
            return pm

        pm = await self.mission_repo.create_player_mission({
            "player_id": player_id,
            "mission_id": mission_id,
            "status": MissionStatus.ACCEPTED,
        })

        objectives = await self.mission_repo.get_objectives_for_mission(mission_id)
        for obj in objectives:
            await self.mission_repo.create_objective_progress({
                "player_mission_id": pm.id,
                "objective_id": obj.id,
                "current_value": 0,
                "completed": False,
            })

        return await self.mission_repo.get_player_mission(player_id, mission_id)

    # ── Start Mission ─────────────────────────────────────────────────────

    async def start_mission(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> PlayerMission:
        pm = await self.mission_repo.get_player_mission(player_id, mission_id)
        if not pm:
            raise NotFoundError("Mission not accepted yet. Accept it first.")
        if pm.status != MissionStatus.ACCEPTED:
            raise ValidationError(
                f"Cannot start mission in '{pm.status}' status. Must be 'accepted'."
            )

        mission = await self.get_mission(mission_id)

        if mission.max_attempts > 0 and pm.attempts >= mission.max_attempts:
            raise ValidationError(
                f"Max attempts ({mission.max_attempts}) reached for this mission"
            )

        if pm.next_available_at and pm.next_available_at > _utcnow():
            raise ValidationError(
                f"Mission on cooldown until {pm.next_available_at.isoformat()}"
            )

        updates: dict = {
            "status": MissionStatus.IN_PROGRESS,
            "started_at": _utcnow(),
            "attempts": pm.attempts + 1,
        }
        await self.mission_repo.update_player_mission(pm.id, updates)

        return await self.mission_repo.get_player_mission(player_id, mission_id)

    # ── Update Progress ───────────────────────────────────────────────────

    async def update_progress(
        self,
        player_id: uuid.UUID,
        mission_id: uuid.UUID,
        objective_id: uuid.UUID,
        increment: int,
    ) -> PlayerMission:
        pm = await self.mission_repo.get_player_mission(player_id, mission_id)
        if not pm:
            raise NotFoundError("Mission not in progress")
        if pm.status != MissionStatus.IN_PROGRESS:
            raise ValidationError("Mission is not in progress")

        obj_progress = await self.mission_repo.get_objective_progress(
            pm.id, objective_id
        )
        if not obj_progress:
            raise NotFoundError("Objective progress not found for this mission")

        obj = await self.mission_repo.get_mission_by_id(mission_id)
        if not obj:
            raise NotFoundError("Mission definition not found")

        objectives = await self.mission_repo.get_objectives_for_mission(mission_id)
        target_obj = None
        for o in objectives:
            if o.id == objective_id:
                target_obj = o
                break

        if not target_obj:
            raise NotFoundError("Objective does not belong to this mission")

        new_value = obj_progress.current_value + increment
        completed = new_value >= target_obj.target_value

        await self.mission_repo.update_objective_progress(
            obj_progress.id,
            {
                "current_value": min(new_value, target_obj.target_value),
                "completed": completed,
            },
        )

        new_progress = await self._update_progress_from_objectives(pm.id, mission_id)
        completed_count = 0
        all_progresses = await self.mission_repo.get_all_objective_progresses(pm.id)
        for op in all_progresses:
            if op.completed:
                completed_count += 1

        await self.mission_repo.update_player_mission(
            pm.id,
            {"progress": new_progress, "objectives_completed": completed_count},
        )

        return await self.mission_repo.get_player_mission(player_id, mission_id)

    # ── Complete Mission ──────────────────────────────────────────────────

    async def complete_mission(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> dict:
        pm = await self.mission_repo.get_player_mission(player_id, mission_id)
        if not pm:
            raise NotFoundError("Mission not found for this player")
        if pm.status != MissionStatus.IN_PROGRESS:
            raise ValidationError("Mission is not in progress")

        mission = await self.get_mission(mission_id)

        now = _utcnow()
        completion_time = 0
        if pm.started_at:
            started = pm.started_at.replace(tzinfo=None) if pm.started_at.tzinfo else pm.started_at
            completion_time = int((now - started).total_seconds())

        await self.mission_repo.update_player_mission(
            pm.id,
            {
                "status": MissionStatus.COMPLETED,
                "progress": 100.0,
                "completed_at": now,
                "last_completed_at": now,
            },
        )

        reward_data = await self._award_rewards(player_id, mission)

        total_obj_count = await self._calculate_total_objectives(mission_id)
        await self.mission_repo.create_history({
            "player_id": player_id,
            "mission_id": mission_id,
            "outcome": "completed",
            "completion_time_seconds": completion_time,
            "objectives_completed": pm.objectives_completed,
            "objectives_total": total_obj_count,
            "money_earned": reward_data["money_earned"],
            "xp_earned": reward_data["xp_earned"],
            "reputation_earned": reward_data["reputation_earned"],
        })

        await self._update_statistics(
            player_id, mission.category, "completed", completion_time
        )

        if mission.cooldown_seconds > 0:
            from datetime import timedelta
            next_available = now + timedelta(seconds=mission.cooldown_seconds)
            existing_cd = await self.mission_repo.get_cooldown(player_id, mission_id)
            if existing_cd:
                await self.mission_repo.update_cooldown(
                    existing_cd.id,
                    {
                        "last_completed_at": now,
                        "next_available_at": next_available,
                    },
                )
            else:
                await self.mission_repo.create_cooldown({
                    "player_id": player_id,
                    "mission_id": mission_id,
                    "last_completed_at": now,
                    "next_available_at": next_available,
                })

        logger.info(
            "Mission %s completed by player %s: +%s money, +%s xp",
            mission_id,
            player_id,
            reward_data["money_earned"],
            reward_data["xp_earned"],
        )

        return {
            "player_mission": await self.mission_repo.get_player_mission(
                player_id, mission_id
            ),
            **reward_data,
            "message": f"Mission '{mission.mission_name}' completed!",
        }

    # ── Fail Mission ──────────────────────────────────────────────────────

    async def fail_mission(
        self,
        player_id: uuid.UUID,
        mission_id: uuid.UUID,
        failure_reason: str | None = None,
    ) -> dict:
        pm = await self.mission_repo.get_player_mission(player_id, mission_id)
        if not pm:
            raise NotFoundError("Mission not found for this player")
        if pm.status != MissionStatus.IN_PROGRESS:
            raise ValidationError("Mission is not in progress")

        mission = await self.get_mission(mission_id)
        now = _utcnow()

        await self.mission_repo.update_player_mission(
            pm.id,
            {
                "status": MissionStatus.FAILED,
                "failed_at": now,
            },
        )

        completion_time = 0
        if pm.started_at:
            started = pm.started_at.replace(tzinfo=None) if pm.started_at.tzinfo else pm.started_at
            completion_time = int((now - started).total_seconds())

        total_obj_count = await self._calculate_total_objectives(mission_id)
        await self.mission_repo.create_history({
            "player_id": player_id,
            "mission_id": mission_id,
            "outcome": "failed",
            "completion_time_seconds": completion_time,
            "objectives_completed": pm.objectives_completed,
            "objectives_total": total_obj_count,
            "failure_reason": failure_reason,
        })

        await self._update_statistics(
            player_id, mission.category, "failed", completion_time
        )

        if mission.cooldown_seconds > 0:
            from datetime import timedelta
            next_available = now + timedelta(seconds=mission.cooldown_seconds)
            existing_cd = await self.mission_repo.get_cooldown(player_id, mission_id)
            if existing_cd:
                await self.mission_repo.update_cooldown(
                    existing_cd.id,
                    {
                        "last_completed_at": now,
                        "next_available_at": next_available,
                    },
                )
            else:
                await self.mission_repo.create_cooldown({
                    "player_id": player_id,
                    "mission_id": mission_id,
                    "last_completed_at": now,
                    "next_available_at": next_available,
                })

        logger.info(
            "Mission %s failed by player %s: %s",
            mission_id,
            player_id,
            failure_reason,
        )

        return {
            "player_mission": await self.mission_repo.get_player_mission(
                player_id, mission_id
            ),
            "failure_reason": failure_reason,
            "message": f"Mission '{mission.mission_name}' failed.",
        }

    # ── Cancel Mission ────────────────────────────────────────────────────

    async def cancel_mission(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> dict:
        pm = await self.mission_repo.get_player_mission(player_id, mission_id)
        if not pm:
            raise NotFoundError("Mission not found for this player")
        if pm.status not in (MissionStatus.ACCEPTED, MissionStatus.IN_PROGRESS, MissionStatus.PAUSED):
            raise ValidationError(
                f"Cannot cancel mission in '{pm.status}' status"
            )

        mission = await self.get_mission(mission_id)
        now = _utcnow()

        await self.mission_repo.update_player_mission(
            pm.id,
            {
                "status": MissionStatus.CANCELLED,
                "cancelled_at": now,
            },
        )

        total_obj_count = await self._calculate_total_objectives(mission_id)
        await self.mission_repo.create_history({
            "player_id": player_id,
            "mission_id": mission_id,
            "outcome": "cancelled",
            "completion_time_seconds": 0,
            "objectives_completed": pm.objectives_completed,
            "objectives_total": total_obj_count,
        })

        await self._update_statistics(player_id, mission.category, "cancelled", 0)

        logger.info("Mission %s cancelled by player %s", mission_id, player_id)

        return {
            "player_mission": await self.mission_repo.get_player_mission(
                player_id, mission_id
            ),
            "message": f"Mission '{mission.mission_name}' cancelled.",
        }

    # ── Claim Rewards ─────────────────────────────────────────────────────

    async def claim_rewards(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> dict:
        pm = await self.mission_repo.get_player_mission(player_id, mission_id)
        if not pm:
            raise NotFoundError("Mission not found for this player")
        if pm.status != MissionStatus.COMPLETED:
            raise ValidationError("Mission is not completed")
        if pm.reward_claimed:
            raise ConflictError("Rewards already claimed")

        mission = await self.get_mission(mission_id)
        reward_data = await self._award_rewards(player_id, mission)

        await self.mission_repo.update_player_mission(
            pm.id, {"reward_claimed": True}
        )

        logger.info(
            "Rewards claimed for mission %s by player %s",
            mission_id,
            player_id,
        )

        return {
            **reward_data,
            "message": "Rewards claimed successfully",
        }

    # ── Restart Mission ───────────────────────────────────────────────────

    async def restart_mission(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> PlayerMission:
        pm = await self.mission_repo.get_player_mission(player_id, mission_id)
        if not pm:
            raise NotFoundError("Mission not found for this player")

        mission = await self.get_mission(mission_id)

        if pm.status not in (
            MissionStatus.COMPLETED,
            MissionStatus.FAILED,
            MissionStatus.CANCELLED,
        ):
            raise ValidationError(
                f"Cannot restart mission in '{pm.status}' status"
            )

        if not mission.repeatable and pm.status == MissionStatus.COMPLETED:
            raise ValidationError("Mission is not repeatable and already completed")

        pm = await self.accept_mission(player_id, mission_id)
        pm = await self.start_mission(player_id, mission_id)

        logger.info("Mission %s restarted by player %s", mission_id, player_id)
        return pm

    # ── Get Progress ──────────────────────────────────────────────────────

    async def get_progress(
        self, player_id: uuid.UUID, mission_id: uuid.UUID
    ) -> PlayerMission | None:
        pm = await self.mission_repo.get_player_mission(player_id, mission_id)
        return pm

    # ── Get History ───────────────────────────────────────────────────────

    async def get_history(
        self,
        player_id: uuid.UUID,
        mission_id: uuid.UUID | None = None,
        outcome: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[MissionHistory], int]:
        history = await self.mission_repo.get_player_history(
            player_id, mission_id, outcome, skip, limit
        )
        total = await self.mission_repo.count_player_history(player_id, outcome)
        return history, total

    # ── Get Statistics ────────────────────────────────────────────────────

    async def get_statistics(self, player_id: uuid.UUID) -> MissionStatistics:
        stats = await self.mission_repo.get_statistics(player_id)
        if not stats:
            stats = await self.mission_repo.create_statistics({"player_id": player_id})
        return stats

    # ── Get Active Missions ───────────────────────────────────────────────

    async def get_active_missions(self, player_id: uuid.UUID) -> list[PlayerMission]:
        return await self.mission_repo.get_player_missions(
            player_id, status=MissionStatus.IN_PROGRESS
        )

    async def get_accepted_missions(self, player_id: uuid.UUID) -> list[PlayerMission]:
        return await self.mission_repo.get_player_missions(
            player_id, status=MissionStatus.ACCEPTED
        )
