"""WebSocket authentication helper."""

import logging
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("rideverse.websocket.auth")


async def authenticate_websocket(websocket: WebSocket) -> str | None:
    """Authenticate a WebSocket connection via query param or first message.

    Returns the player_id if authentication succeeds, None otherwise.
    """
    token = websocket.query_params.get("token")
    if token:
        player_id = await validate_token(token)
        if player_id:
            return player_id

    # Fallback: expect auth message as first frame
    try:
        data = await websocket.receive_json()
        if data.get("type") == "auth" and "token" in data:
            player_id = await validate_token(data["token"])
            if player_id:
                await websocket.send_json({"type": "auth", "status": "success"})
                return player_id

        await websocket.send_json({
            "type": "auth",
            "status": "error",
            "message": "Invalid credentials",
        })
        return None
    except WebSocketDisconnect:
        return None
    except Exception:
        logger.exception("websocket_auth_error")
        return None


async def validate_token(token: str) -> str | None:
    """Validate a JWT token and return the player_id.

    TODO: Implement actual JWT validation.
    """
    # Placeholder: decode JWT and extract player_id
    return None
