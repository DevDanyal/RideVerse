"""Business logic for the Police system."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.police import (
    ArrestStatus,
    CrimeType,
    Crime as CrimeModel,
    DepartmentType,
    Dispatch,
    DispatchPriority,
    DispatchStatus,
    EquipmentType,
    Fine,
    FineStatus,
    Jail,
    JailStatus,
    OfficerRank,
    OfficerStatus,
    PoliceEquipment,
    PoliceOfficer,
    PoliceStation,
    PoliceVehicle,
    PoliceVehicleType,
    ReportStatus,
    WantedLevel,
    WantedLevelValue,
)
from app.repositories.police import PoliceRepository
from app.repositories.player import PlayerRepository

logger = logging.getLogger(__name__)

VALID_DEPARTMENTS = {d.value for d in DepartmentType.__members__.values()}
VALID_OFFICER_RANKS = {r.value for r in OfficerRank.__members__.values()}
VALID_OFFICER_STATUSES = {s.value for s in OfficerStatus.__members__.values()}
VALID_CRIME_TYPES = {c.value for c in CrimeType.__members__.values()}
VALID_ARREST_STATUSES = {a.value for a in ArrestStatus.__members__.values()}
VALID_FINE_STATUSES = {f.value for f in FineStatus.__members__.values()}
VALID_JAIL_STATUSES = {j.value for j in JailStatus.__members__.values()}
VALID_REPORT_STATUSES = {r.value for r in ReportStatus.__members__.values()}
VALID_DISPATCH_PRIORITIES = {p.value for p in DispatchPriority.__members__.values()}
VALID_DISPATCH_STATUSES = {s.value for s in DispatchStatus.__members__.values()}
VALID_EQUIPMENT_TYPES = {e.value for e in EquipmentType.__members__.values()}
VALID_VEHICLE_TYPES = {v.value for v in PoliceVehicleType.__members__.values()}

# Fine amounts by crime type
CRIME_FINE_AMOUNTS: dict[str, float] = {
    CrimeType.SPEEDING.value: 500.0,
    CrimeType.DANGEROUS_DRIVING.value: 1000.0,
    CrimeType.HIT_AND_RUN.value: 2500.0,
    CrimeType.VEHICLE_THEFT.value: 5000.0,
    CrimeType.PROPERTY_DAMAGE.value: 3000.0,
    CrimeType.WEAPON_POSSESSION.value: 10000.0,
    CrimeType.ASSAULT.value: 8000.0,
    CrimeType.ROBBERY.value: 15000.0,
    CrimeType.BUSINESS_THEFT.value: 20000.0,
    CrimeType.ILLEGAL_RACING.value: 7500.0,
    CrimeType.POLICE_ASSAULT.value: 25000.0,
    CrimeType.MURDER.value: 50000.0,
}

# Wanted level escalation by crime type
CRIME_WANTED_LEVELS: dict[str, int] = {
    CrimeType.SPEEDING.value: 1,
    CrimeType.DANGEROUS_DRIVING.value: 1,
    CrimeType.HIT_AND_RUN.value: 2,
    CrimeType.VEHICLE_THEFT.value: 2,
    CrimeType.PROPERTY_DAMAGE.value: 2,
    CrimeType.WEAPON_POSSESSION.value: 3,
    CrimeType.ASSAULT.value: 3,
    CrimeType.ROBBERY.value: 4,
    CrimeType.BUSINESS_THEFT.value: 4,
    CrimeType.ILLEGAL_RACING.value: 2,
    CrimeType.POLICE_ASSAULT.value: 5,
    CrimeType.MURDER.value: 6,
}

# Jail sentences by wanted level (seconds)
JAIL_SENTENCES: dict[int, int] = {
    0: 0,
    1: 30,
    2: 120,
    3: 300,
    4: 600,
    5: 1200,
    6: 3600,
}

# Police response description by wanted level
POLICE_RESPONSES: dict[int, str] = {
    0: "No response",
    1: "Police warning",
    2: "Traffic stop",
    3: "Vehicle chase",
    4: "Multiple police units",
    5: "Maximum response",
    6: "Full force authorized",
}


class PoliceService:
    """Business logic for Police lifecycle, crimes, wanted levels, arrests, fines, jail."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.police_repo = PoliceRepository(session)
        self.player_repo = PlayerRepository(session)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _validate_department(self, department: str) -> None:
        if department not in VALID_DEPARTMENTS:
            raise ValidationError(f"Invalid department: {department}. Valid: {sorted(VALID_DEPARTMENTS)}")

    def _validate_rank(self, rank: str) -> None:
        if rank not in VALID_OFFICER_RANKS:
            raise ValidationError(f"Invalid rank: {rank}. Valid: {sorted(VALID_OFFICER_RANKS)}")

    def _validate_officer_status(self, status: str) -> None:
        if status not in VALID_OFFICER_STATUSES:
            raise ValidationError(f"Invalid officer status: {status}. Valid: {sorted(VALID_OFFICER_STATUSES)}")

    def _validate_crime_type(self, crime_type: str) -> None:
        if crime_type not in VALID_CRIME_TYPES:
            raise ValidationError(f"Invalid crime type: {crime_type}. Valid: {sorted(VALID_CRIME_TYPES)}")

    def _validate_arrest_status(self, status: str) -> None:
        if status not in VALID_ARREST_STATUSES:
            raise ValidationError(f"Invalid arrest status: {status}. Valid: {sorted(VALID_ARREST_STATUSES)}")

    def _validate_fine_status(self, status: str) -> None:
        if status not in VALID_FINE_STATUSES:
            raise ValidationError(f"Invalid fine status: {status}. Valid: {sorted(VALID_FINE_STATUSES)}")

    def _validate_jail_status(self, status: str) -> None:
        if status not in VALID_JAIL_STATUSES:
            raise ValidationError(f"Invalid jail status: {status}. Valid: {sorted(VALID_JAIL_STATUSES)}")

    def _validate_report_status(self, status: str) -> None:
        if status not in VALID_REPORT_STATUSES:
            raise ValidationError(f"Invalid report status: {status}. Valid: {sorted(VALID_REPORT_STATUSES)}")

    def _validate_dispatch_priority(self, priority: str) -> None:
        if priority not in VALID_DISPATCH_PRIORITIES:
            raise ValidationError(f"Invalid dispatch priority: {priority}. Valid: {sorted(VALID_DISPATCH_PRIORITIES)}")

    def _validate_dispatch_status(self, status: str) -> None:
        if status not in VALID_DISPATCH_STATUSES:
            raise ValidationError(f"Invalid dispatch status: {status}. Valid: {sorted(VALID_DISPATCH_STATUSES)}")

    def _validate_equipment_type(self, equipment_type: str) -> None:
        if equipment_type not in VALID_EQUIPMENT_TYPES:
            raise ValidationError(f"Invalid equipment type: {equipment_type}. Valid: {sorted(VALID_EQUIPMENT_TYPES)}")

    def _validate_vehicle_type(self, vehicle_type: str) -> None:
        if vehicle_type not in VALID_VEHICLE_TYPES:
            raise ValidationError(f"Invalid vehicle type: {vehicle_type}. Valid: {sorted(VALID_VEHICLE_TYPES)}")

    # ── Officer CRUD ──────────────────────────────────────────────────────

    async def create_officer(self, data: dict) -> PoliceOfficer:
        if "department" in data and data["department"]:
            self._validate_department(data["department"])
        if "rank" in data and data["rank"]:
            self._validate_rank(data["rank"])

        existing = await self.police_repo.get_officer_by_player_id(data["player_id"])
        if existing:
            raise ConflictError("Player already has a police officer profile")

        existing_badge = await self.police_repo.get_officer_by_badge(data["badge_number"])
        if existing_badge:
            raise ConflictError(f"Badge number '{data['badge_number']}' is already taken")

        if "station_id" in data and data["station_id"]:
            station = await self.police_repo.get_station_by_id(data["station_id"])
            if not station:
                raise NotFoundError("Station not found")

        officer = await self.police_repo.create_officer(data)
        logger.info("Officer '%s' created (badge: %s)", officer.id, officer.badge_number)
        return await self.police_repo.get_officer_by_id(officer.id)

    async def get_officer(self, officer_id: uuid.UUID) -> PoliceOfficer:
        officer = await self.police_repo.get_officer_by_id(officer_id)
        if not officer:
            raise NotFoundError("Officer not found")
        return officer

    async def get_officer_by_player(self, player_id: uuid.UUID) -> PoliceOfficer:
        officer = await self.police_repo.get_officer_by_player_id(player_id)
        if not officer:
            raise NotFoundError("Officer profile not found for this player")
        return officer

    async def list_officers(
        self,
        department: str | None = None,
        status: str | None = None,
        rank: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[PoliceOfficer], int]:
        if department:
            self._validate_department(department)
        if status:
            self._validate_officer_status(status)
        if rank:
            self._validate_rank(rank)
        officers = await self.police_repo.get_all_officers(department, status, rank, skip, limit)
        total = await self.police_repo.count_officers(department, status)
        return officers, total

    async def update_officer(self, officer_id: uuid.UUID, data: dict) -> PoliceOfficer:
        await self.get_officer(officer_id)
        if "department" in data and data["department"]:
            self._validate_department(data["department"])
        if "rank" in data and data["rank"]:
            self._validate_rank(data["rank"])
        if "status" in data and data["status"]:
            self._validate_officer_status(data["status"])
        await self.police_repo.update_officer(officer_id, data)
        return await self.police_repo.get_officer_by_id(officer_id)

    async def delete_officer(self, officer_id: uuid.UUID) -> bool:
        await self.get_officer(officer_id)
        return await self.police_repo.soft_delete_officer(officer_id)

    # ── Station CRUD ──────────────────────────────────────────────────────

    async def create_station(self, data: dict) -> PoliceStation:
        if "department" in data and data["department"]:
            self._validate_department(data["department"])
        station = await self.police_repo.create_station(data)
        logger.info("Station '%s' created", station.station_name)
        return station

    async def get_station(self, station_id: uuid.UUID) -> PoliceStation:
        station = await self.police_repo.get_station_by_id(station_id)
        if not station:
            raise NotFoundError("Station not found")
        return station

    async def list_stations(
        self, department: str | None = None, skip: int = 0, limit: int = 50
    ) -> tuple[list[PoliceStation], int]:
        if department:
            self._validate_department(department)
        stations = await self.police_repo.get_all_stations(department, skip, limit)
        total = await self.police_repo.count_stations(department)
        return stations, total

    async def update_station(self, station_id: uuid.UUID, data: dict) -> PoliceStation:
        await self.get_station(station_id)
        if "department" in data and data["department"]:
            self._validate_department(data["department"])
        await self.police_repo.update_station(station_id, data)
        return await self.police_repo.get_station_by_id(station_id)

    async def delete_station(self, station_id: uuid.UUID) -> bool:
        await self.get_station(station_id)
        return await self.police_repo.soft_delete_station(station_id)

    # ── Crime CRUD ────────────────────────────────────────────────────────

    async def create_crime(self, data: dict) -> Crime:
        if "crime_type" in data:
            self._validate_crime_type(data["crime_type"])
        crime = await self.police_repo.create_crime(data)
        logger.info("Crime '%s' recorded for player %s", crime.crime_type, crime.player_id)
        return crime

    async def get_crime(self, crime_id: uuid.UUID) -> Crime:
        crime = await self.police_repo.get_crime_by_id(crime_id)
        if not crime:
            raise NotFoundError("Crime not found")
        return crime

    async def list_crimes(
        self,
        player_id: uuid.UUID | None = None,
        crime_type: str | None = None,
        resolved: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Crime], int]:
        if crime_type:
            self._validate_crime_type(crime_type)
        crimes = await self.police_repo.get_all_crimes(player_id, crime_type, resolved, skip, limit)
        total = await self.police_repo.count_crimes(player_id, crime_type)
        return crimes, total

    async def update_crime(self, crime_id: uuid.UUID, data: dict) -> Crime:
        await self.get_crime(crime_id)
        if "crime_type" in data and data["crime_type"]:
            self._validate_crime_type(data["crime_type"])
        await self.police_repo.update_crime(crime_id, data)
        return await self.police_repo.get_crime_by_id(crime_id)

    async def resolve_crime(self, crime_id: uuid.UUID) -> Crime:
        await self.get_crime(crime_id)
        await self.police_repo.update_crime(crime_id, {"is_resolved": True})
        return await self.police_repo.get_crime_by_id(crime_id)

    # ── Wanted Level ──────────────────────────────────────────────────────

    async def get_wanted_level(self, player_id: uuid.UUID) -> WantedLevel:
        wl = await self.police_repo.get_wanted_level(player_id)
        if not wl:
            wl = await self.police_repo.create_wanted_level({
                "player_id": player_id,
                "current_level": 0,
                "previous_level": 0,
            })
        return wl

    async def set_wanted_level(
        self,
        player_id: uuid.UUID,
        level: int,
        reason: str | None = None,
        crime_id: uuid.UUID | None = None,
    ) -> WantedLevel:
        if level < 0 or level > 6:
            raise ValidationError("Wanted level must be between 0 and 6")

        wl = await self.police_repo.get_wanted_level(player_id)
        now_str = datetime.now(timezone.utc).isoformat()

        if not wl:
            wl = await self.police_repo.create_wanted_level({
                "player_id": player_id,
                "current_level": level,
                "previous_level": 0,
                "reason": reason,
                "police_response": POLICE_RESPONSES.get(level, "No response"),
                "first_offense_at": now_str if level > 0 else None,
                "last_escalation_at": now_str if level > 0 else None,
                "last_crime_id": crime_id,
            })
        else:
            updates: dict = {
                "previous_level": wl.current_level,
                "current_level": level,
                "police_response": POLICE_RESPONSES.get(level, "No response"),
            }
            if reason:
                updates["reason"] = reason
            if crime_id:
                updates["last_crime_id"] = crime_id
            if level > wl.current_level:
                updates["last_escalation_at"] = now_str
            if level > 0 and not wl.first_offense_at:
                updates["first_offense_at"] = now_str
            if level == 0:
                updates["first_offense_at"] = None
                updates["cooldown_seconds"] = 0
            wl = await self.police_repo.update_wanted_level(player_id, updates)

        logger.info("Player %s wanted level set to %d", player_id, level)
        return wl

    async def escalate_wanted_level(
        self, player_id: uuid.UUID, crime_type: str
    ) -> WantedLevel:
        self._validate_crime_type(crime_type)
        target_level = CRIME_WANTED_LEVELS.get(crime_type, 1)
        wl = await self.get_wanted_level(player_id)
        new_level = max(wl.current_level, target_level)
        return await self.set_wanted_level(
            player_id,
            new_level,
            reason=f"Crime committed: {crime_type}",
        )

    async def get_all_wanted(
        self, min_level: int = 1, skip: int = 0, limit: int = 50
    ) -> tuple[list[WantedLevel], int]:
        wanted = await self.police_repo.get_all_wanted_players(min_level, skip, limit)
        return wanted, len(wanted)

    # ── Arrest ────────────────────────────────────────────────────────────

    async def create_arrest(self, data: dict) -> Arrest:
        self._validate_arrest_status(data.get("status", "pending"))
        officer = await self.get_officer(data["officer_id"])
        crime = await self.get_crime(data["crime_id"])

        wl = await self.get_wanted_level(data["player_id"])

        arrest = await self.police_repo.create_arrest(data)

        await self.police_repo.update_officer(officer.id, {
            "total_arrests": officer.total_arrests + 1,
        })

        await self.police_repo.update_crime(crime.id, {"is_resolved": True})

        await self.set_wanted_level(data["player_id"], 0, reason="Arrested")

        logger.info(
            "Arrest created: officer %s arrested player %s for crime %s",
            officer.id, data["player_id"], crime.id,
        )
        return await self.police_repo.get_arrest_by_id(arrest.id)

    async def get_arrest(self, arrest_id: uuid.UUID) -> Arrest:
        arrest = await self.police_repo.get_arrest_by_id(arrest_id)
        if not arrest:
            raise NotFoundError("Arrest not found")
        return arrest

    async def list_arrests_for_player(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[Arrest], int]:
        arrests = await self.police_repo.get_arrests_for_player(player_id, skip, limit)
        total = await self.police_repo.count_arrests(player_id=player_id)
        return arrests, total

    async def list_arrests_by_officer(
        self, officer_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[Arrest], int]:
        arrests = await self.police_repo.get_arrests_by_officer(officer_id, skip, limit)
        total = await self.police_repo.count_arrests(officer_id=officer_id)
        return arrests, total

    async def update_arrest(self, arrest_id: uuid.UUID, data: dict) -> Arrest:
        await self.get_arrest(arrest_id)
        if "status" in data and data["status"]:
            self._validate_arrest_status(data["status"])
        await self.police_repo.update_arrest(arrest_id, data)
        return await self.police_repo.get_arrest_by_id(arrest_id)

    async def confirm_arrest(self, arrest_id: uuid.UUID) -> Arrest:
        return await self.update_arrest(arrest_id, {"status": "confirmed"})

    async def dismiss_arrest(self, arrest_id: uuid.UUID) -> Arrest:
        return await self.update_arrest(arrest_id, {"status": "dismissed"})

    # ── Fine ──────────────────────────────────────────────────────────────

    async def create_fine(self, data: dict) -> Fine:
        self._validate_fine_status(data.get("status", "pending"))
        fine = await self.police_repo.create_fine(data)
        logger.info("Fine $%.2f created for player %s", fine.amount, fine.player_id)
        return fine

    async def get_fine(self, fine_id: uuid.UUID) -> Fine:
        fine = await self.police_repo.get_fine_by_id(fine_id)
        if not fine:
            raise NotFoundError("Fine not found")
        return fine

    async def list_fines_for_player(
        self, player_id: uuid.UUID, status: str | None = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[Fine], int]:
        if status:
            self._validate_fine_status(status)
        fines = await self.police_repo.get_fines_for_player(player_id, status, skip, limit)
        total = await self.police_repo.count_fines(player_id=player_id, status=status)
        return fines, total

    async def pay_fine(self, fine_id: uuid.UUID) -> Fine:
        fine = await self.get_fine(fine_id)
        if fine.status == "paid":
            raise ConflictError("Fine is already paid")
        if fine.status == "waived":
            raise ConflictError("Fine has been waived")
        now_str = datetime.now(timezone.utc).isoformat()
        await self.police_repo.update_fine(fine_id, {
            "status": "paid",
            "paid_at": now_str,
        })
        logger.info("Fine %s paid", fine_id)
        return await self.police_repo.get_fine_by_id(fine_id)

    async def waive_fine(self, fine_id: uuid.UUID, reason: str) -> Fine:
        fine = await self.get_fine(fine_id)
        if fine.status == "paid":
            raise ConflictError("Cannot waive a paid fine")
        await self.police_repo.update_fine(fine_id, {
            "status": "waived",
            "waived_reason": reason,
        })
        logger.info("Fine %s waived: %s", fine_id, reason)
        return await self.police_repo.get_fine_by_id(fine_id)

    async def update_fine(self, fine_id: uuid.UUID, data: dict) -> Fine:
        await self.get_fine(fine_id)
        if "status" in data and data["status"]:
            self._validate_fine_status(data["status"])
        await self.police_repo.update_fine(fine_id, data)
        return await self.police_repo.get_fine_by_id(fine_id)

    # ── Jail ──────────────────────────────────────────────────────────────

    async def create_jail(self, data: dict) -> Jail:
        self._validate_jail_status(data.get("status", "serving"))
        now_str = datetime.now(timezone.utc).isoformat()
        sentence_seconds = data["sentence_seconds"]
        data["sentence_start"] = now_str
        from datetime import timedelta
        end_dt = datetime.now(timezone.utc) + timedelta(seconds=sentence_seconds)
        data["sentence_end"] = end_dt.isoformat()

        jail = await self.police_repo.create_jail(data)
        logger.info(
            "Jail sentence: %d seconds for player %s", sentence_seconds, data["player_id"]
        )
        return jail

    async def get_jail(self, jail_id: uuid.UUID) -> Jail:
        jail = await self.police_repo.get_jail_by_id(jail_id)
        if not jail:
            raise NotFoundError("Jail record not found")
        return jail

    async def get_jail_for_player(self, player_id: uuid.UUID) -> Jail | None:
        return await self.police_repo.get_jail_for_player(player_id)

    async def list_jailed(
        self, status: str | None = None, skip: int = 0, limit: int = 50
    ) -> tuple[list[Jail], int]:
        if status:
            self._validate_jail_status(status)
        jailed = await self.police_repo.get_all_jailed(status, skip, limit)
        total = len(jailed)
        return jailed, total

    async def release_prisoner(self, jail_id: uuid.UUID, reason: str = "Sentence completed") -> Jail:
        jail = await self.get_jail(jail_id)
        if jail.status != "serving":
            raise ConflictError("Player is not currently serving a sentence")
        now_str = datetime.now(timezone.utc).isoformat()
        await self.police_repo.update_jail(jail_id, {
            "status": "released",
            "released_at": now_str,
            "release_reason": reason,
        })
        logger.info("Prisoner released: %s (reason: %s)", jail_id, reason)
        return await self.police_repo.get_jail_by_id(jail_id)

    # ── Crime Report ──────────────────────────────────────────────────────

    async def create_report(self, data: dict) -> CrimeReport:
        self._validate_report_status(data.get("status", "filed"))
        crime = await self.get_crime(data["crime_id"])
        report = await self.police_repo.create_report(data)
        logger.info("Crime report filed for crime %s by player %s", crime.id, data["reporter_player_id"])
        return report

    async def get_report(self, report_id: uuid.UUID) -> CrimeReport:
        report = await self.police_repo.get_report_by_id(report_id)
        if not report:
            raise NotFoundError("Crime report not found")
        return report

    async def list_reports_for_crime(self, crime_id: uuid.UUID) -> list[CrimeReport]:
        await self.get_crime(crime_id)
        return await self.police_repo.get_reports_for_crime(crime_id)

    async def list_reports_by_player(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[CrimeReport], int]:
        reports = await self.police_repo.get_reports_by_player(player_id, skip, limit)
        total = await self.police_repo.count_reports(player_id=player_id)
        return reports, total

    async def update_report(self, report_id: uuid.UUID, data: dict) -> CrimeReport:
        await self.get_report(report_id)
        if "status" in data and data["status"]:
            self._validate_report_status(data["status"])
        await self.police_repo.update_report(report_id, data)
        return await self.police_repo.get_report_by_id(report_id)

    async def assign_report(self, report_id: uuid.UUID, officer_id: uuid.UUID) -> CrimeReport:
        await self.get_officer(officer_id)
        return await self.update_report(report_id, {
            "assigned_officer_id": officer_id,
            "status": "under_investigation",
        })

    async def close_report(self, report_id: uuid.UUID, notes: str) -> CrimeReport:
        return await self.update_report(report_id, {
            "status": "closed",
            "resolution_notes": notes,
        })

    # ── Dispatch ──────────────────────────────────────────────────────────

    async def create_dispatch(self, data: dict) -> Dispatch:
        self._validate_dispatch_priority(data.get("priority", "medium"))
        self._validate_dispatch_status(data.get("status", "pending"))
        dispatch = await self.police_repo.create_dispatch(data)
        logger.info("Dispatch created for crime %s (priority: %s)", data["crime_id"], data.get("priority", "medium"))
        return dispatch

    async def get_dispatch(self, dispatch_id: uuid.UUID) -> Dispatch:
        dispatch = await self.police_repo.get_dispatch_by_id(dispatch_id)
        if not dispatch:
            raise NotFoundError("Dispatch not found")
        return dispatch

    async def list_pending_dispatches(
        self, skip: int = 0, limit: int = 50
    ) -> tuple[list[Dispatch], int]:
        dispatches = await self.police_repo.get_pending_dispatches(skip, limit)
        total = await self.police_repo.count_dispatches(status="pending")
        return dispatches, total

    async def list_dispatches_for_officer(
        self, officer_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[Dispatch], int]:
        dispatches = await self.police_repo.get_dispatches_for_officer(officer_id, skip, limit)
        total = len(dispatches)
        return dispatches, total

    async def update_dispatch(self, dispatch_id: uuid.UUID, data: dict) -> Dispatch:
        await self.get_dispatch(dispatch_id)
        if "status" in data and data["status"]:
            self._validate_dispatch_status(data["status"])
        if "priority" in data and data["priority"]:
            self._validate_dispatch_priority(data["priority"])
        await self.police_repo.update_dispatch(dispatch_id, data)
        return await self.police_repo.get_dispatch_by_id(dispatch_id)

    async def accept_dispatch(self, dispatch_id: uuid.UUID, officer_id: uuid.UUID) -> Dispatch:
        await self.get_officer(officer_id)
        return await self.update_dispatch(dispatch_id, {
            "officer_id": officer_id,
            "status": "dispatched",
        })

    async def complete_dispatch(self, dispatch_id: uuid.UUID) -> Dispatch:
        return await self.update_dispatch(dispatch_id, {"status": "completed"})

    # ── Police Record ─────────────────────────────────────────────────────

    async def get_police_record(self, player_id: uuid.UUID) -> PoliceRecord:
        record = await self.police_repo.get_record_for_player(player_id)
        if not record:
            record = await self.police_repo.create_record({
                "player_id": player_id,
                "wanted_level": 0,
                "total_arrests": 0,
                "total_fines": 0.0,
            })
        return record

    async def update_police_record(self, player_id: uuid.UUID, data: dict) -> PoliceRecord:
        await self.get_police_record(player_id)
        await self.police_repo.update_record(player_id, data)
        return await self.police_repo.get_record_for_player(player_id)

    async def get_crime_history(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[CrimeHistory]:
        return await self.police_repo.get_crime_history_for_player(player_id, skip, limit)

    async def add_crime_history(self, data: dict) -> CrimeHistory:
        return await self.police_repo.create_crime_history(data)

    # ── Equipment CRUD ────────────────────────────────────────────────────

    async def create_equipment(self, officer_id: uuid.UUID, data: dict) -> PoliceEquipment:
        await self.get_officer(officer_id)
        self._validate_equipment_type(data.get("equipment_type", ""))
        data["officer_id"] = officer_id
        equip = await self.police_repo.create_equipment(data)
        logger.info("Equipment '%s' issued to officer %s", equip.name, officer_id)
        return equip

    async def get_equipment(self, equip_id: uuid.UUID) -> PoliceEquipment:
        equip = await self.police_repo.get_equipment_by_id(equip_id)
        if not equip:
            raise NotFoundError("Equipment not found")
        return equip

    async def list_equipment_for_officer(
        self, officer_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[PoliceEquipment], int]:
        await self.get_officer(officer_id)
        equipment = await self.police_repo.get_equipment_for_officer(officer_id, skip, limit)
        total = await self.police_repo.count_equipment(officer_id=officer_id)
        return equipment, total

    async def update_equipment(self, equip_id: uuid.UUID, data: dict) -> PoliceEquipment:
        await self.get_equipment(equip_id)
        await self.police_repo.update_equipment(equip_id, data)
        return await self.police_repo.get_equipment_by_id(equip_id)

    # ── Vehicle CRUD ──────────────────────────────────────────────────────

    async def create_vehicle(self, data: dict) -> PoliceVehicle:
        self._validate_vehicle_type(data.get("vehicle_type", ""))
        if "officer_id" in data and data["officer_id"]:
            await self.get_officer(data["officer_id"])
        vehicle = await self.police_repo.create_vehicle(data)
        logger.info("Police vehicle '%s' created", vehicle.model_name)
        return vehicle

    async def get_vehicle(self, vehicle_id: uuid.UUID) -> PoliceVehicle:
        vehicle = await self.police_repo.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError("Police vehicle not found")
        return vehicle

    async def list_vehicles(
        self,
        vehicle_type: str | None = None,
        department: str | None = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[PoliceVehicle], int]:
        if vehicle_type:
            self._validate_vehicle_type(vehicle_type)
        if department:
            self._validate_department(department)
        vehicles = await self.police_repo.get_all_vehicles(vehicle_type, department, active_only, skip, limit)
        total = await self.police_repo.count_vehicles(vehicle_type, department)
        return vehicles, total

    async def list_vehicles_for_officer(
        self, officer_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[PoliceVehicle], int]:
        await self.get_officer(officer_id)
        vehicles = await self.police_repo.get_vehicles_for_officer(officer_id, skip, limit)
        total = len(vehicles)
        return vehicles, total

    async def update_vehicle(self, vehicle_id: uuid.UUID, data: dict) -> PoliceVehicle:
        await self.get_vehicle(vehicle_id)
        if "vehicle_type" in data and data["vehicle_type"]:
            self._validate_vehicle_type(data["vehicle_type"])
        if "department" in data and data["department"]:
            self._validate_department(data["department"])
        await self.police_repo.update_vehicle(vehicle_id, data)
        return await self.police_repo.get_vehicle_by_id(vehicle_id)

    async def assign_vehicle_to_officer(
        self, vehicle_id: uuid.UUID, officer_id: uuid.UUID
    ) -> PoliceVehicle:
        await self.get_officer(officer_id)
        await self.get_vehicle(vehicle_id)
        await self.police_repo.update_vehicle(vehicle_id, {"officer_id": officer_id})
        return await self.police_repo.get_vehicle_by_id(vehicle_id)
