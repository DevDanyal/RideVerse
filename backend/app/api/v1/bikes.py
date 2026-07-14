"""Bike API endpoints — Honda 125 system."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.bike import (
    BikeCustomizationResponse,
    BikeCustomizationUpdate,
    BikeDamageReport,
    BikeInsuranceCreate,
    BikeInsuranceResponse,
    BikeListResponse,
    BikePerformanceStats,
    BikePurchaseRequest,
    BikeRefuelRequest,
    BikeRepairRequest,
    BikeRepairResponse,
    BikeSellResponse,
    BikeUpgradeRequest,
    BikeVariantListResponse,
    BikeVariantResponse,
    FuelStationResponse,
    SuccessResponse,
    VehicleResponse,
)
from app.services.bike import BikeService

router = APIRouter(prefix="/bikes", tags=["Bikes"])


def _get_bike_service(session: AsyncSession) -> BikeService:
    return BikeService(session)


# ── Variants ───────────────────────────────────────────────────────────────────


@router.get("/variants", response_model=SuccessResponse[list[BikeVariantResponse]])
async def list_variants(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    variants = await svc.get_variants()
    return SuccessResponse(message="Variants retrieved", data=[BikeVariantResponse.model_validate(v) for v in variants])


@router.get("/variants/{variant_id}", response_model=SuccessResponse[BikeVariantResponse])
async def get_variant(
    variant_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    variant = await svc.get_variant(variant_id)
    return SuccessResponse(message="Variant retrieved", data=BikeVariantResponse.model_validate(variant))


# ── Purchase / Sell ────────────────────────────────────────────────────────────


@router.post("/", status_code=201)
async def purchase_bike(
    body: BikePurchaseRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.purchase_bike(player.id, body.variant_id, body.name)
    return SuccessResponse(
        message="Bike purchased successfully",
        data={
            "vehicle": VehicleResponse.model_validate(result["vehicle"]),
            "variant": BikeVariantResponse.model_validate(result["variant"]),
        },
    )


@router.delete("/{vehicle_id}")
async def sell_bike(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.sell_bike(player.id, vehicle_id)
    return SuccessResponse(message=result["message"], data=result)


# ── List / Detail ──────────────────────────────────────────────────────────────


@router.get("/", response_model=SuccessResponse[list])
async def list_bikes(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    bikes = await svc.get_player_bikes(player.id)
    return SuccessResponse(message="Bikes retrieved", data=bikes)


@router.get("/{vehicle_id}")
async def get_bike_detail(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    detail = await svc.get_bike_detail(player.id, vehicle_id)
    return SuccessResponse(message="Bike detail retrieved", data=detail)


# ── Customization ──────────────────────────────────────────────────────────────


@router.patch("/{vehicle_id}/customization")
async def update_customization(
    vehicle_id: uuid.UUID,
    body: BikeCustomizationUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    data = body.model_dump(exclude_none=True)
    bike = await svc.update_customization(player.id, vehicle_id, data)
    return SuccessResponse(
        message="Customization updated",
        data=BikeCustomizationResponse.model_validate(bike),
    )


@router.post("/{vehicle_id}/upgrade")
async def upgrade_component(
    vehicle_id: uuid.UUID,
    body: BikeUpgradeRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.upgrade_component(player.id, vehicle_id, body.component, body.target_level)
    return SuccessResponse(message="Component upgraded", data=result)


@router.get("/{vehicle_id}/performance")
async def get_performance(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    stats = await svc.get_performance_stats(vehicle_id)
    return SuccessResponse(message="Performance stats retrieved", data=stats)


# ── Fuel ───────────────────────────────────────────────────────────────────────


@router.get("/{vehicle_id}/fuel")
async def get_fuel_info(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    info = await svc.get_fuel_info(vehicle_id)
    return SuccessResponse(message="Fuel info retrieved", data=info)


@router.post("/{vehicle_id}/fuel")
async def purchase_fuel(
    vehicle_id: uuid.UUID,
    body: BikeRefuelRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.purchase_fuel(player.id, vehicle_id, body.station_id, body.fuel_liters)
    return SuccessResponse(message="Fuel purchased", data=result)


# ── Damage / Repair ────────────────────────────────────────────────────────────


@router.get("/{vehicle_id}/damage")
async def get_damage_report(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    report = await svc.get_damage_report(vehicle_id)
    return SuccessResponse(message="Damage report retrieved", data=report)


@router.post("/{vehicle_id}/damage")
async def apply_damage(
    vehicle_id: uuid.UUID,
    body: dict,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.apply_damage(player.id, vehicle_id, body["damage_type"], body["damage_amount"])
    return SuccessResponse(message="Damage applied", data=result)


@router.get("/{vehicle_id}/repair/cost")
async def get_repair_cost(
    vehicle_id: uuid.UUID,
    repair_type: str,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    cost = await svc.get_repair_cost(vehicle_id, repair_type)
    return SuccessResponse(message="Repair cost calculated", data=cost)


@router.post("/{vehicle_id}/repair")
async def repair_bike(
    vehicle_id: uuid.UUID,
    body: BikeRepairRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.repair_bike(player.id, vehicle_id, body.repair_type)
    return SuccessResponse(message=result["message"], data=result)


# ── Insurance ──────────────────────────────────────────────────────────────────


@router.get("/{vehicle_id}/insurance")
async def get_insurance(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    insurance = await svc.get_insurance(vehicle_id)
    return SuccessResponse(
        message="Insurance retrieved",
        data=BikeInsuranceResponse.model_validate(insurance) if insurance else None,
    )


@router.post("/{vehicle_id}/insurance")
async def purchase_insurance(
    vehicle_id: uuid.UUID,
    body: BikeInsuranceCreate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_bike_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.purchase_insurance(player.id, vehicle_id, body.tier)
    return SuccessResponse(
        message=result["message"],
        data=BikeInsuranceResponse.model_validate(result["insurance"]),
    )
