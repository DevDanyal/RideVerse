"""WebSocket Connection Manager — handles connections, rooms, heartbeat, rate limiting."""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from fastapi import WebSocket

from app.models.multiplayer import (
    ConnectionStatus,
    PresenceStatus,
    RoomStatus,
    RoomType,
    WSEventType,
)

logger = logging.getLogger(__name__)


# ── Constants ──────────────────────────────────────────────────────────────────

DEFAULT_HEARTBEAT_INTERVAL_S: float = 30.0
HEARTBEAT_TIMEOUT_S: float = 60.0
DEFAULT_MAX_PLAYERS: int = 16
RATE_LIMIT_WINDOW_S: float = 60.0
RATE_LIMIT_MAX_MESSAGES: int = 120
RECONNECT_GRACE_PERIOD_S: float = 120.0


# ── Connection Info ────────────────────────────────────────────────────────────

class ConnectionInfo:
    """Tracks a single WebSocket connection."""

    __slots__ = (
        "player_id",
        "display_name",
        "connection_id",
        "websocket",
        "room_id",
        "connected_at",
        "last_heartbeat",
        "status",
        "messages_sent",
        "messages_received",
        "rate_limit_count",
        "rate_limit_window_start",
        "seq",
    )

    def __init__(
        self,
        player_id: uuid.UUID,
        display_name: str,
        connection_id: str,
        websocket: WebSocket,
    ) -> None:
        self.player_id = player_id
        self.display_name = display_name
        self.connection_id = connection_id
        self.websocket = websocket
        self.room_id: uuid.UUID | None = None
        self.connected_at = datetime.now(timezone.utc)
        self.last_heartbeat = datetime.now(timezone.utc)
        self.status = ConnectionStatus.CONNECTED
        self.messages_sent = 0
        self.messages_received = 0
        self.rate_limit_count = 0
        self.rate_limit_window_start = time.time()
        self.seq = 0


# ── Room Info ──────────────────────────────────────────────────────────────────

class RoomInfo:
    """In-memory room state."""

    __slots__ = (
        "id",
        "room_name",
        "room_type",
        "room_status",
        "max_players",
        "region",
        "host_player_id",
        "password_hash",
        "map_name",
        "created_at",
        "members",
    )

    def __init__(
        self,
        room_id: uuid.UUID,
        room_name: str,
        room_type: RoomType,
        max_players: int = DEFAULT_MAX_PLAYERS,
        region: str = "global",
        host_player_id: uuid.UUID | None = None,
        password_hash: str | None = None,
        map_name: str | None = None,
    ) -> None:
        self.id = room_id
        self.room_name = room_name
        self.room_type = room_type
        self.room_status = RoomStatus.WAITING
        self.max_players = max_players
        self.region = region
        self.host_player_id = host_player_id
        self.password_hash = password_hash
        self.map_name = map_name
        self.created_at = datetime.now(timezone.utc)
        self.members: set[uuid.UUID] = set()


# ── Connection Manager ─────────────────────────────────────────────────────────

class ConnectionManager:
    """Manages WebSocket connections, rooms, heartbeat, and rate limiting."""

    def __init__(
        self,
        heartbeat_interval_s: float = DEFAULT_HEARTBEAT_INTERVAL_S,
        heartbeat_timeout_s: float = HEARTBEAT_TIMEOUT_S,
        rate_limit_window_s: float = RATE_LIMIT_WINDOW_S,
        rate_limit_max: int = RATE_LIMIT_MAX_MESSAGES,
    ) -> None:
        self._connections: dict[uuid.UUID, ConnectionInfo] = {}
        self._connection_by_id: dict[str, ConnectionInfo] = {}
        self._rooms: dict[uuid.UUID, RoomInfo] = {}
        self._room_by_name: dict[str, uuid.UUID] = {}
        self._player_rooms: dict[uuid.UUID, uuid.UUID] = {}
        self._heartbeat_interval_s = heartbeat_interval_s
        self._heartbeat_timeout_s = heartbeat_timeout_s
        self._rate_limit_window_s = rate_limit_window_s
        self._rate_limit_max = rate_limit_max
        self._presence: dict[uuid.UUID, PresenceStatus] = {}
        self._pending_messages: dict[uuid.UUID, list[dict[str, Any]]] = defaultdict(list)
        self._reconnect_tokens: dict[uuid.UUID, tuple[str, float]] = {}
        self._total_messages: int = 0
        self._peak_concurrent: int = 0

    # ── Connection Management ──────────────────────────────────────────────────

    @property
    def active_connection_count(self) -> int:
        return len(self._connections)

    @property
    def active_room_count(self) -> int:
        return len(self._rooms)

    @property
    def total_messages(self) -> int:
        return self._total_messages

    @property
    def peak_concurrent(self) -> int:
        return self._peak_concurrent

    def get_connection(self, player_id: uuid.UUID) -> ConnectionInfo | None:
        return self._connections.get(player_id)

    def get_connection_by_id(self, connection_id: str) -> ConnectionInfo | None:
        return self._connection_by_id.get(connection_id)

    async def connect(
        self,
        player_id: uuid.UUID,
        display_name: str,
        websocket: WebSocket,
        connection_id: str | None = None,
    ) -> ConnectionInfo:
        """Accept and register a new WebSocket connection."""
        if connection_id is None:
            connection_id = str(uuid.uuid4())

        existing = self._connections.get(player_id)
        if existing is not None:
            await self._cleanup_connection(existing)

        info = ConnectionInfo(
            player_id=player_id,
            display_name=display_name,
            connection_id=connection_id,
            websocket=websocket,
        )
        self._connections[player_id] = info
        self._connection_by_id[connection_id] = info
        self._presence[player_id] = PresenceStatus.ONLINE

        total = len(self._connections)
        if total > self._peak_concurrent:
            self._peak_concurrent = total

        logger.info("Player connected: %s (conn=%s)", player_id, connection_id)
        return info

    async def disconnect(self, player_id: uuid.UUID) -> None:
        """Clean up a disconnected player."""
        info = self._connections.get(player_id)
        if info is None:
            return
        await self._cleanup_connection(info)
        logger.info("Player disconnected: %s", player_id)

    async def _cleanup_connection(self, info: ConnectionInfo) -> None:
        """Internal cleanup when a connection is removed."""
        if info.room_id is not None:
            await self.leave_room(info.player_id, info.room_id)

        self._connections.pop(info.player_id, None)
        self._connection_by_id.pop(info.connection_id, None)
        self._presence[info.player_id] = PresenceStatus.OFFLINE

        try:
            if info.websocket.client_state.name == "CONNECTED":
                await info.websocket.close()
        except Exception:
            pass

    # ── Room Management ────────────────────────────────────────────────────────

    def get_room(self, room_id: uuid.UUID) -> RoomInfo | None:
        return self._rooms.get(room_id)

    def get_player_room(self, player_id: uuid.UUID) -> uuid.UUID | None:
        return self._player_rooms.get(player_id)

    async def create_room(
        self,
        room_name: str,
        room_type: RoomType,
        host_player_id: uuid.UUID,
        max_players: int = DEFAULT_MAX_PLAYERS,
        region: str = "global",
        password_hash: str | None = None,
        map_name: str | None = None,
    ) -> RoomInfo:
        """Create a new room and add the host."""
        room_id = uuid.uuid4()
        room = RoomInfo(
            room_id=room_id,
            room_name=room_name,
            room_type=room_type,
            max_players=max_players,
            region=region,
            host_player_id=host_player_id,
            password_hash=password_hash,
            map_name=map_name,
        )
        room.members.add(host_player_id)
        self._rooms[room_id] = room
        self._room_by_name[room_name] = room_id
        self._player_rooms[host_player_id] = room_id

        conn = self._connections.get(host_player_id)
        if conn is not None:
            conn.room_id = room_id
            self._presence[host_player_id] = PresenceStatus.IN_GAME

        logger.info("Room created: %s (%s) by %s", room_name, room_id, host_player_id)
        return room

    async def join_room(
        self,
        player_id: uuid.UUID,
        room_id: uuid.UUID,
        password: str | None = None,
    ) -> RoomInfo:
        """Add a player to an existing room."""
        room = self._rooms.get(room_id)
        if room is None:
            raise ValueError("Room not found")

        if room.room_status == RoomStatus.FINISHED:
            raise ValueError("Room has already finished")

        if len(room.members) >= room.max_players:
            raise ValueError("Room is full")

        if room.password_hash is not None:
            from app.core.security import get_password_hash
            if password is None or get_password_hash(password) != room.password_hash:
                raise ValueError("Invalid room password")

        existing_room = self._player_rooms.get(player_id)
        if existing_room is not None and existing_room != room_id:
            await self.leave_room(player_id, existing_room)

        room.members.add(player_id)
        self._player_rooms[player_id] = room_id

        conn = self._connections.get(player_id)
        if conn is not None:
            conn.room_id = room_id
            self._presence[player_id] = PresenceStatus.IN_GAME

        logger.info("Player %s joined room %s", player_id, room_id)
        return room

    async def leave_room(self, player_id: uuid.UUID, room_id: uuid.UUID | None = None) -> None:
        """Remove a player from their room."""
        actual_room_id = room_id or self._player_rooms.get(player_id)
        if actual_room_id is None:
            return

        room = self._rooms.get(actual_room_id)
        if room is not None:
            room.members.discard(player_id)
            if len(room.members) == 0:
                await self._destroy_room(actual_room_id)
            elif room.host_player_id == player_id:
                new_host = next(iter(room.members), None)
                if new_host is not None:
                    room.host_player_id = new_host

        self._player_rooms.pop(player_id, None)

        conn = self._connections.get(player_id)
        if conn is not None:
            conn.room_id = None
            self._presence[player_id] = PresenceStatus.ONLINE

        logger.info("Player %s left room %s", player_id, actual_room_id)

    async def _destroy_room(self, room_id: uuid.UUID) -> None:
        """Destroy an empty room."""
        room = self._rooms.pop(room_id, None)
        if room is not None:
            self._room_by_name.pop(room.room_name, None)
            logger.info("Room destroyed: %s", room_id)

    def list_rooms(
        self,
        room_type: RoomType | None = None,
        region: str | None = None,
    ) -> list[RoomInfo]:
        """List available rooms with optional filters."""
        rooms = list(self._rooms.values())
        if room_type is not None:
            rooms = [r for r in rooms if r.room_type == room_type]
        if region is not None:
            rooms = [r for r in rooms if r.region == region]
        return rooms

    # ── Messaging ──────────────────────────────────────────────────────────────

    async def send_to_player(self, player_id: uuid.UUID, message: dict[str, Any]) -> bool:
        """Send a message to a specific player."""
        conn = self._connections.get(player_id)
        if conn is None or conn.websocket.client_state.name != "CONNECTED":
            return False
        try:
            conn.seq += 1
            message["seq"] = conn.seq
            await conn.websocket.send_json(message)
            conn.messages_sent += 1
            self._total_messages += 1
            return True
        except Exception:
            await self.disconnect(player_id)
            return False

    async def send_to_connection(self, connection_id: str, message: dict[str, Any]) -> bool:
        """Send a message to a specific connection."""
        conn = self._connection_by_id.get(connection_id)
        if conn is None:
            return False
        return await self.send_to_player(conn.player_id, message)

    async def broadcast_to_room(
        self,
        room_id: uuid.UUID,
        message: dict[str, Any],
        exclude_player: uuid.UUID | None = None,
    ) -> int:
        """Broadcast a message to all players in a room. Returns count of recipients."""
        room = self._rooms.get(room_id)
        if room is None:
            return 0
        count = 0
        for member_id in room.members:
            if member_id == exclude_player:
                continue
            if await self.send_to_player(member_id, message):
                count += 1
        return count

    async def broadcast_all(self, message: dict[str, Any]) -> int:
        """Broadcast a message to all connected players."""
        count = 0
        for player_id in list(self._connections.keys()):
            if await self.send_to_player(player_id, message):
                count += 1
        return count

    # ── Heartbeat ──────────────────────────────────────────────────────────────

    async def handle_heartbeat(self, player_id: uuid.UUID, timestamp: float) -> None:
        """Process a heartbeat pong from a client."""
        conn = self._connections.get(player_id)
        if conn is not None:
            conn.last_heartbeat = datetime.now(timezone.utc)
            conn.status = ConnectionStatus.CONNECTED

    async def check_heartbeats(self) -> list[uuid.UUID]:
        """Check for timed-out connections. Returns list of timed-out player IDs."""
        now = datetime.now(timezone.utc)
        timed_out: list[uuid.UUID] = []
        for player_id, conn in list(self._connections.items()):
            elapsed = (now - conn.last_heartbeat).total_seconds()
            if elapsed > self._heartbeat_timeout_s:
                conn.status = ConnectionStatus.TIMED_OUT
                timed_out.append(player_id)
                logger.warning(
                    "Heartbeat timeout for player %s (%.1fs since last)",
                    player_id,
                    elapsed,
                )
        for player_id in timed_out:
            await self.disconnect(player_id)
        return timed_out

    # ── Rate Limiting ──────────────────────────────────────────────────────────

    def check_rate_limit(self, player_id: uuid.UUID) -> bool:
        """Check if a player is within the rate limit. Returns True if OK."""
        conn = self._connections.get(player_id)
        if conn is None:
            return False

        now = time.time()
        if now - conn.rate_limit_window_start > self._rate_limit_window_s:
            conn.rate_limit_count = 0
            conn.rate_limit_window_start = now

        conn.rate_limit_count += 1
        return conn.rate_limit_count <= self._rate_limit_max

    def get_rate_limit_remaining(self, player_id: uuid.UUID) -> int:
        """Return how many messages remain in the current rate limit window."""
        conn = self._connections.get(player_id)
        if conn is None:
            return 0

        now = time.time()
        if now - conn.rate_limit_window_start > self._rate_limit_window_s:
            return self._rate_limit_max

        return max(0, self._rate_limit_max - conn.rate_limit_count)

    # ── Presence ───────────────────────────────────────────────────────────────

    def get_presence(self, player_id: uuid.UUID) -> PresenceStatus:
        return self._presence.get(player_id, PresenceStatus.OFFLINE)

    async def update_presence(
        self,
        player_id: uuid.UUID,
        status: PresenceStatus,
        status_message: str | None = None,
    ) -> None:
        """Update a player's presence status."""
        self._presence[player_id] = status
        conn = self._connections.get(player_id)
        if conn is not None:
            await self.send_to_player(player_id, {
                "event": WSEventType.PRESENCE_UPDATE,
                "data": {
                    "status": status.value,
                    "status_message": status_message,
                },
            })

    async def notify_friends_online(self, player_id: uuid.UUID) -> None:
        """Send the list of online friends to a newly connected player."""
        from app.models.friend import Friend, FriendStatus
        # This will be implemented with repo access in the service layer
        # For now, send empty list
        await self.send_to_player(player_id, {
            "event": WSEventType.FRIENDS_ONLINE,
            "data": {"friends": []},
        })

    # ── Reconnection ───────────────────────────────────────────────────────────

    def generate_reconnect_token(self, player_id: uuid.UUID) -> str:
        """Generate a short-lived reconnection token."""
        token = str(uuid.uuid4())
        self._reconnect_tokens[player_id] = (token, time.time())
        return token

    def validate_reconnect_token(self, player_id: uuid.UUID, token: str) -> bool:
        """Validate a reconnection token within the grace period."""
        stored = self._reconnect_tokens.get(player_id)
        if stored is None:
            return False
        stored_token, created_at = stored
        if time.time() - created_at > RECONNECT_GRACE_PERIOD_S:
            self._reconnect_tokens.pop(player_id, None)
            return False
        if stored_token != token:
            return False
        self._reconnect_tokens.pop(player_id, None)
        return True

    # ── Pending Messages (for reconnection) ────────────────────────────────────

    def queue_message(self, player_id: uuid.UUID, message: dict[str, Any]) -> None:
        """Queue a message for a disconnected player."""
        self._pending_messages[player_id].append(message)
        if len(self._pending_messages[player_id]) > 100:
            self._pending_messages[player_id] = self._pending_messages[player_id][-100:]

    async def flush_pending_messages(self, player_id: uuid.UUID) -> int:
        """Send all pending messages to a reconnected player."""
        messages = self._pending_messages.pop(player_id, [])
        count = 0
        for msg in messages:
            if await self.send_to_player(player_id, msg):
                count += 1
        return count

    # ── Statistics ─────────────────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """Return multiplayer statistics."""
        return {
            "total_rooms": len(self._rooms),
            "active_rooms": len([
                r for r in self._rooms.values()
                if r.room_status == RoomStatus.IN_PROGRESS
            ]),
            "total_connections": len(self._connections),
            "active_connections": len([
                c for c in self._connections.values()
                if c.status == ConnectionStatus.CONNECTED
            ]),
            "total_messages": self._total_messages,
            "peak_concurrent": self._peak_concurrent,
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

ws_manager = ConnectionManager()
