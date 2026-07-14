"""Car API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.get("/")
async def list_cars():
    """List all available cars."""
    raise NotImplementedError


@router.get("/{car_id}")
async def get_car(car_id: str):
    """Get car details."""
    raise NotImplementedError


@router.patch("/{car_id}")
async def customize_car(car_id: str):
    """Customize a car."""
    raise NotImplementedError


@router.post("/{car_id}/repair")
async def repair_car(car_id: str):
    """Repair a car."""
    raise NotImplementedError


@router.post("/{car_id}/refuel")
async def refuel_car(car_id: str):
    """Refuel a car."""
    raise NotImplementedError
