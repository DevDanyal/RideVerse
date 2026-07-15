"""WebSocket Event Dispatcher — routes incoming WS messages to handlers."""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

from app.models.multiplayer import WSEventType
from app.services.websocket_manager import ConnectionInfo, ConnectionManager

logger = logging.getLogger(__name__)

HandlerFunc = Callable[
    [ConnectionInfo, dict[str, Any], "WebSocketDispatcher"],
    Coroutine[Any, Any, None],
]


class WebSocketDispatcher:
    """Routes WebSocket events to registered handler functions."""

    def __init__(self, manager: ConnectionManager) -> None:
        self._manager = manager
        self._handlers: dict[str, HandlerFunc] = {}

    def register(self, event_type: WSEventType, handler: HandlerFunc) -> None:
        """Register a handler for a specific event type."""
        self._handlers[event_type.value] = handler
        logger.debug("Registered handler for %s", event_type.value)

    def register_all(self) -> None:
        """Register all built-in event handlers."""
        self.register(WSEventType.PING, self._handle_ping)
        self.register(WSEventType.POSITION_UPDATE, self._handle_position_update)
        self.register(WSEventType.VEHICLE_UPDATE, self._handle_vehicle_update)
        self.register(WSEventType.CHAT_SEND, self._handle_chat_send)
        self.register(WSEventType.ROOM_CREATE, self._handle_room_create)
        self.register(WSEventType.ROOM_JOIN, self._handle_room_join)
        self.register(WSEventType.ROOM_LEAVE, self._handle_room_leave)
        self.register(WSEventType.ROOM_LIST, self._handle_room_list)
        self.register(WSEventType.PRESENCE_UPDATE, self._handle_presence_update)
        self.register(WSEventType.NOTIFICATION_ACK, self._handle_notification_ack)

    async def dispatch(
        self,
        conn: ConnectionInfo,
        raw_message: dict[str, Any],
    ) -> None:
        """Dispatch a raw WebSocket message to the appropriate handler."""
        event_type = raw_message.get("event", "")
        data = raw_message.get("data", {})

        if not self._manager.check_rate_limit(conn.player_id):
            await self._manager.send_to_player(conn.player_id, {
                "event": WSEventType.RATE_LIMITED,
                "data": {"retry_after_ms": 60000},
            })
            return

        handler = self._handlers.get(event_type)
        if handler is None:
            await self._manager.send_to_player(conn.player_id, {
                "event": WSEventType.ERROR,
                "data": {
                    "error_code": "UNKNOWN_EVENT",
                    "message": f"Unknown event type: {event_type}",
                },
            })
            return

        try:
            await handler(conn, data, self)
        except Exception:
            logger.exception("Error handling event %s from player %s", event_type, conn.player_id)
            await self._manager.send_to_player(conn.player_id, {
                "event": WSEventType.ERROR,
                "data": {
                    "error_code": "HANDLER_ERROR",
                    "message": "An error occurred while processing your request",
                },
            })

    # ── Built-in Handlers ──────────────────────────────────────────────────────

    async def _handle_ping(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Respond to a client ping."""
        ts = data.get("ts", time.time())
        await self._manager.handle_heartbeat(conn.player_id, ts)
        await self._manager.send_to_player(conn.player_id, {
            "event": WSEventType.PONG,
            "data": {"ts": ts},
        })

    async def _handle_position_update(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Broadcast position update to room members."""
        if conn.room_id is None:
            return

        broadcast = {
            "event": WSEventType.POSITION_BROADCAST,
            "data": {
                "player_id": str(conn.player_id),
                "display_name": conn.display_name,
                **data,
            },
        }
        await self._manager.broadcast_to_room(
            conn.room_id,
            broadcast,
            exclude_player=conn.player_id,
        )

    async def _handle_vehicle_update(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Broadcast vehicle state update to room members."""
        if conn.room_id is None:
            return

        broadcast = {
            "event": WSEventType.VEHICLE_BROADCAST,
            "data": {
                "player_id": str(conn.player_id),
                **data,
            },
        }
        await self._manager.broadcast_to_room(
            conn.room_id,
            broadcast,
            exclude_player=conn.player_id,
        )

    async def _handle_chat_send(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Process and broadcast a chat message."""
        if conn.room_id is None:
            await self._manager.send_to_player(conn.player_id, {
                "event": WSEventType.ERROR,
                "data": {"error_code": "NOT_IN_ROOM", "message": "You must be in a room to chat"},
            })
            return

        message_text = data.get("message", "").strip()
        if not message_text or len(message_text) > 500:
            await self._manager.send_to_player(conn.player_id, {
                "event": WSEventType.ERROR,
                "data": {"error_code": "INVALID_MESSAGE", "message": "Message must be 1-500 characters"},
            })
            return

        chat_msg = {
            "event": WSEventType.CHAT_MESSAGE,
            "data": {
                "message_id": str(uuid.uuid4()),
                "player_id": str(conn.player_id),
                "display_name": conn.display_name,
                "message": message_text,
                "message_type": data.get("message_type", "chat"),
                "room_id": str(conn.room_id),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        await self._manager.broadcast_to_room(conn.room_id, chat_msg)

    async def _handle_room_create(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Create a new room."""
        room_name = data.get("room_name", "").strip()
        if not room_name:
            await self._manager.send_to_player(conn.player_id, {
                "event": WSEventType.ERROR,
                "data": {"error_code": "INVALID_ROOM_NAME", "message": "Room name is required"},
            })
            return

        from app.models.multiplayer import RoomType
        room_type = RoomType(data.get("room_type", RoomType.QUICK_PLAY.value))
        max_players = min(int(data.get("max_players", 16)), 100)
        region = data.get("region", "global")

        room = await self._manager.create_room(
            room_name=room_name,
            room_type=room_type,
            host_player_id=conn.player_id,
            max_players=max_players,
            region=region,
            map_name=data.get("map_name"),
        )

        await self._manager.send_to_player(conn.player_id, {
            "event": WSEventType.ROOM_INFO,
            "data": {
                "id": str(room.id),
                "room_name": room.room_name,
                "room_type": room.room_type.value,
                "room_status": room.room_status.value,
                "max_players": room.max_players,
                "current_player_count": len(room.members),
                "region": room.region,
                "host_player_id": str(room.host_player_id),
                "map_name": room.map_name,
            },
        })

    async def _handle_room_join(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Join an existing room."""
        room_id_str = data.get("room_id")
        if not room_id_str:
            await self._manager.send_to_player(conn.player_id, {
                "event": WSEventType.ERROR,
                "data": {"error_code": "MISSING_ROOM_ID", "message": "room_id is required"},
            })
            return

        room_id = uuid.UUID(room_id_str)
        try:
            room = await self._manager.join_room(
                player_id=conn.player_id,
                room_id=room_id,
                password=data.get("password"),
            )
        except ValueError as exc:
            await self._manager.send_to_player(conn.player_id, {
                "event": WSEventType.ERROR,
                "data": {"error_code": "JOIN_FAILED", "message": str(exc)},
            })
            return

        await self._manager.send_to_player(conn.player_id, {
            "event": WSEventType.ROOM_INFO,
            "data": {
                "id": str(room.id),
                "room_name": room.room_name,
                "room_type": room.room_type.value,
                "room_status": room.room_status.value,
                "max_players": room.max_players,
                "current_player_count": len(room.members),
                "region": room.region,
                "host_player_id": str(room.host_player_id) if room.host_player_id else None,
                "map_name": room.map_name,
            },
        })

        await self._manager.broadcast_to_room(
            room_id,
            {
                "event": WSEventType.PLAYER_JOINED,
                "data": {
                    "player_id": str(conn.player_id),
                    "display_name": conn.display_name,
                    "room_id": str(room_id),
                    "current_player_count": len(room.members),
                },
            },
            exclude_player=conn.player_id,
        )

    async def _handle_room_leave(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Leave the current room."""
        if conn.room_id is None:
            return

        room_id = conn.room_id
        old_room = self._manager.get_room(room_id)

        await self._manager.leave_room(conn.player_id, room_id)

        await self._manager.send_to_player(conn.player_id, {
            "event": WSEventType.ROOM_UPDATE,
            "data": {"room_id": str(room_id), "action": "left"},
        })

        remaining = self._manager.get_room(room_id)
        if remaining is not None:
            await self._manager.broadcast_to_room(
                room_id,
                {
                    "event": WSEventType.PLAYER_LEFT,
                    "data": {
                        "player_id": str(conn.player_id),
                        "display_name": conn.display_name,
                        "room_id": str(room_id),
                        "current_player_count": len(remaining.members),
                    },
                },
            )

    async def _handle_room_list(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """List available rooms."""
        from app.models.multiplayer import RoomType
        room_type = None
        if data.get("room_type"):
            room_type = RoomType(data["room_type"])
        region = data.get("region")

        rooms = self._manager.list_rooms(room_type=room_type, region=region)
        room_list = []
        for room in rooms:
            room_list.append({
                "id": str(room.id),
                "room_name": room.room_name,
                "room_type": room.room_type.value,
                "room_status": room.room_status.value,
                "max_players": room.max_players,
                "current_player_count": len(room.members),
                "region": room.region,
                "map_name": room.map_name,
                "has_password": room.password_hash is not None,
            })

        await self._manager.send_to_player(conn.player_id, {
            "event": WSEventType.ROOM_LIST,
            "data": {"rooms": room_list, "total": len(room_list)},
        })

    async def _handle_presence_update(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Update player presence."""
        from app.models.multiplayer import PresenceStatus
        status_str = data.get("status", PresenceStatus.ONLINE.value)
        status = PresenceStatus(status_str)
        await self._manager.update_presence(
            conn.player_id,
            status,
            status_message=data.get("status_message"),
        )

    async def _handle_notification_ack(
        self,
        conn: ConnectionInfo,
        data: dict[str, Any],
        dispatcher: WebSocketDispatcher,
    ) -> None:
        """Handle notification acknowledgment."""
        notification_id = data.get("notification_id")
        if notification_id:
            logger.debug(
                "Player %s acknowledged notification %s",
                conn.player_id,
                notification_id,
            )
