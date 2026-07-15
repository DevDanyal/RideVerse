"""Police API endpoints — officers, stations, crimes, wanted levels, arrests, fines, jail, reports, dispatch, records, equipment, vehicles."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.common import SuccessResponse
from app.schemas.police import (
    ArrestCreateRequest,
    ArrestListResponse,
    ArrestResponse,
    ArrestUpdateRequest,
    CrimeCreateRequest,
    CrimeHistoryListResponse,
    CrimeHistoryResponse,
    CrimeListResponse,
    CrimeReportCreateRequest,
    CrimeReportListResponse,
    CrimeReportResponse,
    CrimeReportUpdateRequest,
    CrimeResponse,
    CrimeUpdateRequest,
    DispatchCreateRequest,
    DispatchListResponse,
    DispatchResponse,
    DispatchUpdateRequest,
    FineCreateRequest,
    FineListResponse,
    FinePayRequest,
    FineResponse,
    FineWaiveRequest,
    JailCreateRequest,
    JailListResponse,
    JailReleaseRequest,
    JailResponse,
    PoliceEquipmentCreateRequest,
    PoliceEquipmentListResponse,
    PoliceEquipmentResponse,
    PoliceEquipmentUpdateRequest,
    PoliceOfficerCreateRequest,
    PoliceOfficerListResponse,
    PoliceOfficerResponse,
    PoliceOfficerUpdateRequest,
    PoliceRecordListResponse,
    PoliceRecordResponse,
    PoliceStationCreateRequest,
    PoliceStationListResponse,
    PoliceStationResponse,
    PoliceStationUpdateRequest,
    PoliceVehicleCreateRequest,
    PoliceVehicleListResponse,
    PoliceVehicleResponse,
    PoliceVehicleUpdateRequest,
    WantedLevelResponse,
    WantedLevelSetRequest,
)
from app.services.police import PoliceService

router = APIRouter(prefix="/police", tags=["Police"])


def _get_police_service(session: AsyncSession) -> PoliceService:
    return PoliceService(session)


# ── Police Officers ────────────────────────────────────────────────────────────


@router.get("/officers", response_model=PoliceOfficerListResponse)
async def list_officers(
    department: str | None = None,
    status: str | None = None,
    rank: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    officers, total = await svc.list_officers(department, status, rank, skip, limit)
    return PoliceOfficerListResponse(
        message=f"{len(officers)} officers retrieved",
        data=[PoliceOfficerResponse.model_validate(o) for o in officers],
        total=total,
    )


@router.get("/officers/{officer_id}", response_model=SuccessResponse[PoliceOfficerResponse])
async def get_officer(
    officer_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    officer = await svc.get_officer(officer_id)
    return SuccessResponse(
        message="Officer retrieved",
        data=PoliceOfficerResponse.model_validate(officer),
    )


@router.post("/officers", status_code=201)
async def create_officer(
    body: PoliceOfficerCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    officer = await svc.create_officer(body.model_dump())
    return SuccessResponse(
        message="Officer created",
        data=PoliceOfficerResponse.model_validate(officer),
    )


@router.patch("/officers/{officer_id}")
async def update_officer(
    officer_id: uuid.UUID,
    body: PoliceOfficerUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    officer = await svc.update_officer(officer_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Officer updated",
        data=PoliceOfficerResponse.model_validate(officer),
    )


@router.delete("/officers/{officer_id}")
async def delete_officer(
    officer_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    await svc.delete_officer(officer_id)
    return SuccessResponse(message="Officer deleted")


# ── Police Stations ───────────────────────────────────────────────────────────


@router.get("/stations", response_model=PoliceStationListResponse)
async def list_stations(
    department: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    stations, total = await svc.list_stations(department, skip, limit)
    return PoliceStationListResponse(
        message=f"{len(stations)} stations retrieved",
        data=[PoliceStationResponse.model_validate(s) for s in stations],
        total=total,
    )


@router.get("/stations/{station_id}", response_model=SuccessResponse[PoliceStationResponse])
async def get_station(
    station_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    station = await svc.get_station(station_id)
    return SuccessResponse(
        message="Station retrieved",
        data=PoliceStationResponse.model_validate(station),
    )


@router.post("/stations", status_code=201)
async def create_station(
    body: PoliceStationCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    station = await svc.create_station(body.model_dump())
    return SuccessResponse(
        message="Station created",
        data=PoliceStationResponse.model_validate(station),
    )


@router.patch("/stations/{station_id}")
async def update_station(
    station_id: uuid.UUID,
    body: PoliceStationUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    station = await svc.update_station(station_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Station updated",
        data=PoliceStationResponse.model_validate(station),
    )


@router.delete("/stations/{station_id}")
async def delete_station(
    station_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    await svc.delete_station(station_id)
    return SuccessResponse(message="Station deleted")


# ── Crimes ────────────────────────────────────────────────────────────────────


@router.get("/crimes", response_model=CrimeListResponse)
async def list_crimes(
    player_id: uuid.UUID | None = None,
    crime_type: str | None = None,
    resolved: bool | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    crimes, total = await svc.list_crimes(player_id, crime_type, resolved, skip, limit)
    return CrimeListResponse(
        message=f"{len(crimes)} crimes retrieved",
        data=[CrimeResponse.model_validate(c) for c in crimes],
        total=total,
    )


@router.get("/crimes/{crime_id}", response_model=SuccessResponse[CrimeResponse])
async def get_crime(
    crime_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    crime = await svc.get_crime(crime_id)
    return SuccessResponse(
        message="Crime retrieved",
        data=CrimeResponse.model_validate(crime),
    )


@router.post("/crimes", status_code=201)
async def create_crime(
    body: CrimeCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    crime = await svc.create_crime(body.model_dump())
    return SuccessResponse(
        message="Crime recorded",
        data=CrimeResponse.model_validate(crime),
    )


@router.patch("/crimes/{crime_id}")
async def update_crime(
    crime_id: uuid.UUID,
    body: CrimeUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    crime = await svc.update_crime(crime_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Crime updated",
        data=CrimeResponse.model_validate(crime),
    )


@router.post("/crimes/{crime_id}/resolve")
async def resolve_crime(
    crime_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    crime = await svc.resolve_crime(crime_id)
    return SuccessResponse(
        message="Crime resolved",
        data=CrimeResponse.model_validate(crime),
    )


# ── Wanted Levels ─────────────────────────────────────────────────────────────


@router.get("/wanted/{player_id}", response_model=SuccessResponse[WantedLevelResponse])
async def get_wanted_level(
    player_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    wl = await svc.get_wanted_level(player_id)
    return SuccessResponse(
        message="Wanted level retrieved",
        data=WantedLevelResponse.model_validate(wl),
    )


@router.post("/wanted/set")
async def set_wanted_level(
    body: WantedLevelSetRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    wl = await svc.set_wanted_level(body.player_id, body.current_level, body.reason)
    return SuccessResponse(
        message="Wanted level set",
        data=WantedLevelResponse.model_validate(wl),
    )


@router.get("/wanted")
async def list_wanted(
    min_level: int = 1,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    wanted, total = await svc.get_all_wanted(min_level, skip, limit)
    return SuccessResponse(
        message=f"{len(wanted)} wanted players found",
        data=[WantedLevelResponse.model_validate(w) for w in wanted],
    )


# ── Arrests ───────────────────────────────────────────────────────────────────


@router.get("/arrests", response_model=ArrestListResponse)
async def list_arrests(
    player_id: uuid.UUID | None = None,
    officer_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    if player_id:
        arrests, total = await svc.list_arrests_for_player(player_id, skip, limit)
    elif officer_id:
        arrests, total = await svc.list_arrests_by_officer(officer_id, skip, limit)
    else:
        arrests, total = [], 0
    return ArrestListResponse(
        message=f"{len(arrests)} arrests retrieved",
        data=[ArrestResponse.model_validate(a) for a in arrests],
        total=total,
    )


@router.get("/arrests/{arrest_id}", response_model=SuccessResponse[ArrestResponse])
async def get_arrest(
    arrest_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    arrest = await svc.get_arrest(arrest_id)
    return SuccessResponse(
        message="Arrest retrieved",
        data=ArrestResponse.model_validate(arrest),
    )


@router.post("/arrests", status_code=201)
async def create_arrest(
    body: ArrestCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    arrest = await svc.create_arrest(body.model_dump())
    return SuccessResponse(
        message="Arrest recorded",
        data=ArrestResponse.model_validate(arrest),
    )


@router.patch("/arrests/{arrest_id}")
async def update_arrest(
    arrest_id: uuid.UUID,
    body: ArrestUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    arrest = await svc.update_arrest(arrest_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Arrest updated",
        data=ArrestResponse.model_validate(arrest),
    )


@router.post("/arrests/{arrest_id}/confirm")
async def confirm_arrest(
    arrest_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    arrest = await svc.confirm_arrest(arrest_id)
    return SuccessResponse(
        message="Arrest confirmed",
        data=ArrestResponse.model_validate(arrest),
    )


@router.post("/arrests/{arrest_id}/dismiss")
async def dismiss_arrest(
    arrest_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    arrest = await svc.dismiss_arrest(arrest_id)
    return SuccessResponse(
        message="Arrest dismissed",
        data=ArrestResponse.model_validate(arrest),
    )


# ── Fines ─────────────────────────────────────────────────────────────────────


@router.get("/fines", response_model=FineListResponse)
async def list_fines(
    player_id: uuid.UUID | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    if player_id:
        fines, total = await svc.list_fines_for_player(player_id, status, skip, limit)
    else:
        fines, total = [], 0
    return FineListResponse(
        message=f"{len(fines)} fines retrieved",
        data=[FineResponse.model_validate(f) for f in fines],
        total=total,
    )


@router.get("/fines/{fine_id}", response_model=SuccessResponse[FineResponse])
async def get_fine(
    fine_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    fine = await svc.get_fine(fine_id)
    return SuccessResponse(
        message="Fine retrieved",
        data=FineResponse.model_validate(fine),
    )


@router.post("/fines", status_code=201)
async def create_fine(
    body: FineCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    fine = await svc.create_fine(body.model_dump())
    return SuccessResponse(
        message="Fine created",
        data=FineResponse.model_validate(fine),
    )


@router.post("/fines/{fine_id}/pay")
async def pay_fine(
    fine_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    fine = await svc.pay_fine(fine_id)
    return SuccessResponse(
        message="Fine paid",
        data=FineResponse.model_validate(fine),
    )


@router.post("/fines/{fine_id}/waive")
async def waive_fine(
    fine_id: uuid.UUID,
    body: FineWaiveRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    fine = await svc.waive_fine(fine_id, body.waived_reason)
    return SuccessResponse(
        message="Fine waived",
        data=FineResponse.model_validate(fine),
    )


# ── Jail ──────────────────────────────────────────────────────────────────────


@router.get("/jail", response_model=JailListResponse)
async def list_jailed(
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    jailed, total = await svc.list_jailed(status, skip, limit)
    return JailListResponse(
        message=f"{len(jailed)} jail records retrieved",
        data=[JailResponse.model_validate(j) for j in jailed],
        total=total,
    )


@router.get("/jail/{jail_id}", response_model=SuccessResponse[JailResponse])
async def get_jail(
    jail_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    jail = await svc.get_jail(jail_id)
    return SuccessResponse(
        message="Jail record retrieved",
        data=JailResponse.model_validate(jail),
    )


@router.post("/jail", status_code=201)
async def create_jail(
    body: JailCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    jail = await svc.create_jail(body.model_dump())
    return SuccessResponse(
        message="Jail sentence recorded",
        data=JailResponse.model_validate(jail),
    )


@router.post("/jail/{jail_id}/release")
async def release_prisoner(
    jail_id: uuid.UUID,
    body: JailReleaseRequest | None = None,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    reason = body.release_reason if body else "Sentence completed"
    jail = await svc.release_prisoner(jail_id, reason)
    return SuccessResponse(
        message="Prisoner released",
        data=JailResponse.model_validate(jail),
    )


# ── Crime Reports ─────────────────────────────────────────────────────────────


@router.get("/reports", response_model=CrimeReportListResponse)
async def list_reports(
    player_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    if player_id:
        reports, total = await svc.list_reports_by_player(player_id, skip, limit)
    else:
        reports, total = [], 0
    return CrimeReportListResponse(
        message=f"{len(reports)} reports retrieved",
        data=[CrimeReportResponse.model_validate(r) for r in reports],
        total=total,
    )


@router.get("/reports/{report_id}", response_model=SuccessResponse[CrimeReportResponse])
async def get_report(
    report_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    report = await svc.get_report(report_id)
    return SuccessResponse(
        message="Report retrieved",
        data=CrimeReportResponse.model_validate(report),
    )


@router.post("/reports", status_code=201)
async def create_report(
    body: CrimeReportCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    report = await svc.create_report(body.model_dump())
    return SuccessResponse(
        message="Report filed",
        data=CrimeReportResponse.model_validate(report),
    )


@router.patch("/reports/{report_id}")
async def update_report(
    report_id: uuid.UUID,
    body: CrimeReportUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    report = await svc.update_report(report_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Report updated",
        data=CrimeReportResponse.model_validate(report),
    )


@router.post("/reports/{report_id}/assign/{officer_id}")
async def assign_report(
    report_id: uuid.UUID,
    officer_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    report = await svc.assign_report(report_id, officer_id)
    return SuccessResponse(
        message="Report assigned",
        data=CrimeReportResponse.model_validate(report),
    )


@router.post("/reports/{report_id}/close")
async def close_report(
    report_id: uuid.UUID,
    notes: str = "Investigation complete",
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    report = await svc.close_report(report_id, notes)
    return SuccessResponse(
        message="Report closed",
        data=CrimeReportResponse.model_validate(report),
    )


# ── Dispatch ──────────────────────────────────────────────────────────────────


@router.get("/dispatch", response_model=DispatchListResponse)
async def list_pending_dispatches(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    dispatches, total = await svc.list_pending_dispatches(skip, limit)
    return DispatchListResponse(
        message=f"{len(dispatches)} pending dispatches",
        data=[DispatchResponse.model_validate(d) for d in dispatches],
        total=total,
    )


@router.get("/dispatch/{dispatch_id}", response_model=SuccessResponse[DispatchResponse])
async def get_dispatch(
    dispatch_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    dispatch = await svc.get_dispatch(dispatch_id)
    return SuccessResponse(
        message="Dispatch retrieved",
        data=DispatchResponse.model_validate(dispatch),
    )


@router.post("/dispatch", status_code=201)
async def create_dispatch(
    body: DispatchCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    dispatch = await svc.create_dispatch(body.model_dump())
    return SuccessResponse(
        message="Dispatch created",
        data=DispatchResponse.model_validate(dispatch),
    )


@router.patch("/dispatch/{dispatch_id}")
async def update_dispatch(
    dispatch_id: uuid.UUID,
    body: DispatchUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    dispatch = await svc.update_dispatch(dispatch_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Dispatch updated",
        data=DispatchResponse.model_validate(dispatch),
    )


@router.post("/dispatch/{dispatch_id}/accept/{officer_id}")
async def accept_dispatch(
    dispatch_id: uuid.UUID,
    officer_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    dispatch = await svc.accept_dispatch(dispatch_id, officer_id)
    return SuccessResponse(
        message="Dispatch accepted",
        data=DispatchResponse.model_validate(dispatch),
    )


@router.post("/dispatch/{dispatch_id}/complete")
async def complete_dispatch(
    dispatch_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    dispatch = await svc.complete_dispatch(dispatch_id)
    return SuccessResponse(
        message="Dispatch completed",
        data=DispatchResponse.model_validate(dispatch),
    )


# ── Player Criminal Record ────────────────────────────────────────────────────


@router.get("/record/{player_id}", response_model=SuccessResponse[PoliceRecordResponse])
async def get_police_record(
    player_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    record = await svc.get_police_record(player_id)
    return SuccessResponse(
        message="Police record retrieved",
        data=PoliceRecordResponse.model_validate(record),
    )


@router.get("/record/{player_id}/history", response_model=CrimeHistoryListResponse)
async def get_crime_history(
    player_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    history = await svc.get_crime_history(player_id, skip, limit)
    return CrimeHistoryListResponse(
        message=f"{len(history)} crime history entries retrieved",
        data=[CrimeHistoryResponse.model_validate(h) for h in history],
        total=len(history),
    )


# ── Police Equipment ──────────────────────────────────────────────────────────


@router.get("/officers/{officer_id}/equipment", response_model=PoliceEquipmentListResponse)
async def list_equipment(
    officer_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    equipment, total = await svc.list_equipment_for_officer(officer_id, skip, limit)
    return PoliceEquipmentListResponse(
        message=f"{len(equipment)} equipment items retrieved",
        data=[PoliceEquipmentResponse.model_validate(e) for e in equipment],
        total=total,
    )


@router.post("/officers/{officer_id}/equipment", status_code=201)
async def create_equipment(
    officer_id: uuid.UUID,
    body: PoliceEquipmentCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    equip = await svc.create_equipment(officer_id, body.model_dump())
    return SuccessResponse(
        message="Equipment issued",
        data=PoliceEquipmentResponse.model_validate(equip),
    )


@router.patch("/equipment/{equip_id}")
async def update_equipment(
    equip_id: uuid.UUID,
    body: PoliceEquipmentUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    equip = await svc.update_equipment(equip_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Equipment updated",
        data=PoliceEquipmentResponse.model_validate(equip),
    )


# ── Police Vehicles ───────────────────────────────────────────────────────────


@router.get("/vehicles", response_model=PoliceVehicleListResponse)
async def list_vehicles(
    vehicle_type: str | None = None,
    department: str | None = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    vehicles, total = await svc.list_vehicles(vehicle_type, department, active_only, skip, limit)
    return PoliceVehicleListResponse(
        message=f"{len(vehicles)} vehicles retrieved",
        data=[PoliceVehicleResponse.model_validate(v) for v in vehicles],
        total=total,
    )


@router.get("/vehicles/{vehicle_id}", response_model=SuccessResponse[PoliceVehicleResponse])
async def get_vehicle(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    vehicle = await svc.get_vehicle(vehicle_id)
    return SuccessResponse(
        message="Vehicle retrieved",
        data=PoliceVehicleResponse.model_validate(vehicle),
    )


@router.post("/vehicles", status_code=201)
async def create_vehicle(
    body: PoliceVehicleCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    vehicle = await svc.create_vehicle(body.model_dump())
    return SuccessResponse(
        message="Vehicle created",
        data=PoliceVehicleResponse.model_validate(vehicle),
    )


@router.patch("/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: uuid.UUID,
    body: PoliceVehicleUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    vehicle = await svc.update_vehicle(vehicle_id, body.model_dump(exclude_unset=True))
    return SuccessResponse(
        message="Vehicle updated",
        data=PoliceVehicleResponse.model_validate(vehicle),
    )


@router.post("/vehicles/{vehicle_id}/assign/{officer_id}")
async def assign_vehicle(
    vehicle_id: uuid.UUID,
    officer_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_police_service(session)
    vehicle = await svc.assign_vehicle_to_officer(vehicle_id, officer_id)
    return SuccessResponse(
        message="Vehicle assigned",
        data=PoliceVehicleResponse.model_validate(vehicle),
    )
