"""Business API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/businesses", tags=["Businesses"])


@router.get("/")
async def list_businesses():
    """List available businesses."""
    raise NotImplementedError


@router.post("/buy")
async def buy_business():
    """Buy a business."""
    raise NotImplementedError


@router.post("/sell")
async def sell_business():
    """Sell a business."""
    raise NotImplementedError


@router.get("/{business_id}")
async def get_business(business_id: str):
    """Get business details."""
    raise NotImplementedError


@router.patch("/{business_id}")
async def upgrade_business(business_id: str):
    """Upgrade a business."""
    raise NotImplementedError


@router.get("/income")
async def income_report():
    """Get income report."""
    raise NotImplementedError
