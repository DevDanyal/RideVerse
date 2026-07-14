"""Bike API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/bikes", tags=["Bikes"])


@router.get("/")
async def list_bikes():
    """List all available bikes."""
    raise NotImplementedError


@router.get("/{bike_id}")
async def get_bike(bike_id: str):
    """Get bike details."""
    raise NotImplementedError


@router.patch("/{bike_id}")
async def customize_bike(bike_id: str):
    """Customize a bike."""
    raise NotImplementedError


@router.post("/{bike_id}/repair")
async def repair_bike(bike_id: str):
    """Repair a bike."""
    raise NotImplementedError


@router.post("/{bike_id}/refuel")
async def refuel_bike(bike_id: str):
    """Refuel a bike."""
    raise NotImplementedError
