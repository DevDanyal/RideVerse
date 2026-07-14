"""Police API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/police", tags=["Police"])


@router.get("/status")
async def police_status():
    """Get police status."""
    raise NotImplementedError


@router.get("/wanted")
async def wanted_level():
    """Get wanted level."""
    raise NotImplementedError


@router.post("/pay-fine")
async def pay_fine():
    """Pay outstanding fine."""
    raise NotImplementedError


@router.post("/surrender")
async def surrender():
    """Surrender to police."""
    raise NotImplementedError


@router.get("/history")
async def crime_history():
    """Get crime history."""
    raise NotImplementedError
