"""Club API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("/")
async def list_clubs():
    """List all clubs."""
    raise NotImplementedError


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_club():
    """Create a new club."""
    raise NotImplementedError


@router.get("/{club_id}")
async def get_club(club_id: str):
    """Get club info."""
    raise NotImplementedError


@router.patch("/{club_id}")
async def update_club(club_id: str):
    """Update club details."""
    raise NotImplementedError


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_club(club_id: str):
    """Delete a club."""
    raise NotImplementedError


@router.post("/invite")
async def invite_player():
    """Invite player to club."""
    raise NotImplementedError


@router.post("/join")
async def join_club():
    """Join a club."""
    raise NotImplementedError


@router.post("/leave")
async def leave_club():
    """Leave current club."""
    raise NotImplementedError


@router.post("/kick")
async def kick_member():
    """Kick a member from club."""
    raise NotImplementedError


@router.get("/members")
async def club_members():
    """Get club members."""
    raise NotImplementedError
