"""NPC API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/npcs", tags=["NPCs"])


@router.get("/")
async def list_npcs():
    """Get nearby NPCs."""
    raise NotImplementedError


@router.get("/{npc_id}")
async def get_npc(npc_id: str):
    """Get NPC details."""
    raise NotImplementedError


@router.post("/interact")
async def interact_with_npc():
    """Interact with an NPC."""
    raise NotImplementedError
