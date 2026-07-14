"""Friends API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/friends", tags=["Friends"])


@router.get("/")
async def list_friends():
    """Get friend list."""
    raise NotImplementedError


@router.post("/request")
async def send_request():
    """Send friend request."""
    raise NotImplementedError


@router.post("/accept")
async def accept_request():
    """Accept friend request."""
    raise NotImplementedError


@router.post("/reject")
async def reject_request():
    """Reject friend request."""
    raise NotImplementedError


@router.delete("/remove")
async def remove_friend():
    """Remove a friend."""
    raise NotImplementedError


@router.post("/block")
async def block_player():
    """Block a player."""
    raise NotImplementedError


@router.post("/unblock")
async def unblock_player():
    """Unblock a player."""
    raise NotImplementedError


@router.get("/requests")
async def pending_requests():
    """Get pending friend requests."""
    raise NotImplementedError
