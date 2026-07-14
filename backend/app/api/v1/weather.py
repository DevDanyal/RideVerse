"""Weather API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current")
async def current_weather():
    """Get current weather."""
    raise NotImplementedError


@router.get("/forecast")
async def weather_forecast():
    """Get weather forecast."""
    raise NotImplementedError
