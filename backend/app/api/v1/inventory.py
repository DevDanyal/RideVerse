"""Inventory API endpoints."""
from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.inventory import InventoryRepository
from app.repositories.player import PlayerRepository
from app.schemas.common import SuccessResponse
from app.schemas.inventory import InventoryItemResponse, InventoryResponse
from app.services.inventory import InventoryService

router = APIRouter(prefix="/players/me/inventory", tags=["Inventory"])


def _get_inventory_service(session: AsyncSession) -> InventoryService:
    player_repo = PlayerRepository(session)
    inventory_repo = InventoryRepository(session)
    return InventoryService(player_repo, inventory_repo)


# ── Get Inventory ──────────────────────────────────────────────────────────────


@router.get("", response_model=SuccessResponse[InventoryResponse])
async def get_inventory(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[InventoryResponse]:
    """Get the authenticated player's inventory."""
    svc = _get_inventory_service(session)
    inventory = await svc.get_inventory(account_id=_uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Inventory retrieved successfully",
        data=InventoryResponse(
            id=inventory["id"],
            player_id=inventory["player_id"],
            max_slots=inventory["max_slots"],
            used_slots=inventory["used_slots"],
            total_weight=inventory["total_weight"],
        ),
    )


# ── Get Inventory Items ───────────────────────────────────────────────────────


@router.get("/items", response_model=SuccessResponse[list[InventoryItemResponse]])
async def get_items(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[list[InventoryItemResponse]]:
    """Get all items in the authenticated player's inventory."""
    svc = _get_inventory_service(session)
    inventory = await svc.get_inventory(account_id=_uuid.UUID(current_user["sub"]))
    items = inventory.get("items", [])
    return SuccessResponse(
        message="Items retrieved successfully",
        data=[InventoryItemResponse(**item) for item in items],
    )
