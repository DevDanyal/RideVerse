from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.multiplayer import (
    ConnectionStatus,
    PresenceStatus,
    RoomStatus,
    RoomType,
    WSEventType,
    WSMessagePriority,
)


# ── WebSocket Event Envelope ──────────────────────────────────────────────────

class WSEvent(BaseModel):
    """Generic WebSocket event envelope for all WS messages."""

    event: WSEventType
    data: dict[str, Any] = Field(default_factory=dict)
    seq: int | None = None
    timestamp: datetime | None = None


class WSErrorEvent(BaseModel):
    """Error event sent to client."""

    event: WSEventType = WSEventType.ERROR
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: str = "UNKNOWN"
    message: str = "An error occurred"


class WSRateLimitedEvent(BaseModel):
    """Rate limit exceeded event."""

    event: WSEventType = WSEventType.RATE_LIMITED
    retry_after_ms: int = 1000


# ── Auth Events ────────────────────────────────────────────────────────────────

class WSAuthRequest(BaseModel):
    """Client sends JWT token to authenticate."""

    token: str


class WSAuthSuccess(BaseModel):
    """Server confirms successful authentication."""

    player_id: uuid.UUID
    display_name: str
    connection_id: str


class WSAuthFailure(BaseModel):
    """Server rejects authentication."""

    reason: str


# ── Heartbeat Events ──────────────────────────────────────────────────────────

class WSPing(BaseModel):
    """Server or client sends ping."""

    ts: float = Field(description="Timestamp in ms")


class WSPong(BaseModel):
    """Server or client sends pong."""

    ts: float
    rtt_ms: float | None = None


# ── Room Events ────────────────────────────────────────────────────────────────

class RoomCreateRequest(BaseModel):
    """Request to create a new room."""

    room_name: str = Field(min_length=1, max_length=100)
    room_type: RoomType = RoomType.QUICK_PLAY
    max_players: int = Field(default=16, ge=2, le=100)
    region: str = Field(default="global", max_length=50)
    password: str | None = Field(default=None, max_length=100)
    map_name: str | None = Field(default=None, max_length=100)


class RoomJoinRequest(BaseModel):
    """Request to join an existing room."""

    room_id: uuid.UUID
    password: str | None = None


class RoomLeaveRequest(BaseModel):
    """Request to leave the current room."""

    room_id: uuid.UUID | None = None


class RoomListRequest(BaseModel):
    """Request to list available rooms."""

    room_type: RoomType | None = None
    region: str | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class RoomInfo(BaseModel):
    """Room information sent to clients."""

    id: uuid.UUID
    room_name: str
    room_type: RoomType
    room_status: RoomStatus
    max_players: int
    current_player_count: int
    region: str
    host_player_id: uuid.UUID | None = None
    map_name: str | None = None
    has_password: bool = False
    created_at: datetime | None = None


class RoomMemberInfo(BaseModel):
    """Member information within a room."""

    player_id: uuid.UUID
    display_name: str
    is_host: bool
    is_ready: bool
    level: int | None = None


class RoomUpdateEvent(BaseModel):
    """Broadcast when room state changes."""

    room_id: uuid.UUID
    room_status: RoomStatus
    current_player_count: int
    members: list[RoomMemberInfo] = Field(default_factory=list)


# ── Position Sync Events ──────────────────────────────────────────────────────

class PositionUpdate(BaseModel):
    """Client sends position update."""

    position_x: float
    position_y: float
    position_z: float
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    velocity_z: float = 0.0
    speed: float = 0.0
    is_in_vehicle: bool = False
    vehicle_id: uuid.UUID | None = None


class PositionBroadcast(BaseModel):
    """Server broadcasts position to other players."""

    player_id: uuid.UUID
    display_name: str | None = None
    position_x: float
    position_y: float
    position_z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float
    speed: float
    is_in_vehicle: bool
    vehicle_id: uuid.UUID | None = None
    seq: int | None = None


# ── Vehicle Sync Events ───────────────────────────────────────────────────────

class VehicleUpdate(BaseModel):
    """Client sends vehicle state update."""

    vehicle_id: uuid.UUID
    position_x: float
    position_y: float
    position_z: float
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    velocity_z: float = 0.0
    speed: float = 0.0
    health: float = 100.0
    fuel: float = 100.0
    current_gear: int = 0
    rpm: float = 0.0


class VehicleBroadcast(BaseModel):
    """Server broadcasts vehicle state to other players."""

    player_id: uuid.UUID
    vehicle_id: uuid.UUID
    position_x: float
    position_y: float
    position_z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float
    speed: float
    health: float
    fuel: float
    current_gear: int
    rpm: float
    seq: int | None = None


# ── Chat Events ────────────────────────────────────────────────────────────────

class ChatSendRequest(BaseModel):
    """Client sends a chat message."""

    message: str = Field(min_length=1, max_length=500)
    message_type: str = "chat"


class ChatMessageEvent(BaseModel):
    """Server broadcasts a chat message."""

    message_id: uuid.UUID
    player_id: uuid.UUID
    display_name: str
    message: str
    message_type: str
    room_id: uuid.UUID
    timestamp: datetime


# ── Presence Events ────────────────────────────────────────────────────────────

class PresenceUpdate(BaseModel):
    """Client updates their presence status."""

    status: PresenceStatus
    status_message: str | None = Field(default=None, max_length=200)


class FriendPresenceEvent(BaseModel):
    """Server notifies client about friend presence changes."""

    friend_player_id: uuid.UUID
    display_name: str
    status: PresenceStatus
    current_room_id: uuid.UUID | None = None


class FriendsOnlineEvent(BaseModel):
    """Server sends list of online friends on connect."""

    friends: list[FriendPresenceEvent] = Field(default_factory=list)


# ── Notification Events ───────────────────────────────────────────────────────

class NotificationEvent(BaseModel):
    """Server pushes a notification to the client."""

    notification_id: uuid.UUID
    title: str
    message: str
    notification_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime


class NotificationAckRequest(BaseModel):
    """Client acknowledges a notification."""

    notification_id: uuid.UUID


# ── REST API Schemas ──────────────────────────────────────────────────────────

class MultiplayerRoomCreateRequest(BaseModel):
    """REST: Create a room."""

    room_name: str = Field(min_length=1, max_length=100)
    room_type: RoomType = RoomType.QUICK_PLAY
    max_players: int = Field(default=16, ge=2, le=100)
    region: str = Field(default="global", max_length=50)
    password: str | None = Field(default=None, max_length=100)
    map_name: str | None = Field(default=None, max_length=100)


class MultiplayerRoomUpdateRequest(BaseModel):
    """REST: Update room settings."""

    room_name: str | None = Field(default=None, min_length=1, max_length=100)
    max_players: int | None = Field(default=None, ge=2, le=100)
    room_status: RoomStatus | None = None
    map_name: str | None = None


class MultiplayerRoomResponse(BaseModel):
    """REST: Room response."""

    id: uuid.UUID
    room_name: str
    room_type: RoomType
    room_status: RoomStatus
    max_players: int
    current_player_count: int
    region: str
    host_player_id: uuid.UUID | None = None
    map_name: str | None = None
    has_password: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MultiplayerRoomListResponse(BaseModel):
    """REST: Paginated room list."""

    rooms: list[MultiplayerRoomResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    total_pages: int = 0


class WebSocketSessionResponse(BaseModel):
    """REST: WebSocket session info."""

    id: uuid.UUID
    player_id: uuid.UUID
    connection_id: str
    room_id: uuid.UUID | None = None
    connection_status: ConnectionStatus
    connected_at: datetime
    last_heartbeat: datetime
    messages_sent: int = 0
    messages_received: int = 0


class PlayerPresenceResponse(BaseModel):
    """REST: Player presence info."""

    player_id: uuid.UUID
    status: PresenceStatus
    last_seen: datetime
    current_room_id: uuid.UUID | None = None
    status_message: str | None = None


class MultiplayerStatsResponse(BaseModel):
    """REST: Multiplayer statistics."""

    total_rooms: int = 0
    active_rooms: int = 0
    total_connections: int = 0
    active_connections: int = 0
    total_messages: int = 0
    peak_concurrent: int = 0
