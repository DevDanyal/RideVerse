"""Garage API endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.garage import GarageRepository
from app.repositories.player import PlayerRepository
from app.schemas.common import SuccessResponse
from app.schemas.garage import (
    GarageCreate,
    GarageResponse,
    GarageSlotResponse,
    RetrieveVehicleRequest,
    StoreVehicleRequest,
)
from app.services.garage import GarageService

router = APIRouter(prefix="/garages", tags=["Garages"])


def _get_garage_service(session: AsyncSession) -> GarageService:
    player_repo = PlayerRepository(session)
    garage_repo = GarageRepository(session)
    return GarageService(player_repo, garage_repo)


# ── List Garages ───────────────────────────────────────────────────────────────


@router.get("/", response_model=SuccessResponse[list[GarageResponse]])
async def list_garages(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[list[GarageResponse]]:
    """List all garages for the authenticated player."""
    svc = _get_garage_service(session)
    garages = await svc.get_garages(account_id=uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Garages retrieved successfully",
        data=[GarageResponse(**g) for g in garages],
    )


# ── Get Garage ─────────────────────────────────────────────────────────────────


@router.get("/{garage_id}", response_model=SuccessResponse[GarageResponse])
async def get_garage(
    garage_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[GarageResponse]:
    """Get garage details with slots."""
    svc = _get_garage_service(session)
    result = await svc.get_garage(
        account_id=uuid.UUID(current_user["sub"]),
        garage_id=garage_id,
    )
    return SuccessResponse(
        message="Garage retrieved successfully",
        data=GarageResponse(**result),
    )


# ── Create Garage ──────────────────────────────────────────────────────────────


@router.post("/", status_code=201, response_model=SuccessResponse[GarageResponse])
async def create_garage(
    body: GarageCreate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[GarageResponse]:
    """Purchase a new garage."""
    svc = _get_garage_service(session)
    result = await svc.create_garage(
        account_id=uuid.UUID(current_user["sub"]),
        garage_name=body.garage_name,
        location=body.location,
        purchase_price=body.purchase_price,
    )
    return SuccessResponse(
        message="Garage created successfully",
        data=GarageResponse(**result),
    )


# ── Store Vehicle ──────────────────────────────────────────────────────────────


@router.post("/store", response_model=SuccessResponse[GarageResponse])
async def store_vehicle(
    body: StoreVehicleRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[GarageResponse]:
    """Store a vehicle in a garage."""
    svc = _get_garage_service(session)
    result = await svc.store_vehicle(
        account_id=uuid.UUID(current_user["sub"]),
        garage_id=body.garage_id,
        vehicle_id=body.vehicle_id,
    )
    return SuccessResponse(
        message="Vehicle stored in garage successfully",
        data=GarageResponse(**result),
    )


# ── Retrieve Vehicle ──────────────────────────────────────────────────────────


@router.post("/retrieve", response_model=SuccessResponse[GarageResponse])
async def retrieve_vehicle(
    body: RetrieveVehicleRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[GarageResponse]:
    """Retrieve a vehicle from a garage."""
    svc = _get_garage_service(session)
    result = await svc.retrieve_vehicle(
        account_id=uuid.UUID(current_user["sub"]),
        garage_id=body.garage_id,
        vehicle_id=body.vehicle_id,
    )
    return SuccessResponse(
        message="Vehicle retrieved from garage successfully",
        data=GarageResponse(**result["garage"]),
    )
