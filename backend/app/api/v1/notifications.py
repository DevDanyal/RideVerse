"""Notification API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def get_notifications():
    """Get player notifications."""
    raise NotImplementedError


@router.post("/read")
async def mark_read():
    """Mark notification as read."""
    raise NotImplementedError


@router.post("/read-all")
async def mark_all_read():
    """Mark all notifications as read."""
    raise NotImplementedError


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: str):
    """Delete a notification."""
    raise NotImplementedError
