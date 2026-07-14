"""WebSocket connection manager."""

from fastapi import WebSocket
import logging

logger = logging.getLogger("rideverse.websocket")


class ConnectionManager:
    """Manages WebSocket connections, channels, and message broadcasting."""

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._channels: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, player_id: str) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self._connections[player_id] = websocket
        logger.info("websocket connected player_id=%s", player_id)

    async def disconnect(self, player_id: str) -> None:
        """Remove a WebSocket connection."""
        self._connections.pop(player_id, None)
        for channel_members in self._channels.values():
            channel_members.discard(player_id)
        logger.info("websocket disconnected player_id=%s", player_id)

    async def send_personal_message(self, message: str, player_id: str) -> None:
        """Send a message to a specific player."""
        websocket = self._connections.get(player_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str) -> None:
        """Broadcast a message to all connected players."""
        disconnected = []
        for player_id, websocket in self._connections.items():
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(player_id)
        for player_id in disconnected:
            await self.disconnect(player_id)

    async def broadcast_to_channel(self, channel: str, message: str) -> None:
        """Broadcast a message to all members of a channel."""
        members = self._channels.get(channel, set())
        disconnected = []
        for player_id in members:
            websocket = self._connections.get(player_id)
            if websocket:
                try:
                    await websocket.send_text(message)
                except Exception:
                    disconnected.append(player_id)
        for player_id in disconnected:
            await self.disconnect(player_id)

    def subscribe(self, player_id: str, channel: str) -> None:
        """Subscribe a player to a channel."""
        if channel not in self._channels:
            self._channels[channel] = set()
        self._channels[channel].add(player_id)

    def unsubscribe(self, player_id: str, channel: str) -> None:
        """Unsubscribe a player from a channel."""
        if channel in self._channels:
            self._channels[channel].discard(player_id)

    @property
    def active_connections(self) -> int:
        """Return the number of active connections."""
        return len(self._connections)


manager = ConnectionManager()
