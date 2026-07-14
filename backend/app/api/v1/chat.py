"""Chat API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/channels")
async def get_channels():
    """Get available chat channels."""
    raise NotImplementedError


@router.get("/messages")
async def get_messages():
    """Get recent messages."""
    raise NotImplementedError


@router.post("/send")
async def send_message():
    """Send a message."""
    raise NotImplementedError


@router.delete("/message/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: str):
    """Delete a message."""
    raise NotImplementedError
