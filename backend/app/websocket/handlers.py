"""WebSocket message handlers."""

import json
import logging
from fastapi import WebSocket

from app.websocket.manager import manager

logger = logging.getLogger("rideverse.websocket.handlers")


async def handle_chat_message(player_id: str, data: dict) -> None:
    """Handle incoming chat messages."""
    channel = data.get("channel", "global")
    content = data.get("content", "")
    if not content:
        return

    payload = json.dumps({
        "type": "chat",
        "player_id": player_id,
        "channel": channel,
        "content": content,
    })
    await manager.broadcast_to_channel(channel, payload)


async def handle_position_update(player_id: str, data: dict) -> None:
    """Handle player position updates."""
    payload = json.dumps({
        "type": "position",
        "player_id": player_id,
        "x": data.get("x", 0),
        "y": data.get("y", 0),
        "z": data.get("z", 0),
    })
    await manager.broadcast_to_channel("world", payload)


async def handle_vehicle_update(player_id: str, data: dict) -> None:
    """Handle vehicle state updates."""
    payload = json.dumps({
        "type": "vehicle",
        "player_id": player_id,
        "vehicle_id": data.get("vehicle_id"),
        "speed": data.get("speed", 0),
        "heading": data.get("heading", 0),
    })
    await manager.broadcast_to_channel("world", payload)


async def handle_typing(player_id: str, data: dict) -> None:
    """Handle typing indicator."""
    channel = data.get("channel", "global")
    payload = json.dumps({
        "type": "typing",
        "player_id": player_id,
        "channel": channel,
    })
    await manager.broadcast_to_channel(channel, payload)


HANDLERS: dict[str, callable] = {
    "chat": handle_chat_message,
    "position": handle_position_update,
    "vehicle": handle_vehicle_update,
    "typing": handle_typing,
}


async def dispatch_message(player_id: str, raw: str) -> None:
    """Parse and dispatch a raw WebSocket message to the correct handler."""
    try:
        data = json.loads(raw)
        event_type = data.get("type", "")
        handler = HANDLERS.get(event_type)
        if handler:
            await handler(player_id, data)
        else:
            logger.warning("unknown_ws_event type=%s player_id=%s", event_type, player_id)
    except json.JSONDecodeError:
        logger.warning("invalid_json player_id=%s", player_id)
