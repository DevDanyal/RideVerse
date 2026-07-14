"""Mission API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/missions", tags=["Missions"])


@router.get("/")
async def available_missions():
    """Get available missions."""
    raise NotImplementedError


@router.get("/{mission_id}")
async def get_mission(mission_id: str):
    """Get mission details."""
    raise NotImplementedError


@router.post("/start")
async def start_mission():
    """Start a mission."""
    raise NotImplementedError


@router.post("/complete")
async def complete_mission():
    """Complete a mission."""
    raise NotImplementedError


@router.post("/cancel")
async def cancel_mission():
    """Cancel a mission."""
    raise NotImplementedError


@router.get("/history")
async def mission_history():
    """Get mission history."""
    raise NotImplementedError


@router.get("/daily")
async def daily_missions():
    """Get daily missions."""
    raise NotImplementedError


@router.get("/weekly")
async def weekly_missions():
    """Get weekly missions."""
    raise NotImplementedError
