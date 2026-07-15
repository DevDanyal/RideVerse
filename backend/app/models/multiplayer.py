from __future__ import annotations

import uuid
from datetime import datetime
from enum import IntEnum, StrEnum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# ── Enums ──────────────────────────────────────────────────────────────────────

class RoomType(StrEnum):
    QUICK_PLAY = "quick_play"
    PRIVATE = "private"
    TOURNAMENT = "tournament"
    EVENT = "event"
    RACE = "race"
    TRAINING = "training"


class RoomStatus(StrEnum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class ConnectionStatus(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    TIMED_OUT = "timed_out"


class PresenceStatus(StrEnum):
    ONLINE = "online"
    IN_GAME = "in_game"
    IN_MENU = "in_menu"
    AWAY = "away"
    OFFLINE = "offline"


class WSEventType(StrEnum):
    # Connection
    AUTH = "auth"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    # Heartbeat
    PING = "ping"
    PONG = "pong"
    # Room
    ROOM_CREATE = "room_create"
    ROOM_JOIN = "room_join"
    ROOM_LEAVE = "room_leave"
    ROOM_LIST = "room_list"
    ROOM_INFO = "room_info"
    ROOM_UPDATE = "room_update"
    ROOM_DESTROY = "room_destroy"
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    # Position Sync
    POSITION_UPDATE = "position_update"
    POSITION_BROADCAST = "position_broadcast"
    # Vehicle Sync
    VEHICLE_UPDATE = "vehicle_update"
    VEHICLE_BROADCAST = "vehicle_broadcast"
    # Chat
    CHAT_SEND = "chat_send"
    CHAT_MESSAGE = "chat_message"
    CHAT_HISTORY = "chat_history"
    # Presence
    PRESENCE_UPDATE = "presence_update"
    FRIENDS_ONLINE = "friends_online"
    # Notifications
    NOTIFICATION = "notification"
    NOTIFICATION_ACK = "notification_ack"
    # Errors
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class WSMessagePriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# ── Models ─────────────────────────────────────────────────────────────────────

class MultiplayerRoom(Base):
    __tablename__ = "multiplayer_rooms"

    room_name: Mapped[str] = mapped_column(String(100), nullable=False)
    room_type: Mapped[RoomType] = mapped_column(
        SAEnum(RoomType, native_enum=False), nullable=False, index=True
    )
    room_status: Mapped[RoomStatus] = mapped_column(
        SAEnum(RoomStatus, native_enum=False), default=RoomStatus.WAITING, nullable=False
    )
    max_players: Mapped[int] = mapped_column(Integer, default=16, nullable=False)
    current_player_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    region: Mapped[str] = mapped_column(String(50), default="global", nullable=False)
    host_player_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="SET NULL"), nullable=True
    )
    password_hash: Mapped[str | None] = mapped_column(String(256), nullable=True)
    map_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    members: Mapped[list[RoomMember]] = relationship(
        "RoomMember", back_populates="room", cascade="all, delete-orphan"
    )
    messages: Mapped[list[MultiplayerChatMessage]] = relationship(
        "MultiplayerChatMessage", back_populates="room", cascade="all, delete-orphan"
    )

    __table_args__ = (
        {"comment": "Multiplayer rooms and lobbies"},
    )


class RoomMember(Base):
    __tablename__ = "room_members"

    room_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("multiplayer_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_host: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    room: Mapped[MultiplayerRoom] = relationship("MultiplayerRoom", back_populates="members")

    __table_args__ = (
        {"comment": "Room membership tracking"},
    )


class WebSocketSession(Base):
    __tablename__ = "websocket_sessions"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    connection_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("multiplayer_rooms.id", ondelete="SET NULL"),
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    connection_status: Mapped[ConnectionStatus] = mapped_column(
        SAEnum(ConnectionStatus, native_enum=False),
        default=ConnectionStatus.CONNECTED,
        nullable=False,
    )
    messages_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        {"comment": "Active WebSocket connection sessions"},
    )


class PlayerPosition(Base):
    __tablename__ = "player_positions"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("multiplayer_rooms.id", ondelete="SET NULL"),
        nullable=True,
    )
    position_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    position_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    position_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    velocity_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    velocity_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    velocity_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    speed: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_in_vehicle: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        {"comment": "Real-time player position data for sync"},
    )


class VehicleSync(Base):
    __tablename__ = "vehicle_sync"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("multiplayer_rooms.id", ondelete="SET NULL"),
        nullable=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    position_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    position_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    position_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    velocity_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    velocity_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    velocity_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    speed: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    health: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    fuel: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    current_gear: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rpm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        {"comment": "Real-time vehicle state sync data"},
    )


class PlayerPresence(Base):
    __tablename__ = "player_presence"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    status: Mapped[PresenceStatus] = mapped_column(
        SAEnum(PresenceStatus, native_enum=False),
        default=PresenceStatus.OFFLINE,
        nullable=False,
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    current_room_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    status_message: Mapped[str | None] = mapped_column(String(200), nullable=True)

    __table_args__ = (
        {"comment": "Player online presence tracking"},
    )


class MultiplayerChatMessage(Base):
    __tablename__ = "multiplayer_chat_messages"

    room_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("multiplayer_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(30), default="chat", nullable=False)

    room: Mapped[MultiplayerRoom] = relationship("MultiplayerRoom", back_populates="messages")

    __table_args__ = (
        {"comment": "In-game multiplayer chat messages"},
    )


class FriendPresence(Base):
    __tablename__ = "friend_presences"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    friend_player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[PresenceStatus] = mapped_column(
        SAEnum(PresenceStatus, native_enum=False),
        default=PresenceStatus.OFFLINE,
        nullable=False,
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        {"comment": "Friend presence status cache"},
    )


class RateLimitRecord(Base):
    __tablename__ = "rate_limit_records"

    player_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        {"comment": "WebSocket rate limiting tracking"},
    )
