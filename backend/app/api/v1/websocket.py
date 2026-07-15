"""WebSocket API endpoints — authenticated game WS connection + REST admin endpoints."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.models.multiplayer import WSEventType
from app.repositories.auth import AuthRepository
from app.schemas.common import SuccessResponse
from app.schemas.multiplayer import (
    MultiplayerRoomCreateRequest,
    MultiplayerRoomListResponse,
    MultiplayerRoomResponse,
    MultiplayerRoomUpdateRequest,
    MultiplayerStatsResponse,
    WebSocketSessionResponse,
)
from app.services.multiplayer import MultiplayerService
from app.services.websocket_dispatcher import WebSocketDispatcher
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multiplayer", tags=["Multiplayer"])

# ── Dispatcher singleton ───────────────────────────────────────────────────────

_dispatcher = WebSocketDispatcher(ws_manager)
_dispatcher.register_all()


# ── WebSocket Connection ───────────────────────────────────────────────────────

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    """Authenticated WebSocket endpoint for real-time multiplayer.

    Clients connect via ws://host/api/v1/multiplayer/ws/<jwt_token>.
    The JWT is validated on connect; on failure the socket is closed immediately.
    """
    from app.core.security import verify_token

    payload = verify_token(token)
    if payload is None or payload.get("type") != "access":
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    player_id = uuid.UUID(payload["sub"])

    await websocket.accept()
    connection_id = str(uuid.uuid4())

    # Look up display_name via auth repo
    display_name = "Player"
    async with get_db_session() as session:
        repo = AuthRepository(session)
        account = await repo.get_account_by_id(player_id)
        if account is not None and hasattr(account, "player") and account.player is not None:
            display_name = account.player.display_name
        elif account is not None:
            display_name = account.username

    # Register in connection manager
    info = await ws_manager.connect(
        player_id=player_id,
        display_name=display_name,
        websocket=websocket,
        connection_id=connection_id,
    )

    # Send auth success
    await ws_manager.send_to_player(player_id, {
        "event": WSEventType.AUTH_SUCCESS,
        "data": {
            "player_id": str(player_id),
            "display_name": display_name,
            "connection_id": connection_id,
        },
    })

    logger.info("WS connected: %s (%s)", player_id, connection_id)

    try:
        while True:
            raw = await websocket.receive_json()
            await _dispatcher.dispatch(info, raw)
    except WebSocketDisconnect:
        logger.info("WS client disconnected: %s", player_id)
    except Exception:
        logger.exception("WS error for player %s", player_id)
    finally:
        await ws_manager.disconnect(player_id)


# ── REST Endpoints ─────────────────────────────────────────────────────────────

@router.get("/rooms", response_model=MultiplayerRoomListResponse)
async def list_rooms(
    room_type: str | None = Query(None),
    region: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _user: dict[str, Any] = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> MultiplayerRoomListResponse:
    """List available multiplayer rooms."""
    service = MultiplayerService(session)
    result = await service.list_rooms(
        room_type=room_type, region=region, page=page, per_page=per_page
    )
    return MultiplayerRoomListResponse(**result)


@router.post("/rooms", response_model=SuccessResponse[MultiplayerRoomResponse])
async def create_room(
    body: MultiplayerRoomCreateRequest,
    user: dict[str, Any] = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[MultiplayerRoomResponse]:
    """Create a new multiplayer room via REST."""
    service = MultiplayerService(session)
    player_id = uuid.UUID(user["sub"])
    result = await service.create_room(
        player_id=player_id,
        room_name=body.room_name,
        room_type=body.room_type.value,
        max_players=body.max_players,
        region=body.region,
        password=body.password,
        map_name=body.map_name,
    )
    return SuccessResponse(data=MultiplayerRoomResponse(**result))


@router.get("/rooms/{room_id}", response_model=SuccessResponse[MultiplayerRoomResponse])
async def get_room(
    room_id: uuid.UUID,
    _user: dict[str, Any] = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[MultiplayerRoomResponse]:
    """Get details of a specific room."""
    service = MultiplayerService(session)
    result = await service.get_room(room_id)
    return SuccessResponse(data=MultiplayerRoomResponse(**result))


@router.patch("/rooms/{room_id}", response_model=SuccessResponse[MultiplayerRoomResponse])
async def update_room(
    room_id: uuid.UUID,
    body: MultiplayerRoomUpdateRequest,
    user: dict[str, Any] = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[MultiplayerRoomResponse]:
    """Update room settings (host only)."""
    service = MultiplayerService(session)
    player_id = uuid.UUID(user["sub"])
    result = await service.update_room(
        room_id=room_id,
        player_id=player_id,
        room_name=body.room_name,
        max_players=body.max_players,
        room_status=body.room_status.value if body.room_status else None,
        map_name=body.map_name,
    )
    return SuccessResponse(data=MultiplayerRoomResponse(**result))


@router.delete("/rooms/{room_id}")
async def delete_room(
    room_id: uuid.UUID,
    user: dict[str, Any] = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[None]:
    """Delete a room (host only)."""
    service = MultiplayerService(session)
    player_id = uuid.UUID(user["sub"])
    await service.delete_room(room_id, player_id)
    return SuccessResponse(message="Room deleted")


@router.get("/sessions", response_model=SuccessResponse[list[WebSocketSessionResponse]])
async def get_sessions(
    user: dict[str, Any] = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[list[WebSocketSessionResponse]]:
    """Get all WebSocket sessions for the current user."""
    service = MultiplayerService(session)
    player_id = uuid.UUID(user["sub"])
    sessions = await service.get_player_sessions(player_id)
    return SuccessResponse(data=[WebSocketSessionResponse(**s) for s in sessions])


@router.get("/stats", response_model=SuccessResponse[MultiplayerStatsResponse])
async def get_stats(
    _user: dict[str, Any] = Depends(get_current_active_user),
) -> SuccessResponse[MultiplayerStatsResponse]:
    """Get multiplayer statistics."""
    stats = ws_manager.get_stats()
    return SuccessResponse(data=MultiplayerStatsResponse(**stats))
