"""Shop API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/shops", tags=["Shops"])


@router.get("/")
async def list_shops():
    """Get all shops."""
    raise NotImplementedError


@router.get("/bikes")
async def bike_shop():
    """Get bike shop inventory."""
    raise NotImplementedError


@router.get("/cars")
async def car_shop():
    """Get car shop inventory."""
    raise NotImplementedError


@router.get("/weapons")
async def weapon_shop():
    """Get weapon shop inventory."""
    raise NotImplementedError


@router.post("/purchase")
async def purchase_item():
    """Purchase an item from a shop."""
    raise NotImplementedError


@router.post("/sell")
async def sell_item():
    """Sell an item to a shop."""
    raise NotImplementedError
