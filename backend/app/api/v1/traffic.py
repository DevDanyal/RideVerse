"""Traffic API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/traffic", tags=["Traffic"])


@router.get("/status")
async def traffic_status():
    """Get traffic status."""
    raise NotImplementedError


@router.get("/events")
async def traffic_events():
    """Get traffic events."""
    raise NotImplementedError
