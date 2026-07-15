"""Unit tests for the Multiplayer & WebSocket System (TASK 15).

Covers: Connection Manager (connect/disconnect, rooms, heartbeat, rate limiting,
reconnection, messaging, presence), Dispatcher (ping, position, vehicle, chat,
room create/join/leave/list, presence), Repository (room CRUD, member, session,
position, vehicle sync, presence, chat, rate limit), Service (room management,
session, position, vehicle sync, presence, chat, stats), Schemas (validation),
REST API (rooms, sessions, stats).
"""
from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import create_access_token, get_password_hash
from app.database.base import Base
from app.dependencies import get_current_active_user, get_db_session
from app.main import app
from app.models.auth import AccountRole, AccountStatus, PlayerAccount
from app.models.economy import Wallet
from app.models.inventory import Inventory
from app.models.multiplayer import (
    ConnectionStatus,
    MultiplayerRoom,
    PlayerPosition,
    PlayerPresence,
    PresenceStatus,
    RoomMember,
    RoomStatus,
    RoomType,
    VehicleSync,
    WebSocketSession,
    WSEventType,
)
from app.models.player import Player, PlayerSettings, PlayerStatistics
from app.repositories.auth import AuthRepository
from app.repositories.multiplayer import MultiplayerRepository
from app.schemas.multiplayer import (
    RoomCreateRequest,
    RoomJoinRequest,
    RoomListRequest,
    WSEvent,
    WSErrorEvent,
    WSAuthRequest,
    WSRateLimitedEvent,
    PositionUpdate,
    VehicleUpdate,
    ChatSendRequest,
    PresenceUpdate,
    MultiplayerRoomCreateRequest,
    MultiplayerRoomResponse,
    MultiplayerRoomUpdateRequest,
    MultiplayerStatsResponse,
    WebSocketSessionResponse,
)
from app.services.multiplayer import MultiplayerService
from app.services.websocket_dispatcher import WebSocketDispatcher
from app.services.websocket_manager import (
    ConnectionInfo,
    ConnectionManager,
    RoomInfo,
    ws_manager,
)

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_MP_TABLES = [
    Base.metadata.tables[name]
    for name in (
        "player_accounts",
        "player_sessions",
        "refresh_tokens",
        "players",
        "player_statistics",
        "player_settings",
        "inventories",
        "wallets",
        "multiplayer_rooms",
        "room_members",
        "websocket_sessions",
        "player_positions",
        "vehicle_sync",
        "player_presence",
        "friend_presences",
        "multiplayer_chat_messages",
        "rate_limit_records",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_MP_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_MP_TABLES)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        yield session
        if session.is_active:
            await session.rollback()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _override():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(db: AsyncSession) -> dict:
    email = f"mp_test_{uuid.uuid4().hex[:8]}@test.com"
    username = f"mp_tester_{uuid.uuid4().hex[:8]}"
    repo = AuthRepository(db)
    account = await repo.create_account(email, username, get_password_hash("StrongPass1!"))
    await db.flush()

    player = Player(
        account_id=account.id,
        display_name=f"Player_{username}",
        level=1,
    )
    db.add(player)
    await db.flush()

    token = create_access_token({"sub": str(account.id), "type": "access"})
    return {"Authorization": f"Bearer {token}"}


async def _create_player_with_account(db: AsyncSession) -> tuple[PlayerAccount, Player]:
    email = f"mp_player_{uuid.uuid4().hex[:8]}@test.com"
    username = f"mp_player_{uuid.uuid4().hex[:8]}"
    repo = AuthRepository(db)
    account = await repo.create_account(email, username, get_password_hash("StrongPass1!"))
    await db.flush()

    player = Player(
        account_id=account.id,
        display_name=f"Player_{username}",
        level=1,
    )
    db.add(player)
    await db.flush()
    return account, player


# ── Schema Tests ───────────────────────────────────────────────────────────────


class TestMultiplayerSchemas:
    def test_ws_event_valid(self):
        event = WSEvent(event=WSEventType.PING, data={"ts": 1.0})
        assert event.event == WSEventType.PING
        assert event.data["ts"] == 1.0

    def test_ws_event_with_seq(self):
        event = WSEvent(event=WSEventType.POSITION_UPDATE, data={}, seq=42)
        assert event.seq == 42

    def test_ws_error_event(self):
        event = WSErrorEvent(error_code="TEST_ERR", message="Test error")
        assert event.event == WSEventType.ERROR
        assert event.error_code == "TEST_ERR"

    def test_ws_rate_limited(self):
        event = WSRateLimitedEvent(retry_after_ms=5000)
        assert event.retry_after_ms == 5000

    def test_ws_auth_request(self):
        req = WSAuthRequest(token="abc123")
        assert req.token == "abc123"

    def test_room_create_request_defaults(self):
        req = RoomCreateRequest(room_name="Test Room")
        assert req.room_name == "Test Room"
        assert req.room_type == RoomType.QUICK_PLAY
        assert req.max_players == 16

    def test_room_create_request_validation(self):
        with pytest.raises(Exception):
            RoomCreateRequest(room_name="")

    def test_room_join_request(self):
        room_id = uuid.uuid4()
        req = RoomJoinRequest(room_id=room_id, password="secret")
        assert req.room_id == room_id
        assert req.password == "secret"

    def test_room_list_request_defaults(self):
        req = RoomListRequest()
        assert req.page == 1
        assert req.per_page == 20

    def test_position_update(self):
        pos = PositionUpdate(
            position_x=10.0, position_y=20.0, position_z=30.0
        )
        assert pos.position_x == 10.0
        assert pos.is_in_vehicle is False

    def test_vehicle_update(self):
        vid = uuid.uuid4()
        v = VehicleUpdate(
            vehicle_id=vid,
            position_x=1.0, position_y=2.0, position_z=3.0,
            speed=100.0, health=80.0, fuel=50.0,
        )
        assert v.vehicle_id == vid
        assert v.speed == 100.0

    def test_chat_send_request(self):
        req = ChatSendRequest(message="Hello!")
        assert req.message == "Hello!"
        assert req.message_type == "chat"

    def test_chat_send_request_empty_fails(self):
        with pytest.raises(Exception):
            ChatSendRequest(message="")

    def test_chat_send_request_too_long(self):
        with pytest.raises(Exception):
            ChatSendRequest(message="x" * 501)

    def test_presence_update(self):
        p = PresenceUpdate(status=PresenceStatus.IN_GAME)
        assert p.status == PresenceStatus.IN_GAME

    def test_multiplayer_room_create_request(self):
        req = MultiplayerRoomCreateRequest(room_name="Race Room")
        assert req.room_type == RoomType.QUICK_PLAY

    def test_multiplayer_room_update_request_partial(self):
        req = MultiplayerRoomUpdateRequest(room_name="Updated")
        assert req.room_name == "Updated"
        assert req.max_players is None

    def test_multiplayer_stats_response(self):
        s = MultiplayerStatsResponse(total_rooms=5, active_connections=10)
        assert s.total_rooms == 5
        assert s.active_connections == 10


# ── Connection Manager Tests ───────────────────────────────────────────────────


class TestConnectionManager:
    def setup_method(self):
        self.mgr = ConnectionManager(
            heartbeat_interval_s=1.0,
            heartbeat_timeout_s=5.0,
            rate_limit_window_s=60.0,
            rate_limit_max=10,
        )

    def test_initial_state(self):
        assert self.mgr.active_connection_count == 0
        assert self.mgr.active_room_count == 0
        assert self.mgr.total_messages == 0

    def test_get_connection_none(self):
        assert self.mgr.get_connection(uuid.uuid4()) is None

    def test_get_connection_by_id_none(self):
        assert self.mgr.get_connection_by_id("nonexistent") is None

    def test_get_room_none(self):
        assert self.mgr.get_room(uuid.uuid4()) is None

    def test_get_player_room_none(self):
        assert self.mgr.get_player_room(uuid.uuid4()) is None

    def test_list_rooms_empty(self):
        assert self.mgr.list_rooms() == []

    def test_list_rooms_by_type(self):
        assert self.mgr.list_rooms(room_type=RoomType.RACE) == []

    def test_list_rooms_by_region(self):
        assert self.mgr.list_rooms(region="eu") == []

    def test_get_presence_offline(self):
        pid = uuid.uuid4()
        assert self.mgr.get_presence(pid) == PresenceStatus.OFFLINE

    def test_check_rate_limit_no_connection(self):
        assert self.mgr.check_rate_limit(uuid.uuid4()) is False

    def test_get_rate_limit_remaining_no_connection(self):
        assert self.mgr.get_rate_limit_remaining(uuid.uuid4()) == 0

    def test_get_stats(self):
        stats = self.mgr.get_stats()
        assert stats["total_rooms"] == 0
        assert stats["total_connections"] == 0
        assert stats["total_messages"] == 0

    def test_generate_and_validate_reconnect_token(self):
        pid = uuid.uuid4()
        token = self.mgr.generate_reconnect_token(pid)
        assert token
        assert self.mgr.validate_reconnect_token(pid, token) is True

    def test_reconnect_token_wrong_token(self):
        pid = uuid.uuid4()
        token = self.mgr.generate_reconnect_token(pid)
        assert self.mgr.validate_reconnect_token(pid, "wrong") is False

    def test_reconnect_token_already_used(self):
        pid = uuid.uuid4()
        token = self.mgr.generate_reconnect_token(pid)
        assert self.mgr.validate_reconnect_token(pid, token) is True
        assert self.mgr.validate_reconnect_token(pid, token) is False

    def test_queue_and_flush_pending_messages(self):
        pid = uuid.uuid4()
        self.mgr.queue_message(pid, {"event": "test", "data": {}})
        assert len(self.mgr._pending_messages[pid]) == 1
        count = asyncio.get_event_loop().run_until_complete(
            self.mgr.flush_pending_messages(pid)
        )
        assert count == 0  # no connection to send to

    def test_queue_pending_messages_limit(self):
        pid = uuid.uuid4()
        for _ in range(120):
            self.mgr.queue_message(pid, {"event": "test", "data": {}})
        assert len(self.mgr._pending_messages[pid]) == 100


# ── Room Info Tests ────────────────────────────────────────────────────────────


class TestRoomInfo:
    def test_create_room_info(self):
        rid = uuid.uuid4()
        host = uuid.uuid4()
        room = RoomInfo(
            room_id=rid,
            room_name="Test Room",
            room_type=RoomType.QUICK_PLAY,
            max_players=8,
            region="us-east",
            host_player_id=host,
        )
        assert room.id == rid
        assert room.room_name == "Test Room"
        assert room.room_type == RoomType.QUICK_PLAY
        assert room.max_players == 8
        assert room.region == "us-east"
        assert room.host_player_id == host
        assert room.room_status == RoomStatus.WAITING
        assert len(room.members) == 0
        assert room.password_hash is None
        assert room.map_name is None

    def test_room_members_add(self):
        room = RoomInfo(
            room_id=uuid.uuid4(),
            room_name="R",
            room_type=RoomType.PRIVATE,
        )
        pid = uuid.uuid4()
        room.members.add(pid)
        assert pid in room.members
        assert len(room.members) == 1

    def test_room_members_set_operations(self):
        room = RoomInfo(
            room_id=uuid.uuid4(),
            room_name="R",
            room_type=RoomType.RACE,
        )
        p1, p2 = uuid.uuid4(), uuid.uuid4()
        room.members.add(p1)
        room.members.add(p2)
        assert len(room.members) == 2
        room.members.discard(p1)
        assert len(room.members) == 1


# ── Connection Info Tests ──────────────────────────────────────────────────────


class TestConnectionInfo:
    def test_create_connection_info(self):
        ws = MagicMock()
        ws.client_state.name = "CONNECTED"
        pid = uuid.uuid4()
        info = ConnectionInfo(
            player_id=pid,
            display_name="TestPlayer",
            connection_id="conn-123",
            websocket=ws,
        )
        assert info.player_id == pid
        assert info.display_name == "TestPlayer"
        assert info.connection_id == "conn-123"
        assert info.room_id is None
        assert info.messages_sent == 0
        assert info.messages_received == 0
        assert info.seq == 0
        assert info.status == ConnectionStatus.CONNECTED

    def test_connection_info_default_values(self):
        ws = MagicMock()
        info = ConnectionInfo(
            player_id=uuid.uuid4(),
            display_name="P",
            connection_id="c",
            websocket=ws,
        )
        assert info.rate_limit_count == 0
        assert isinstance(info.connected_at, datetime)
        assert isinstance(info.last_heartbeat, datetime)


# ── Repository Tests ───────────────────────────────────────────────────────────


class TestMultiplayerRepository:
    async def test_create_and_get_room(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        room = await repo.create_room({
            "room_name": "Test Room",
            "room_type": "quick_play",
            "max_players": 8,
            "region": "us-east",
            "current_player_count": 0,
        })
        await db.flush()
        assert room.room_name == "Test Room"
        assert room.room_type == RoomType.QUICK_PLAY

        fetched = await repo.get_room_by_id(room.id)
        assert fetched is not None
        assert fetched.room_name == "Test Room"

    async def test_get_room_not_found(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        assert await repo.get_room_by_id(uuid.uuid4()) is None

    async def test_list_rooms(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        await repo.create_room({
            "room_name": "Room A",
            "room_type": "quick_play",
            "max_players": 8,
            "region": "us-east",
            "current_player_count": 0,
        })
        await repo.create_room({
            "room_name": "Room B",
            "room_type": "race",
            "max_players": 4,
            "region": "eu-west",
            "current_player_count": 0,
        })
        await db.flush()

        all_rooms = await repo.list_rooms()
        assert len(all_rooms) >= 2

        filtered = await repo.list_rooms(room_type="race")
        assert all(r.room_type == RoomType.RACE for r in filtered)

    async def test_count_rooms(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        await repo.create_room({
            "room_name": "C1",
            "room_type": "quick_play",
            "max_players": 8,
            "region": "us-east",
            "current_player_count": 0,
        })
        await db.flush()
        count = await repo.count_rooms()
        assert count >= 1

    async def test_update_room(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        room = await repo.create_room({
            "room_name": "Update Me",
            "room_type": "quick_play",
            "max_players": 8,
            "region": "us-east",
            "current_player_count": 0,
        })
        await db.flush()

        updated = await repo.update_room(room.id, room_name="Updated Room")
        assert updated is not None
        assert updated.room_name == "Updated Room"

    async def test_delete_room(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        room = await repo.create_room({
            "room_name": "Delete Me",
            "room_type": "quick_play",
            "max_players": 8,
            "region": "us-east",
            "current_player_count": 0,
        })
        await db.flush()

        result = await repo.delete_room(room.id)
        assert result is True
        assert await repo.get_room_by_id(room.id) is None

    async def test_add_and_get_room_members(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        room = await repo.create_room({
            "room_name": "Members Room",
            "room_type": "quick_play",
            "max_players": 8,
            "region": "us-east",
            "current_player_count": 0,
        })
        await db.flush()

        pid1, pid2 = uuid.uuid4(), uuid.uuid4()
        await repo.add_room_member(room.id, pid1, is_host=True)
        await repo.add_room_member(room.id, pid2, is_host=False)
        await db.flush()

        members = await repo.get_room_members(room.id)
        assert len(members) == 2

    async def test_remove_room_member(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        room = await repo.create_room({
            "room_name": "Remove Member",
            "room_type": "quick_play",
            "max_players": 8,
            "region": "us-east",
            "current_player_count": 0,
        })
        await db.flush()

        pid = uuid.uuid4()
        await repo.add_room_member(room.id, pid)
        await db.flush()

        result = await repo.remove_room_member(room.id, pid)
        assert result is True

    async def test_get_player_room_membership_none(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        assert await repo.get_player_room_membership(uuid.uuid4()) is None

    async def test_update_room_member(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        room = await repo.create_room({
            "room_name": "Update Member",
            "room_type": "quick_play",
            "max_players": 8,
            "region": "us-east",
            "current_player_count": 0,
        })
        await db.flush()

        pid = uuid.uuid4()
        await repo.add_room_member(room.id, pid)
        await db.flush()

        updated = await repo.update_room_member(room.id, pid, is_ready=True)
        assert updated is not None
        assert updated.is_ready is True

    async def test_create_and_get_ws_session(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        session = await repo.create_ws_session({
            "player_id": uuid.uuid4(),
            "connection_id": "conn-001",
            "connected_at": datetime.now(timezone.utc),
            "last_heartbeat": datetime.now(timezone.utc),
            "connection_status": ConnectionStatus.CONNECTED,
        })
        await db.flush()

        fetched = await repo.get_ws_session_by_connection_id("conn-001")
        assert fetched is not None
        assert fetched.connection_id == "conn-001"

    async def test_get_ws_sessions_by_player(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        pid = uuid.uuid4()
        await repo.create_ws_session({
            "player_id": pid,
            "connection_id": "conn-a",
            "connected_at": datetime.now(timezone.utc),
            "last_heartbeat": datetime.now(timezone.utc),
            "connection_status": ConnectionStatus.CONNECTED,
        })
        await db.flush()

        sessions = await repo.get_ws_sessions_by_player(pid)
        assert len(sessions) >= 1

    async def test_update_ws_session(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        await repo.create_ws_session({
            "player_id": uuid.uuid4(),
            "connection_id": "conn-update",
            "connected_at": datetime.now(timezone.utc),
            "last_heartbeat": datetime.now(timezone.utc),
            "connection_status": ConnectionStatus.CONNECTED,
        })
        await db.flush()

        updated = await repo.update_ws_session("conn-update", messages_sent=5)
        assert updated is not None
        assert updated.messages_sent == 5

    async def test_close_ws_session(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        await repo.create_ws_session({
            "player_id": uuid.uuid4(),
            "connection_id": "conn-close",
            "connected_at": datetime.now(timezone.utc),
            "last_heartbeat": datetime.now(timezone.utc),
            "connection_status": ConnectionStatus.CONNECTED,
        })
        await db.flush()

        result = await repo.close_ws_session("conn-close")
        assert result is True

    async def test_upsert_player_position_create(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        pid = uuid.uuid4()
        pos = await repo.upsert_player_position(pid, {
            "position_x": 10.0,
            "position_y": 20.0,
            "position_z": 30.0,
            "speed": 50.0,
            "last_updated": datetime.now(timezone.utc),
        })
        await db.flush()
        assert pos.position_x == 10.0
        assert pos.player_id == pid

    async def test_upsert_player_position_update(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        pid = uuid.uuid4()
        await repo.upsert_player_position(pid, {
            "position_x": 0.0,
            "position_y": 0.0,
            "position_z": 0.0,
            "speed": 0.0,
            "last_updated": datetime.now(timezone.utc),
        })
        await db.flush()

        updated = await repo.upsert_player_position(pid, {
            "position_x": 100.0,
            "position_y": 200.0,
            "position_z": 300.0,
            "speed": 120.0,
            "last_updated": datetime.now(timezone.utc),
        })
        assert updated.position_x == 100.0

    async def test_get_player_position_none(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        assert await repo.get_player_position(uuid.uuid4()) is None

    async def test_get_room_positions(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        rid = uuid.uuid4()
        pid = uuid.uuid4()
        await repo.upsert_player_position(pid, {
            "position_x": 1.0,
            "position_y": 2.0,
            "position_z": 3.0,
            "speed": 10.0,
            "room_id": rid,
            "last_updated": datetime.now(timezone.utc),
        })
        await db.flush()

        positions = await repo.get_room_positions(rid)
        assert len(positions) >= 1

    async def test_upsert_vehicle_sync(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        pid, vid = uuid.uuid4(), uuid.uuid4()
        sync = await repo.upsert_vehicle_sync(pid, vid, {
            "speed": 100.0,
            "health": 80.0,
            "fuel": 50.0,
            "current_gear": 3,
            "rpm": 4500.0,
            "last_updated": datetime.now(timezone.utc),
        })
        await db.flush()
        assert sync.speed == 100.0
        assert sync.health == 80.0

    async def test_upsert_vehicle_sync_update(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        pid, vid = uuid.uuid4(), uuid.uuid4()
        await repo.upsert_vehicle_sync(pid, vid, {
            "speed": 50.0,
            "health": 100.0,
            "fuel": 100.0,
            "current_gear": 1,
            "rpm": 2000.0,
            "last_updated": datetime.now(timezone.utc),
        })
        await db.flush()

        updated = await repo.upsert_vehicle_sync(pid, vid, {
            "speed": 120.0,
            "health": 90.0,
            "fuel": 80.0,
            "current_gear": 4,
            "rpm": 5500.0,
            "last_updated": datetime.now(timezone.utc),
        })
        assert updated.speed == 120.0
        assert updated.current_gear == 4

    async def test_upsert_presence(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        pid = uuid.uuid4()
        presence = await repo.upsert_presence(pid, {
            "status": PresenceStatus.ONLINE,
            "last_seen": datetime.now(timezone.utc),
        })
        await db.flush()
        assert presence.status == PresenceStatus.ONLINE

    async def test_get_presence_none(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        assert await repo.get_presence(uuid.uuid4()) is None

    async def test_create_chat_message(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        msg = await repo.create_chat_message({
            "room_id": uuid.uuid4(),
            "player_id": uuid.uuid4(),
            "message": "Hello world!",
            "message_type": "chat",
        })
        await db.flush()
        assert msg.message == "Hello world!"

    async def test_get_room_messages(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        rid = uuid.uuid4()
        for i in range(3):
            await repo.create_chat_message({
                "room_id": rid,
                "player_id": uuid.uuid4(),
                "message": f"msg {i}",
                "message_type": "chat",
            })
        await db.flush()

        messages = await repo.get_room_messages(rid)
        assert len(messages) >= 3

    async def test_get_or_create_rate_limit(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        now = datetime.now(timezone.utc)
        record = await repo.get_or_create_rate_limit(uuid.uuid4(), "chat", now)
        await db.flush()
        assert record.message_count == 1

        updated = await repo.get_or_create_rate_limit(uuid.uuid4(), "chat", now)
        assert updated.message_count == 1  # different player

    async def test_get_total_rooms(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        count = await repo.get_total_rooms()
        assert count >= 0

    async def test_get_active_connections(self, db: AsyncSession):
        repo = MultiplayerRepository(db)
        count = await repo.get_active_connections()
        assert count >= 0


# ── Service Tests ──────────────────────────────────────────────────────────────


class TestMultiplayerService:
    async def test_create_room(self, db: AsyncSession):
        service = MultiplayerService(db)
        account, player = await _create_player_with_account(db)
        await db.flush()

        result = await service.create_room(
            player_id=player.id,
            room_name="Service Room",
            room_type="quick_play",
            max_players=8,
            region="us-east",
        )
        assert result["room_name"] == "Service Room"
        assert result["room_type"] == "quick_play"
        assert result["max_players"] == 8

    async def test_create_room_invalid_name(self, db: AsyncSession):
        service = MultiplayerService(db)
        account, player = await _create_player_with_account(db)
        await db.flush()

        with pytest.raises(ValidationError):
            await service.create_room(
                player_id=player.id,
                room_name="",
            )

    async def test_create_room_invalid_max_players(self, db: AsyncSession):
        service = MultiplayerService(db)
        account, player = await _create_player_with_account(db)
        await db.flush()

        with pytest.raises(ValidationError):
            await service.create_room(
                player_id=player.id,
                room_name="Room",
                max_players=1,
            )

    async def test_create_room_already_in_room(self, db: AsyncSession):
        service = MultiplayerService(db)
        account, player = await _create_player_with_account(db)
        await db.flush()

        await service.create_room(player_id=player.id, room_name="First Room")
        with pytest.raises(ValidationError):
            await service.create_room(player_id=player.id, room_name="Second Room")

    async def test_get_room(self, db: AsyncSession):
        service = MultiplayerService(db)
        account, player = await _create_player_with_account(db)
        await db.flush()

        created = await service.create_room(
            player_id=player.id,
            room_name="Get Room",
        )
        fetched = await service.get_room(created["id"])
        assert fetched["room_name"] == "Get Room"
        assert "members" in fetched

    async def test_get_room_not_found(self, db: AsyncSession):
        service = MultiplayerService(db)
        with pytest.raises(NotFoundError):
            await service.get_room(uuid.uuid4())

    async def test_list_rooms(self, db: AsyncSession):
        service = MultiplayerService(db)
        account, player = await _create_player_with_account(db)
        await db.flush()

        await service.create_room(player_id=player.id, room_name="List Room")
        result = await service.list_rooms()
        assert "rooms" in result
        assert result["total"] >= 1

    async def test_update_room(self, db: AsyncSession):
        service = MultiplayerService(db)
        account, player = await _create_player_with_account(db)
        await db.flush()

        created = await service.create_room(player_id=player.id, room_name="Update")
        updated = await service.update_room(
            created["id"], player.id, room_name="Updated"
        )
        assert updated["room_name"] == "Updated"

    async def test_update_room_not_host(self, db: AsyncSession):
        service = MultiplayerService(db)
        account1, player1 = await _create_player_with_account(db)
        account2, player2 = await _create_player_with_account(db)
        await db.flush()

        created = await service.create_room(player_id=player1.id, room_name="Host Room")
        with pytest.raises(ValidationError):
            await service.update_room(created["id"], player2.id, room_name="Hacked")

    async def test_delete_room(self, db: AsyncSession):
        service = MultiplayerService(db)
        account, player = await _create_player_with_account(db)
        await db.flush()

        created = await service.create_room(player_id=player.id, room_name="Delete Me")
        result = await service.delete_room(created["id"], player.id)
        assert result is True

    async def test_delete_room_not_host(self, db: AsyncSession):
        service = MultiplayerService(db)
        account1, player1 = await _create_player_with_account(db)
        account2, player2 = await _create_player_with_account(db)
        await db.flush()

        created = await service.create_room(player_id=player1.id, room_name="Host Only")
        with pytest.raises(ValidationError):
            await service.delete_room(created["id"], player2.id)

    async def test_register_and_close_session(self, db: AsyncSession):
        service = MultiplayerService(db)
        pid = uuid.uuid4()
        result = await service.register_session(pid, "conn-001", "127.0.0.1")
        assert result["connection_id"] == "conn-001"

        sessions = await service.get_player_sessions(pid)
        assert len(sessions) >= 1

        closed = await service.close_session("conn-001")
        assert closed is True

    async def test_update_player_position(self, db: AsyncSession):
        service = MultiplayerService(db)
        pid = uuid.uuid4()
        result = await service.update_player_position(
            pid, None, {
                "position_x": 10.0,
                "position_y": 20.0,
                "position_z": 30.0,
                "speed": 50.0,
            }
        )
        assert result["position_x"] == 10.0

    async def test_get_player_position(self, db: AsyncSession):
        service = MultiplayerService(db)
        pid = uuid.uuid4()
        await service.update_player_position(pid, None, {
            "position_x": 5.0,
            "position_y": 10.0,
            "position_z": 15.0,
            "speed": 25.0,
        })
        pos = await service.get_player_position(pid)
        assert pos is not None
        assert pos["position_x"] == 5.0

    async def test_get_player_position_none(self, db: AsyncSession):
        service = MultiplayerService(db)
        assert await service.get_player_position(uuid.uuid4()) is None

    async def test_update_vehicle_sync(self, db: AsyncSession):
        service = MultiplayerService(db)
        pid, vid = uuid.uuid4(), uuid.uuid4()
        result = await service.update_vehicle_sync(
            pid, None, vid, {
                "speed": 100.0,
                "health": 80.0,
                "fuel": 50.0,
                "current_gear": 3,
                "rpm": 4500.0,
            }
        )
        assert result["speed"] == 100.0

    async def test_update_presence(self, db: AsyncSession):
        service = MultiplayerService(db)
        pid = uuid.uuid4()
        result = await service.update_presence(pid, "online", "Playing!")
        assert result["status"] == "online"
        assert result["status_message"] == "Playing!"

    async def test_get_presence(self, db: AsyncSession):
        service = MultiplayerService(db)
        pid = uuid.uuid4()
        await service.update_presence(pid, "online")
        presence = await service.get_presence(pid)
        assert presence is not None
        assert presence["status"] == "online"

    async def test_get_presence_none(self, db: AsyncSession):
        service = MultiplayerService(db)
        assert await service.get_presence(uuid.uuid4()) is None

    async def test_save_and_get_chat_messages(self, db: AsyncSession):
        service = MultiplayerService(db)
        rid = uuid.uuid4()
        pid = uuid.uuid4()
        msg = await service.save_chat_message(rid, pid, "Hello!", "chat")
        assert msg["message"] == "Hello!"

        messages = await service.get_room_messages(rid)
        assert len(messages) >= 1

    async def test_get_statistics(self, db: AsyncSession):
        service = MultiplayerService(db)
        stats = await service.get_statistics()
        assert "total_rooms" in stats
        assert "active_connections" in stats


# ── Dispatcher Tests ───────────────────────────────────────────────────────────


class TestWebSocketDispatcher:
    def setup_method(self):
        self.mgr = ConnectionManager(
            heartbeat_interval_s=1.0,
            heartbeat_timeout_s=5.0,
            rate_limit_window_s=60.0,
            rate_limit_max=100,
        )
        self.dispatcher = WebSocketDispatcher(self.mgr)
        self.dispatcher.register_all()

    def test_register_handlers(self):
        assert WSEventType.PING.value in self.dispatcher._handlers
        assert WSEventType.POSITION_UPDATE.value in self.dispatcher._handlers
        assert WSEventType.VEHICLE_UPDATE.value in self.dispatcher._handlers
        assert WSEventType.CHAT_SEND.value in self.dispatcher._handlers
        assert WSEventType.ROOM_CREATE.value in self.dispatcher._handlers
        assert WSEventType.ROOM_JOIN.value in self.dispatcher._handlers
        assert WSEventType.ROOM_LEAVE.value in self.dispatcher._handlers
        assert WSEventType.ROOM_LIST.value in self.dispatcher._handlers
        assert WSEventType.PRESENCE_UPDATE.value in self.dispatcher._handlers
        assert WSEventType.NOTIFICATION_ACK.value in self.dispatcher._handlers

    def test_custom_handler_registration(self):
        async def custom_handler(conn, data, dispatcher):
            pass

        self.dispatcher.register(WSEventType.AUTH, custom_handler)
        assert "auth" in self.dispatcher._handlers

    async def test_dispatch_unknown_event(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-1", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {"event": "unknown_event", "data": {}})

    async def test_dispatch_rate_limited(self):
        self.mgr._rate_limit_max = 1
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-rl", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {"event": "ping", "data": {"ts": 1.0}})
        await self.dispatcher.dispatch(info, {"event": "ping", "data": {"ts": 2.0}})

    async def test_handle_ping(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-ping", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {"event": "ping", "data": {"ts": 123.0}})
        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["event"] == "pong"

    async def test_handle_position_update_no_room(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-pos", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "position_update",
            "data": {"position_x": 1.0, "position_y": 2.0, "position_z": 3.0},
        })

    async def test_handle_position_update_in_room(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-pos2", ws)
        self.mgr._connections[pid] = info

        room = RoomInfo(
            room_id=uuid.uuid4(),
            room_name="Pos Room",
            room_type=RoomType.QUICK_PLAY,
        )
        room.members.add(pid)
        self.mgr._rooms[room.id] = room
        info.room_id = room.id

        other_ws = AsyncMock()
        other_ws.client_state.name = "CONNECTED"
        other_ws.send_json = AsyncMock()
        other_pid = uuid.uuid4()
        other_info = ConnectionInfo(other_pid, "Other", "conn-other", other_ws)
        room.members.add(other_pid)
        self.mgr._connections[other_pid] = other_info

        await self.dispatcher.dispatch(info, {
            "event": "position_update",
            "data": {"position_x": 10.0, "position_y": 20.0, "position_z": 30.0},
        })
        other_ws.send_json.assert_called_once()

    async def test_handle_chat_send_no_room(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-chat", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "chat_send",
            "data": {"message": "Hello"},
        })
        call_args = ws.send_json.call_args[0][0]
        assert call_args["event"] == "error"

    async def test_handle_chat_send_empty_message(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-chat2", ws)
        self.mgr._connections[pid] = info

        room = RoomInfo(
            room_id=uuid.uuid4(),
            room_name="Chat Room",
            room_type=RoomType.QUICK_PLAY,
        )
        room.members.add(pid)
        self.mgr._rooms[room.id] = room
        info.room_id = room.id

        await self.dispatcher.dispatch(info, {
            "event": "chat_send",
            "data": {"message": ""},
        })
        call_args = ws.send_json.call_args[0][0]
        assert call_args["event"] == "error"

    async def test_handle_chat_send_too_long(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-chat3", ws)
        self.mgr._connections[pid] = info

        room = RoomInfo(
            room_id=uuid.uuid4(),
            room_name="Chat Room 2",
            room_type=RoomType.QUICK_PLAY,
        )
        room.members.add(pid)
        self.mgr._rooms[room.id] = room
        info.room_id = room.id

        await self.dispatcher.dispatch(info, {
            "event": "chat_send",
            "data": {"message": "x" * 501},
        })
        call_args = ws.send_json.call_args[0][0]
        assert call_args["event"] == "error"

    async def test_handle_chat_send_valid(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-chat4", ws)
        self.mgr._connections[pid] = info

        room = RoomInfo(
            room_id=uuid.uuid4(),
            room_name="Chat Room 3",
            room_type=RoomType.QUICK_PLAY,
        )
        room.members.add(pid)
        self.mgr._rooms[room.id] = room
        info.room_id = room.id

        await self.dispatcher.dispatch(info, {
            "event": "chat_send",
            "data": {"message": "Hello everyone!"},
        })
        ws.send_json.assert_called()
        call_args = ws.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "chat_message"

    async def test_handle_room_create(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-create", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "room_create",
            "data": {
                "room_name": "My Room",
                "room_type": "race",
                "max_players": 8,
                "region": "eu",
            },
        })
        ws.send_json.assert_called()
        call_args = ws.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "room_info"
        assert call_args["data"]["room_name"] == "My Room"

    async def test_handle_room_create_empty_name(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-create2", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "room_create",
            "data": {"room_name": ""},
        })
        call_args = ws.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "error"

    async def test_handle_room_join(self):
        ws1 = AsyncMock()
        ws1.client_state.name = "CONNECTED"
        ws1.send_json = AsyncMock()
        pid1 = uuid.uuid4()
        info1 = ConnectionInfo(pid1, "Host", "conn-host", ws1)
        self.mgr._connections[pid1] = info1

        await self.dispatcher.dispatch(info1, {
            "event": "room_create",
            "data": {"room_name": "Join Room", "room_type": "quick_play"},
        })

        room_id = info1.room_id

        ws2 = AsyncMock()
        ws2.client_state.name = "CONNECTED"
        ws2.send_json = AsyncMock()
        pid2 = uuid.uuid4()
        info2 = ConnectionInfo(pid2, "Joiner", "conn-join", ws2)
        self.mgr._connections[pid2] = info2

        await self.dispatcher.dispatch(info2, {
            "event": "room_join",
            "data": {"room_id": str(room_id)},
        })
        ws2.send_json.assert_called()
        call_args = ws2.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "room_info"
        assert info2.room_id == room_id

    async def test_handle_room_join_missing_id(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-join2", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "room_join",
            "data": {},
        })
        call_args = ws.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "error"

    async def test_handle_room_join_not_found(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-join3", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "room_join",
            "data": {"room_id": str(uuid.uuid4())},
        })
        call_args = ws.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "error"

    async def test_handle_room_leave(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-leave", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "room_create",
            "data": {"room_name": "Leave Room"},
        })
        assert info.room_id is not None

        await self.dispatcher.dispatch(info, {"event": "room_leave", "data": {}})
        assert info.room_id is None

    async def test_handle_room_leave_not_in_room(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-leave2", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {"event": "room_leave", "data": {}})

    async def test_handle_room_list(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-list", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {"event": "room_list", "data": {}})
        ws.send_json.assert_called()
        call_args = ws.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "room_list"
        assert "rooms" in call_args["data"]

    async def test_handle_room_list_with_type(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-list2", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "room_list",
            "data": {"room_type": "race"},
        })
        ws.send_json.assert_called()

    async def test_handle_presence_update(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-presence", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "presence_update",
            "data": {"status": "away", "status_message": "brb"},
        })
        assert self.mgr.get_presence(pid) == PresenceStatus.AWAY

    async def test_handle_notification_ack(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-ack", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "notification_ack",
            "data": {"notification_id": str(uuid.uuid4())},
        })

    async def test_handle_vehicle_update_no_room(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-veh", ws)
        self.mgr._connections[pid] = info

        await self.dispatcher.dispatch(info, {
            "event": "vehicle_update",
            "data": {"vehicle_id": str(uuid.uuid4()), "speed": 100.0},
        })

    async def test_handle_vehicle_update_in_room(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-veh2", ws)
        self.mgr._connections[pid] = info

        room = RoomInfo(
            room_id=uuid.uuid4(),
            room_name="Vehicle Room",
            room_type=RoomType.RACE,
        )
        room.members.add(pid)
        self.mgr._rooms[room.id] = room
        info.room_id = room.id

        other_ws = AsyncMock()
        other_ws.client_state.name = "CONNECTED"
        other_ws.send_json = AsyncMock()
        other_pid = uuid.uuid4()
        other_info = ConnectionInfo(other_pid, "Other", "conn-veh-other", other_ws)
        room.members.add(other_pid)
        self.mgr._connections[other_pid] = other_info

        vid = uuid.uuid4()
        await self.dispatcher.dispatch(info, {
            "event": "vehicle_update",
            "data": {
                "vehicle_id": str(vid),
                "speed": 150.0,
                "position_x": 10.0,
                "position_y": 0.0,
                "position_z": 20.0,
            },
        })
        other_ws.send_json.assert_called_once()
        call_args = other_ws.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "vehicle_broadcast"

    async def test_dispatch_exception_handling(self):
        ws = AsyncMock()
        ws.client_state.name = "CONNECTED"
        ws.send_json = AsyncMock()
        pid = uuid.uuid4()
        info = ConnectionInfo(pid, "Test", "conn-err", ws)
        self.mgr._connections[pid] = info

        async def bad_handler(conn, data, dispatcher):
            raise RuntimeError("boom")

        self.dispatcher.register(WSEventType.AUTH, bad_handler)
        await self.dispatcher.dispatch(info, {"event": "auth", "data": {"token": "x"}})
        ws.send_json.assert_called()
        call_args = ws.send_json.call_args_list[0][0][0]
        assert call_args["event"] == "error"


# ── REST API Tests ─────────────────────────────────────────────────────────────


class TestMultiplayerREST:
    async def test_list_rooms(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/multiplayer/rooms", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        assert "total" in data

    async def test_create_room(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/multiplayer/rooms",
            json={
                "room_name": "API Room",
                "room_type": "quick_play",
                "max_players": 8,
                "region": "us-east",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["room_name"] == "API Room"

    async def test_create_room_invalid_name(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/multiplayer/rooms",
            json={"room_name": "", "room_type": "quick_play"},
            headers=auth_headers,
        )
        assert response.status_code in (400, 422)

    async def test_get_room(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/multiplayer/rooms",
            json={"room_name": "Get API Room", "room_type": "race"},
            headers=auth_headers,
        )
        room_id = create_resp.json()["data"]["id"]

        response = await client.get(
            f"/api/v1/multiplayer/rooms/{room_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["room_name"] == "Get API Room"

    async def test_update_room(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/multiplayer/rooms",
            json={"room_name": "Update API Room"},
            headers=auth_headers,
        )
        room_id = create_resp.json()["data"]["id"]

        response = await client.patch(
            f"/api/v1/multiplayer/rooms/{room_id}",
            json={"room_name": "Updated API Room"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["room_name"] == "Updated API Room"

    async def test_delete_room(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/multiplayer/rooms",
            json={"room_name": "Delete API Room"},
            headers=auth_headers,
        )
        room_id = create_resp.json()["data"]["id"]

        response = await client.delete(
            f"/api/v1/multiplayer/rooms/{room_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

    async def test_get_sessions(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            "/api/v1/multiplayer/sessions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_get_stats(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            "/api/v1/multiplayer/stats",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_rooms" in data["data"]

    async def test_unauthorized_access(self, client: AsyncClient):
        response = await client.get("/api/v1/multiplayer/rooms")
        assert response.status_code == 401
