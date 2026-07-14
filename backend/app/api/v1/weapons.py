"""Weapon API endpoints — full weapon system."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.common import SuccessResponse
from app.schemas.weapon import (
    AmmoPurchaseRequest,
    WeaponAttachmentRequest,
    WeaponAttachmentResponse,
    WeaponAmmunitionResponse,
    WeaponBuyRequest,
    WeaponEquipRequest,
    WeaponListResponse,
    WeaponReloadRequest,
    WeaponRepairCostResponse,
    WeaponRepairRequest,
    WeaponRepairResponse,
    WeaponResponse,
    WeaponSellRequest,
    WeaponStatsResponse,
)
from app.services.weapon import WeaponService

router = APIRouter(prefix="/weapons", tags=["Weapons"])


def _get_weapon_service(session: AsyncSession) -> WeaponService:
    return WeaponService(session)


# ── Catalog ──────────────────────────────────────────────────────────────────


@router.get("/", response_model=SuccessResponse[list[WeaponResponse]])
async def list_weapons(
    weapon_type: str | None = None,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    weapons = await svc.get_all_weapons(weapon_type=weapon_type)
    return SuccessResponse(
        message="Weapons retrieved",
        data=[WeaponResponse.model_validate(w) for w in weapons],
    )


@router.get("/{weapon_id}", response_model=SuccessResponse[WeaponResponse])
async def get_weapon(
    weapon_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    weapon = await svc.get_weapon(weapon_id)
    return SuccessResponse(
        message="Weapon retrieved",
        data=WeaponResponse.model_validate(weapon),
    )


# ── Purchase / Sell ──────────────────────────────────────────────────────────


@router.post("/buy", status_code=201)
async def buy_weapon(
    body: WeaponBuyRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.buy_weapon(player.id, body.weapon_id)
    return SuccessResponse(
        message=result["message"],
        data={
            "player_weapon_id": str(result["player_weapon"].id),
            "cost": result["cost"],
        },
    )


@router.post("/sell")
async def sell_weapon(
    body: WeaponSellRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.sell_weapon(player.id, body.player_weapon_id)
    return SuccessResponse(message=result["message"], data=result)


# ── Player Weapons ───────────────────────────────────────────────────────────


@router.get("/inventory/list")
async def list_player_weapons(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    weapons = await svc.get_player_weapons(player.id)
    return SuccessResponse(message="Player weapons retrieved", data=weapons)


@router.post("/equip")
async def equip_weapon(
    body: WeaponEquipRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.equip_weapon(
        player.id, body.player_weapon_id, body.equip
    )
    return SuccessResponse(message=result["message"], data=result)


# ── Ammunition ───────────────────────────────────────────────────────────────


@router.get("/ammo/inventory")
async def get_ammo_inventory(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    ammo = await svc.get_ammo_inventory(player.id)
    return SuccessResponse(
        message="Ammo inventory retrieved",
        data=[WeaponAmmunitionResponse.model_validate(a) for a in ammo],
    )


@router.post("/ammo/buy")
async def purchase_ammo(
    body: AmmoPurchaseRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.purchase_ammo(player.id, body.ammo_type, body.quantity)
    return SuccessResponse(message="Ammo purchased", data=result)


@router.post("/reload")
async def reload_weapon(
    body: WeaponReloadRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.reload_weapon(player.id, body.player_weapon_id)
    return SuccessResponse(message=result["message"], data=result)


# ── Durability ───────────────────────────────────────────────────────────────


@router.post("/durability/reduce")
async def reduce_durability(
    player_weapon_id: uuid.UUID,
    amount: float = 1.0,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.reduce_durability(player.id, player_weapon_id, amount)
    return SuccessResponse(message=result["message"], data=result)


@router.get("/{player_weapon_id}/repair/cost")
async def get_repair_cost(
    player_weapon_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    cost = await svc.get_repair_cost(player.id, player_weapon_id)
    return SuccessResponse(
        message="Repair cost calculated",
        data=WeaponRepairCostResponse(**cost),
    )


@router.post("/repair")
async def repair_weapon(
    body: WeaponRepairRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.repair_weapon(player.id, body.player_weapon_id)
    return SuccessResponse(
        message=result["message"],
        data=WeaponRepairResponse(**result),
    )


# ── Attachments ──────────────────────────────────────────────────────────────


@router.get("/{player_weapon_id}/attachments")
async def get_attachments(
    player_weapon_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    attachment = await svc.get_attachments(player.id, player_weapon_id)
    return SuccessResponse(
        message="Attachments retrieved",
        data=WeaponAttachmentResponse.model_validate(attachment)
        if attachment
        else None,
    )


@router.post("/{player_weapon_id}/attachments/add")
async def add_attachment(
    player_weapon_id: uuid.UUID,
    body: WeaponAttachmentRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.add_attachment(
        player.id, player_weapon_id, body.attachment_type
    )
    return SuccessResponse(message=result["message"], data=result)


@router.post("/{player_weapon_id}/attachments/remove")
async def remove_attachment(
    player_weapon_id: uuid.UUID,
    body: WeaponAttachmentRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    result = await svc.remove_attachment(
        player.id, player_weapon_id, body.attachment_type
    )
    return SuccessResponse(message=result["message"], data=result)


# ── Stats ────────────────────────────────────────────────────────────────────


@router.get("/{player_weapon_id}/stats")
async def get_weapon_stats(
    player_weapon_id: uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_weapon_service(session)
    account_id = uuid.UUID(current_user["sub"])
    player = await svc._get_player_or_raise(account_id)
    stats = await svc.get_weapon_stats(player.id, player_weapon_id)
    return SuccessResponse(
        message="Weapon stats retrieved",
        data=WeaponStatsResponse(**stats),
    )
