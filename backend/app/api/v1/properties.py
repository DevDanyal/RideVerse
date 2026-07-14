"""Property API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("/")
async def list_properties():
    """List available properties."""
    raise NotImplementedError


@router.post("/buy")
async def buy_property():
    """Buy a property."""
    raise NotImplementedError


@router.post("/sell")
async def sell_property():
    """Sell a property."""
    raise NotImplementedError


@router.get("/{property_id}")
async def get_property(property_id: str):
    """Get property details."""
    raise NotImplementedError


@router.patch("/{property_id}")
async def upgrade_property(property_id: str):
    """Upgrade a property."""
    raise NotImplementedError
