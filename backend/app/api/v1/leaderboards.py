"""Leaderboard API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])


@router.get("/")
async def list_leaderboards():
    """Get available leaderboards."""
    raise NotImplementedError


@router.get("/global")
async def global_rankings():
    """Get global rankings."""
    raise NotImplementedError


@router.get("/weekly")
async def weekly_rankings():
    """Get weekly rankings."""
    raise NotImplementedError


@router.get("/monthly")
async def monthly_rankings():
    """Get monthly rankings."""
    raise NotImplementedError


@router.get("/friends")
async def friends_leaderboard():
    """Get friends leaderboard."""
    raise NotImplementedError
