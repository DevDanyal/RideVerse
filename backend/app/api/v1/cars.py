"""Car API endpoints — full car system."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.car import (
    CarCustomizationResponse,
    CarCustomizationUpdate,
    CarDamageReport,
    CarInsuranceCreate,
    CarInsuranceResponse,
    CarListResponse,
    CarPerformanceStats,
    CarPurchaseRequest,
    CarRefuelRequest,
    CarRepairRequest,
    CarRepairResponse,
    CarSellResponse,
    CarUpgradeRequest,
    CarVariantListResponse,
    CarVariantResponse,
    FuelStationResponse,
    SuccessResponse,
    VehicleResponse,
)
from app.services.car import CarService

router = APIRouter(prefix="/cars", tags=["Cars"])


def _get_car_service(session: AsyncSession) -> CarService:
    return CarService(session)


# ── Variants ───────────────────────────────────────────────────────────────────


@router.get("/variants", response_model=SuccessResponse[list[CarVariantResponse]])
async def list_variants(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    variants = await svc.get_variants()
    return SuccessResponse(message="Variants retrieved", data=[CarVariantResponse.model_validate(v) for v in variants])


@router.get("/variants/{variant_id}", response_model=SuccessResponse[CarVariantResponse])
async def get_variant(
    variant_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    variant = await svc.get_variant(variant_id)
    return SuccessResponse(message="Variant retrieved", data=CarVariantResponse.model_validate(variant))


# ── Purchase / Sell ────────────────────────────────────────────────────────────


@router.post("/", status_code=201)
async def purchase_car(
    body: CarPurchaseRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.purchase_car(player.id, body.variant_id, body.name)
    return SuccessResponse(
        message="Car purchased successfully",
        data={
            "vehicle": VehicleResponse.model_validate(result["vehicle"]),
            "variant": CarVariantResponse.model_validate(result["variant"]),
        },
    )


@router.delete("/{vehicle_id}")
async def sell_car(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.sell_car(player.id, vehicle_id)
    return SuccessResponse(message=result["message"], data=result)


# ── List / Detail ──────────────────────────────────────────────────────────────


@router.get("/", response_model=SuccessResponse[list])
async def list_cars(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    cars = await svc.get_player_cars(player.id)
    return SuccessResponse(message="Cars retrieved", data=cars)


@router.get("/{vehicle_id}")
async def get_car_detail(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    detail = await svc.get_car_detail(player.id, vehicle_id)
    return SuccessResponse(message="Car detail retrieved", data=detail)


# ── Customization ──────────────────────────────────────────────────────────────


@router.patch("/{vehicle_id}/customization")
async def update_customization(
    vehicle_id: uuid.UUID,
    body: CarCustomizationUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    data = body.model_dump(exclude_none=True)
    car = await svc.update_customization(player.id, vehicle_id, data)
    return SuccessResponse(
        message="Customization updated",
        data=CarCustomizationResponse.model_validate(car),
    )


@router.post("/{vehicle_id}/upgrade")
async def upgrade_component(
    vehicle_id: uuid.UUID,
    body: CarUpgradeRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
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
    svc = _get_car_service(session)
    stats = await svc.get_performance_stats(vehicle_id)
    return SuccessResponse(message="Performance stats retrieved", data=stats)


# ── Fuel ───────────────────────────────────────────────────────────────────────


@router.get("/{vehicle_id}/fuel")
async def get_fuel_info(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    info = await svc.get_fuel_info(vehicle_id)
    return SuccessResponse(message="Fuel info retrieved", data=info)


@router.post("/{vehicle_id}/fuel")
async def purchase_fuel(
    vehicle_id: uuid.UUID,
    body: CarRefuelRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
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
    svc = _get_car_service(session)
    report = await svc.get_damage_report(vehicle_id)
    return SuccessResponse(message="Damage report retrieved", data=report)


@router.post("/{vehicle_id}/damage")
async def apply_damage(
    vehicle_id: uuid.UUID,
    body: dict,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
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
    svc = _get_car_service(session)
    cost = await svc.get_repair_cost(vehicle_id, repair_type)
    return SuccessResponse(message="Repair cost calculated", data=cost)


@router.post("/{vehicle_id}/repair")
async def repair_car(
    vehicle_id: uuid.UUID,
    body: CarRepairRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.repair_car(player.id, vehicle_id, body.repair_type)
    return SuccessResponse(message=result["message"], data=result)


# ── Insurance ──────────────────────────────────────────────────────────────────


@router.get("/{vehicle_id}/insurance")
async def get_insurance(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    insurance = await svc.get_insurance(vehicle_id)
    return SuccessResponse(
        message="Insurance retrieved",
        data=CarInsuranceResponse.model_validate(insurance) if insurance else None,
    )


@router.post("/{vehicle_id}/insurance")
async def purchase_insurance(
    vehicle_id: uuid.UUID,
    body: CarInsuranceCreate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_car_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.purchase_insurance(player.id, vehicle_id, body.tier)
    return SuccessResponse(
        message=result["message"],
        data=CarInsuranceResponse.model_validate(result["insurance"]),
    )
