"""Repository layer for Police-related database operations."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.police import (
    Arrest,
    Crime,
    CrimeReport,
    CrimeHistory,
    Dispatch,
    Fine,
    Jail,
    PoliceEquipment,
    PoliceOfficer,
    PoliceRecord,
    PoliceStation,
    PoliceVehicle,
    WantedLevel,
)


class PoliceRepository:
    """Data-access layer for all Police-related models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Police Officer ─────────────────────────────────────────────────────

    async def get_officer_by_id(self, officer_id: uuid.UUID) -> PoliceOfficer | None:
        stmt = (
            select(PoliceOfficer)
            .options(
                selectinload(PoliceOfficer.equipment),
                selectinload(PoliceOfficer.vehicles),
            )
            .where(PoliceOfficer.id == officer_id, PoliceOfficer.is_deleted.is_(False))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_officer_by_player_id(self, player_id: uuid.UUID) -> PoliceOfficer | None:
        stmt = select(PoliceOfficer).where(
            PoliceOfficer.player_id == player_id,
            PoliceOfficer.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_officer_by_badge(self, badge_number: str) -> PoliceOfficer | None:
        stmt = select(PoliceOfficer).where(
            PoliceOfficer.badge_number == badge_number,
            PoliceOfficer.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_officers(
        self,
        department: str | None = None,
        status: str | None = None,
        rank: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PoliceOfficer]:
        stmt = select(PoliceOfficer).where(PoliceOfficer.is_deleted.is_(False))
        if department:
            stmt = stmt.where(PoliceOfficer.department == department)
        if status:
            stmt = stmt.where(PoliceOfficer.status == status)
        if rank:
            stmt = stmt.where(PoliceOfficer.rank == rank)
        stmt = stmt.order_by(PoliceOfficer.badge_number).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_officers(
        self,
        department: str | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(PoliceOfficer.id)).where(PoliceOfficer.is_deleted.is_(False))
        if department:
            stmt = stmt.where(PoliceOfficer.department == department)
        if status:
            stmt = stmt.where(PoliceOfficer.status == status)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_officer(self, data: dict) -> PoliceOfficer:
        officer = PoliceOfficer(**data)
        self._session.add(officer)
        await self._session.flush()
        return officer

    async def update_officer(self, officer_id: uuid.UUID, data: dict) -> PoliceOfficer | None:
        stmt = (
            update(PoliceOfficer)
            .where(PoliceOfficer.id == officer_id, PoliceOfficer.is_deleted.is_(False))
            .values(**data)
            .returning(PoliceOfficer)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_officer(self, officer_id: uuid.UUID) -> bool:
        stmt = update(PoliceOfficer).where(
            PoliceOfficer.id == officer_id, PoliceOfficer.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Police Station ─────────────────────────────────────────────────────

    async def get_station_by_id(self, station_id: uuid.UUID) -> PoliceStation | None:
        stmt = select(PoliceStation).where(
            PoliceStation.id == station_id, PoliceStation.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_stations(
        self,
        department: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PoliceStation]:
        stmt = select(PoliceStation).where(PoliceStation.is_deleted.is_(False))
        if department:
            stmt = stmt.where(PoliceStation.department == department)
        stmt = stmt.order_by(PoliceStation.station_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_stations(self, department: str | None = None) -> int:
        stmt = select(func.count(PoliceStation.id)).where(PoliceStation.is_deleted.is_(False))
        if department:
            stmt = stmt.where(PoliceStation.department == department)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_station(self, data: dict) -> PoliceStation:
        station = PoliceStation(**data)
        self._session.add(station)
        await self._session.flush()
        return station

    async def update_station(self, station_id: uuid.UUID, data: dict) -> PoliceStation | None:
        stmt = (
            update(PoliceStation)
            .where(PoliceStation.id == station_id, PoliceStation.is_deleted.is_(False))
            .values(**data)
            .returning(PoliceStation)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_station(self, station_id: uuid.UUID) -> bool:
        stmt = update(PoliceStation).where(
            PoliceStation.id == station_id, PoliceStation.is_deleted.is_(False)
        ).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Crime ─────────────────────────────────────────────────────────────

    async def get_crime_by_id(self, crime_id: uuid.UUID) -> Crime | None:
        stmt = select(Crime).where(
            Crime.id == crime_id, Crime.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_crimes(
        self,
        player_id: uuid.UUID | None = None,
        crime_type: str | None = None,
        resolved: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Crime]:
        stmt = select(Crime).where(Crime.is_deleted.is_(False))
        if player_id:
            stmt = stmt.where(Crime.player_id == player_id)
        if crime_type:
            stmt = stmt.where(Crime.crime_type == crime_type)
        if resolved is not None:
            stmt = stmt.where(Crime.is_resolved == resolved)
        stmt = stmt.order_by(Crime.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_crimes(
        self,
        player_id: uuid.UUID | None = None,
        crime_type: str | None = None,
    ) -> int:
        stmt = select(func.count(Crime.id)).where(Crime.is_deleted.is_(False))
        if player_id:
            stmt = stmt.where(Crime.player_id == player_id)
        if crime_type:
            stmt = stmt.where(Crime.crime_type == crime_type)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_crime(self, data: dict) -> Crime:
        crime = Crime(**data)
        self._session.add(crime)
        await self._session.flush()
        return crime

    async def update_crime(self, crime_id: uuid.UUID, data: dict) -> Crime | None:
        stmt = (
            update(Crime)
            .where(Crime.id == crime_id, Crime.is_deleted.is_(False))
            .values(**data)
            .returning(Crime)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Wanted Level ──────────────────────────────────────────────────────

    async def get_wanted_level(self, player_id: uuid.UUID) -> WantedLevel | None:
        stmt = select(WantedLevel).where(
            WantedLevel.player_id == player_id,
            WantedLevel.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_wanted_players(
        self, min_level: int = 1, skip: int = 0, limit: int = 50
    ) -> list[WantedLevel]:
        stmt = (
            select(WantedLevel)
            .where(
                WantedLevel.current_level >= min_level,
                WantedLevel.is_deleted.is_(False),
            )
            .order_by(WantedLevel.current_level.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_wanted_level(self, data: dict) -> WantedLevel:
        wl = WantedLevel(**data)
        self._session.add(wl)
        await self._session.flush()
        return wl

    async def update_wanted_level(self, player_id: uuid.UUID, data: dict) -> WantedLevel | None:
        stmt = (
            update(WantedLevel)
            .where(
                WantedLevel.player_id == player_id,
                WantedLevel.is_deleted.is_(False),
            )
            .values(**data)
            .returning(WantedLevel)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Arrest ────────────────────────────────────────────────────────────

    async def get_arrest_by_id(self, arrest_id: uuid.UUID) -> Arrest | None:
        stmt = (
            select(Arrest)
            .options(
                selectinload(Arrest.fine),
                selectinload(Arrest.jail),
            )
            .where(Arrest.id == arrest_id, Arrest.is_deleted.is_(False))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_arrests_for_player(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[Arrest]:
        stmt = (
            select(Arrest)
            .where(Arrest.player_id == player_id, Arrest.is_deleted.is_(False))
            .order_by(Arrest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_arrests_by_officer(
        self, officer_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[Arrest]:
        stmt = (
            select(Arrest)
            .where(Arrest.officer_id == officer_id, Arrest.is_deleted.is_(False))
            .order_by(Arrest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_arrests(
        self, player_id: uuid.UUID | None = None, officer_id: uuid.UUID | None = None
    ) -> int:
        stmt = select(func.count(Arrest.id)).where(Arrest.is_deleted.is_(False))
        if player_id:
            stmt = stmt.where(Arrest.player_id == player_id)
        if officer_id:
            stmt = stmt.where(Arrest.officer_id == officer_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_arrest(self, data: dict) -> Arrest:
        arrest = Arrest(**data)
        self._session.add(arrest)
        await self._session.flush()
        return arrest

    async def update_arrest(self, arrest_id: uuid.UUID, data: dict) -> Arrest | None:
        stmt = (
            update(Arrest)
            .where(Arrest.id == arrest_id, Arrest.is_deleted.is_(False))
            .values(**data)
            .returning(Arrest)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Fine ──────────────────────────────────────────────────────────────

    async def get_fine_by_id(self, fine_id: uuid.UUID) -> Fine | None:
        stmt = select(Fine).where(Fine.id == fine_id, Fine.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_fine_for_arrest(self, arrest_id: uuid.UUID) -> Fine | None:
        stmt = select(Fine).where(
            Fine.arrest_id == arrest_id, Fine.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_fines_for_player(
        self,
        player_id: uuid.UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Fine]:
        stmt = select(Fine).where(Fine.player_id == player_id, Fine.is_deleted.is_(False))
        if status:
            stmt = stmt.where(Fine.status == status)
        stmt = stmt.order_by(Fine.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_fines(
        self, player_id: uuid.UUID | None = None, status: str | None = None
    ) -> int:
        stmt = select(func.count(Fine.id)).where(Fine.is_deleted.is_(False))
        if player_id:
            stmt = stmt.where(Fine.player_id == player_id)
        if status:
            stmt = stmt.where(Fine.status == status)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_fine(self, data: dict) -> Fine:
        fine = Fine(**data)
        self._session.add(fine)
        await self._session.flush()
        return fine

    async def update_fine(self, fine_id: uuid.UUID, data: dict) -> Fine | None:
        stmt = (
            update(Fine)
            .where(Fine.id == fine_id, Fine.is_deleted.is_(False))
            .values(**data)
            .returning(Fine)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Jail ──────────────────────────────────────────────────────────────

    async def get_jail_by_id(self, jail_id: uuid.UUID) -> Jail | None:
        stmt = select(Jail).where(Jail.id == jail_id, Jail.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_jail_for_arrest(self, arrest_id: uuid.UUID) -> Jail | None:
        stmt = select(Jail).where(Jail.arrest_id == arrest_id, Jail.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_jail_for_player(self, player_id: uuid.UUID) -> Jail | None:
        stmt = select(Jail).where(
            Jail.player_id == player_id,
            Jail.status == "serving",
            Jail.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_jailed(
        self, status: str | None = None, skip: int = 0, limit: int = 50
    ) -> list[Jail]:
        stmt = select(Jail).where(Jail.is_deleted.is_(False))
        if status:
            stmt = stmt.where(Jail.status == status)
        stmt = stmt.order_by(Jail.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_jail(self, data: dict) -> Jail:
        jail = Jail(**data)
        self._session.add(jail)
        await self._session.flush()
        return jail

    async def update_jail(self, jail_id: uuid.UUID, data: dict) -> Jail | None:
        stmt = (
            update(Jail)
            .where(Jail.id == jail_id, Jail.is_deleted.is_(False))
            .values(**data)
            .returning(Jail)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Crime Report ──────────────────────────────────────────────────────

    async def get_report_by_id(self, report_id: uuid.UUID) -> CrimeReport | None:
        stmt = select(CrimeReport).where(
            CrimeReport.id == report_id, CrimeReport.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_reports_for_crime(self, crime_id: uuid.UUID) -> list[CrimeReport]:
        stmt = (
            select(CrimeReport)
            .where(CrimeReport.crime_id == crime_id, CrimeReport.is_deleted.is_(False))
            .order_by(CrimeReport.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_reports_by_player(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[CrimeReport]:
        stmt = (
            select(CrimeReport)
            .where(
                CrimeReport.reporter_player_id == player_id,
                CrimeReport.is_deleted.is_(False),
            )
            .order_by(CrimeReport.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_reports(
        self, player_id: uuid.UUID | None = None, status: str | None = None
    ) -> int:
        stmt = select(func.count(CrimeReport.id)).where(CrimeReport.is_deleted.is_(False))
        if player_id:
            stmt = stmt.where(CrimeReport.reporter_player_id == player_id)
        if status:
            stmt = stmt.where(CrimeReport.status == status)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_report(self, data: dict) -> CrimeReport:
        report = CrimeReport(**data)
        self._session.add(report)
        await self._session.flush()
        return report

    async def update_report(self, report_id: uuid.UUID, data: dict) -> CrimeReport | None:
        stmt = (
            update(CrimeReport)
            .where(CrimeReport.id == report_id, CrimeReport.is_deleted.is_(False))
            .values(**data)
            .returning(CrimeReport)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Dispatch ──────────────────────────────────────────────────────────

    async def get_dispatch_by_id(self, dispatch_id: uuid.UUID) -> Dispatch | None:
        stmt = select(Dispatch).where(
            Dispatch.id == dispatch_id, Dispatch.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_dispatches(
        self, skip: int = 0, limit: int = 50
    ) -> list[Dispatch]:
        stmt = (
            select(Dispatch)
            .where(Dispatch.status == "pending", Dispatch.is_deleted.is_(False))
            .order_by(Dispatch.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_dispatches_for_officer(
        self, officer_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[Dispatch]:
        stmt = (
            select(Dispatch)
            .where(Dispatch.officer_id == officer_id, Dispatch.is_deleted.is_(False))
            .order_by(Dispatch.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_dispatches(self, status: str | None = None) -> int:
        stmt = select(func.count(Dispatch.id)).where(Dispatch.is_deleted.is_(False))
        if status:
            stmt = stmt.where(Dispatch.status == status)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_dispatch(self, data: dict) -> Dispatch:
        dispatch = Dispatch(**data)
        self._session.add(dispatch)
        await self._session.flush()
        return dispatch

    async def update_dispatch(self, dispatch_id: uuid.UUID, data: dict) -> Dispatch | None:
        stmt = (
            update(Dispatch)
            .where(Dispatch.id == dispatch_id, Dispatch.is_deleted.is_(False))
            .values(**data)
            .returning(Dispatch)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Police Record ─────────────────────────────────────────────────────

    async def get_record_for_player(self, player_id: uuid.UUID) -> PoliceRecord | None:
        stmt = select(PoliceRecord).where(
            PoliceRecord.player_id == player_id,
            PoliceRecord.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_record(self, data: dict) -> PoliceRecord:
        record = PoliceRecord(**data)
        self._session.add(record)
        await self._session.flush()
        return record

    async def update_record(self, player_id: uuid.UUID, data: dict) -> PoliceRecord | None:
        stmt = (
            update(PoliceRecord)
            .where(PoliceRecord.player_id == player_id, PoliceRecord.is_deleted.is_(False))
            .values(**data)
            .returning(PoliceRecord)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Crime History ─────────────────────────────────────────────────────

    async def get_crime_history_for_player(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[CrimeHistory]:
        stmt = (
            select(CrimeHistory)
            .where(CrimeHistory.player_id == player_id, CrimeHistory.is_deleted.is_(False))
            .order_by(CrimeHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_crime_history(self, data: dict) -> CrimeHistory:
        ch = CrimeHistory(**data)
        self._session.add(ch)
        await self._session.flush()
        return ch

    # ── Police Equipment ──────────────────────────────────────────────────

    async def get_equipment_by_id(self, equip_id: uuid.UUID) -> PoliceEquipment | None:
        stmt = select(PoliceEquipment).where(
            PoliceEquipment.id == equip_id, PoliceEquipment.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_equipment_for_officer(
        self, officer_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[PoliceEquipment]:
        stmt = (
            select(PoliceEquipment)
            .where(
                PoliceEquipment.officer_id == officer_id,
                PoliceEquipment.is_deleted.is_(False),
            )
            .order_by(PoliceEquipment.name)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_equipment(self, officer_id: uuid.UUID | None = None) -> int:
        stmt = select(func.count(PoliceEquipment.id)).where(PoliceEquipment.is_deleted.is_(False))
        if officer_id:
            stmt = stmt.where(PoliceEquipment.officer_id == officer_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_equipment(self, data: dict) -> PoliceEquipment:
        equip = PoliceEquipment(**data)
        self._session.add(equip)
        await self._session.flush()
        return equip

    async def update_equipment(self, equip_id: uuid.UUID, data: dict) -> PoliceEquipment | None:
        stmt = (
            update(PoliceEquipment)
            .where(PoliceEquipment.id == equip_id, PoliceEquipment.is_deleted.is_(False))
            .values(**data)
            .returning(PoliceEquipment)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Police Vehicle ────────────────────────────────────────────────────

    async def get_vehicle_by_id(self, vehicle_id: uuid.UUID) -> PoliceVehicle | None:
        stmt = select(PoliceVehicle).where(
            PoliceVehicle.id == vehicle_id, PoliceVehicle.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vehicles_for_officer(
        self, officer_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[PoliceVehicle]:
        stmt = (
            select(PoliceVehicle)
            .where(
                PoliceVehicle.officer_id == officer_id,
                PoliceVehicle.is_deleted.is_(False),
            )
            .order_by(PoliceVehicle.call_sign)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_vehicles(
        self,
        vehicle_type: str | None = None,
        department: str | None = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PoliceVehicle]:
        stmt = select(PoliceVehicle).where(PoliceVehicle.is_deleted.is_(False))
        if vehicle_type:
            stmt = stmt.where(PoliceVehicle.vehicle_type == vehicle_type)
        if department:
            stmt = stmt.where(PoliceVehicle.department == department)
        if active_only:
            stmt = stmt.where(PoliceVehicle.is_active.is_(True))
        stmt = stmt.order_by(PoliceVehicle.call_sign).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_vehicles(
        self, vehicle_type: str | None = None, department: str | None = None
    ) -> int:
        stmt = select(func.count(PoliceVehicle.id)).where(PoliceVehicle.is_deleted.is_(False))
        if vehicle_type:
            stmt = stmt.where(PoliceVehicle.vehicle_type == vehicle_type)
        if department:
            stmt = stmt.where(PoliceVehicle.department == department)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_vehicle(self, data: dict) -> PoliceVehicle:
        vehicle = PoliceVehicle(**data)
        self._session.add(vehicle)
        await self._session.flush()
        return vehicle

    async def update_vehicle(self, vehicle_id: uuid.UUID, data: dict) -> PoliceVehicle | None:
        stmt = (
            update(PoliceVehicle)
            .where(PoliceVehicle.id == vehicle_id, PoliceVehicle.is_deleted.is_(False))
            .values(**data)
            .returning(PoliceVehicle)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
