"""Weapon API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/weapons", tags=["Weapons"])


@router.get("/")
async def list_weapons():
    """List all weapons."""
    raise NotImplementedError


@router.get("/{weapon_id}")
async def get_weapon(weapon_id: str):
    """Get weapon details."""
    raise NotImplementedError


@router.post("/buy")
async def buy_weapon():
    """Buy a weapon."""
    raise NotImplementedError


@router.post("/sell")
async def sell_weapon():
    """Sell a weapon."""
    raise NotImplementedError


@router.post("/equip")
async def equip_weapon():
    """Equip a weapon."""
    raise NotImplementedError


@router.post("/unequip")
async def unequip_weapon():
    """Unequip a weapon."""
    raise NotImplementedError


@router.post("/reload")
async def reload_weapon():
    """Reload equipped weapon."""
    raise NotImplementedError
