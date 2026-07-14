"""Vehicle API endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.garage import GarageRepository
from app.repositories.player import PlayerRepository
from app.repositories.vehicle import VehicleRepository
from app.schemas.common import SuccessResponse
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleDetailResponse,
    VehicleResponse,
    VehicleUpdate,
)
from app.services.garage import GarageService
from app.services.vehicle import VehicleService

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def _get_vehicle_service(session: AsyncSession) -> VehicleService:
    player_repo = PlayerRepository(session)
    vehicle_repo = VehicleRepository(session)
    garage_repo = GarageRepository(session)
    return VehicleService(player_repo, vehicle_repo, garage_repo)


def _to_detail(data: dict) -> VehicleDetailResponse:
    """Convert flat vehicle dict to nested VehicleDetailResponse."""
    vehicle_fields = {k: v for k, v in data.items() if k not in ("bike", "car")}
    return VehicleDetailResponse(
        vehicle=VehicleResponse(**vehicle_fields),
        bike=data.get("bike"),
        car=data.get("car"),
    )


# ── List Vehicles ──────────────────────────────────────────────────────────────


@router.get("/", response_model=SuccessResponse[list[VehicleResponse]])
async def list_vehicles(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[list[VehicleResponse]]:
    """List all vehicles for the authenticated player."""
    svc = _get_vehicle_service(session)
    vehicles = await svc.get_vehicles(account_id=uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Vehicles retrieved successfully",
        data=[VehicleResponse(**v) for v in vehicles],
    )


# ── Buy Vehicle ────────────────────────────────────────────────────────────────


@router.post("/", status_code=201, response_model=SuccessResponse[VehicleDetailResponse])
async def buy_vehicle(
    body: VehicleCreate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[VehicleDetailResponse]:
    """Purchase a new vehicle."""
    svc = _get_vehicle_service(session)
    result = await svc.buy_vehicle(
        account_id=uuid.UUID(current_user["sub"]),
        vehicle_type=body.vehicle_type,
        brand=body.brand,
        model=body.model,
        year=body.year,
        vin=body.vin,
        license_plate=body.license_plate,
        purchase_price=body.purchase_price,
    )
    return SuccessResponse(
        message="Vehicle purchased successfully",
        data=_to_detail(result),
    )


# ── Get Vehicle Detail ─────────────────────────────────────────────────────────


@router.get("/{vehicle_id}", response_model=SuccessResponse[VehicleDetailResponse])
async def get_vehicle(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[VehicleDetailResponse]:
    """Get detailed vehicle information including bike/car upgrades."""
    svc = _get_vehicle_service(session)
    result = await svc.get_vehicle(
        account_id=uuid.UUID(current_user["sub"]),
        vehicle_id=vehicle_id,
    )
    return SuccessResponse(
        message="Vehicle retrieved successfully",
        data=_to_detail(result),
    )


# ── Update Vehicle ─────────────────────────────────────────────────────────────


@router.patch("/{vehicle_id}", response_model=SuccessResponse[VehicleDetailResponse])
async def update_vehicle(
    vehicle_id: uuid.UUID,
    body: VehicleUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[VehicleDetailResponse]:
    """Update vehicle details."""
    svc = _get_vehicle_service(session)
    result = await svc.update_vehicle(
        account_id=uuid.UUID(current_user["sub"]),
        vehicle_id=vehicle_id,
        **body.model_dump(exclude_none=True),
    )
    return SuccessResponse(
        message="Vehicle updated successfully",
        data=_to_detail(result),
    )


# ── Sell Vehicle ───────────────────────────────────────────────────────────────


@router.delete("/{vehicle_id}")
async def sell_vehicle(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[dict]:
    """Sell a vehicle."""
    svc = _get_vehicle_service(session)
    result = await svc.sell_vehicle(
        account_id=uuid.UUID(current_user["sub"]),
        vehicle_id=vehicle_id,
    )
    return SuccessResponse(
        message="Vehicle sold successfully",
        data=result,
    )


# ── Store in Garage ────────────────────────────────────────────────────────────


@router.post("/{vehicle_id}/garage/store", response_model=SuccessResponse[VehicleDetailResponse])
async def store_in_garage(
    vehicle_id: uuid.UUID,
    garage_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[VehicleDetailResponse]:
    """Store a vehicle in a garage."""
    svc = _get_vehicle_service(session)
    result = await svc.store_in_garage(
        account_id=uuid.UUID(current_user["sub"]),
        vehicle_id=vehicle_id,
        garage_id=garage_id,
    )
    return SuccessResponse(
        message="Vehicle stored in garage successfully",
        data=_to_detail(result),
    )


# ── Remove from Garage ────────────────────────────────────────────────────────


@router.post("/{vehicle_id}/garage/remove", response_model=SuccessResponse[VehicleDetailResponse])
async def remove_from_garage(
    vehicle_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[VehicleDetailResponse]:
    """Remove a vehicle from its garage."""
    svc = _get_vehicle_service(session)
    result = await svc.remove_from_garage(
        account_id=uuid.UUID(current_user["sub"]),
        vehicle_id=vehicle_id,
    )
    return SuccessResponse(
        message="Vehicle removed from garage successfully",
        data=_to_detail(result),
    )
