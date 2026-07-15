"""Repository layer for multiplayer-related database operations."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.multiplayer import (
    ConnectionStatus,
    FriendPresence,
    MultiplayerChatMessage,
    MultiplayerRoom,
    PlayerPosition,
    PlayerPresence,
    PresenceStatus,
    RateLimitRecord,
    RoomMember,
    RoomStatus,
    VehicleSync,
    WebSocketSession,
)


class MultiplayerRepository:
    """Data-access layer for multiplayer models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Room Operations ────────────────────────────────────────────────────────

    async def create_room(self, data: dict[str, Any]) -> MultiplayerRoom:
        room = MultiplayerRoom(**data)
        self._session.add(room)
        await self._session.flush()
        return room

    async def get_room_by_id(self, room_id: uuid.UUID) -> MultiplayerRoom | None:
        stmt = select(MultiplayerRoom).where(
            MultiplayerRoom.id == room_id,
            MultiplayerRoom.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_rooms(
        self,
        room_type: str | None = None,
        region: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[MultiplayerRoom]:
        stmt = select(MultiplayerRoom).where(MultiplayerRoom.is_deleted.is_(False))
        if room_type is not None:
            stmt = stmt.where(MultiplayerRoom.room_type == room_type)
        if region is not None:
            stmt = stmt.where(MultiplayerRoom.region == region)
        if status is not None:
            stmt = stmt.where(MultiplayerRoom.room_status == status)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_rooms(
        self,
        room_type: str | None = None,
        region: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(MultiplayerRoom).where(
            MultiplayerRoom.is_deleted.is_(False)
        )
        if room_type is not None:
            stmt = stmt.where(MultiplayerRoom.room_type == room_type)
        if region is not None:
            stmt = stmt.where(MultiplayerRoom.region == region)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update_room(self, room_id: uuid.UUID, **kwargs: Any) -> MultiplayerRoom | None:
        stmt = (
            update(MultiplayerRoom)
            .where(MultiplayerRoom.id == room_id, MultiplayerRoom.is_deleted.is_(False))
            .values(**kwargs)
            .returning(MultiplayerRoom)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_room(self, room_id: uuid.UUID) -> bool:
        stmt = (
            update(MultiplayerRoom)
            .where(MultiplayerRoom.id == room_id)
            .values(is_deleted=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Room Member Operations ─────────────────────────────────────────────────

    async def add_room_member(self, room_id: uuid.UUID, player_id: uuid.UUID, is_host: bool = False) -> RoomMember:
        member = RoomMember(
            room_id=room_id,
            player_id=player_id,
            is_host=is_host,
            is_ready=False,
            joined_at=datetime.now(timezone.utc),
        )
        self._session.add(member)
        await self._session.flush()
        return member

    async def remove_room_member(self, room_id: uuid.UUID, player_id: uuid.UUID) -> bool:
        stmt = (
            update(RoomMember)
            .where(
                RoomMember.room_id == room_id,
                RoomMember.player_id == player_id,
                RoomMember.left_at.is_(None),
            )
            .values(left_at=datetime.now(timezone.utc))
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_room_members(self, room_id: uuid.UUID) -> list[RoomMember]:
        stmt = select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.left_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_player_room_membership(self, player_id: uuid.UUID) -> RoomMember | None:
        stmt = select(RoomMember).where(
            RoomMember.player_id == player_id,
            RoomMember.left_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_room_member(self, room_id: uuid.UUID, player_id: uuid.UUID, **kwargs: Any) -> RoomMember | None:
        stmt = (
            update(RoomMember)
            .where(
                RoomMember.room_id == room_id,
                RoomMember.player_id == player_id,
            )
            .values(**kwargs)
            .returning(RoomMember)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── WebSocket Session Operations ───────────────────────────────────────────

    async def create_ws_session(self, data: dict[str, Any]) -> WebSocketSession:
        session = WebSocketSession(**data)
        self._session.add(session)
        await self._session.flush()
        return session

    async def get_ws_session_by_connection_id(self, connection_id: str) -> WebSocketSession | None:
        stmt = select(WebSocketSession).where(
            WebSocketSession.connection_id == connection_id,
            WebSocketSession.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_ws_sessions_by_player(self, player_id: uuid.UUID) -> list[WebSocketSession]:
        stmt = select(WebSocketSession).where(
            WebSocketSession.player_id == player_id,
            WebSocketSession.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_ws_session(self, connection_id: str, **kwargs: Any) -> WebSocketSession | None:
        stmt = (
            update(WebSocketSession)
            .where(WebSocketSession.connection_id == connection_id)
            .values(**kwargs)
            .returning(WebSocketSession)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def close_ws_session(self, connection_id: str) -> bool:
        return await self.update_ws_session(
            connection_id,
            connection_status=ConnectionStatus.DISCONNECTED,
        ) is not None

    # ── Player Position Operations ─────────────────────────────────────────────

    async def upsert_player_position(self, player_id: uuid.UUID, data: dict[str, Any]) -> PlayerPosition:
        stmt = select(PlayerPosition).where(PlayerPosition.player_id == player_id)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            for key, value in data.items():
                setattr(existing, key, value)
            await self._session.flush()
            return existing

        position = PlayerPosition(player_id=player_id, **data)
        self._session.add(position)
        await self._session.flush()
        return position

    async def get_player_position(self, player_id: uuid.UUID) -> PlayerPosition | None:
        stmt = select(PlayerPosition).where(PlayerPosition.player_id == player_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_room_positions(self, room_id: uuid.UUID) -> list[PlayerPosition]:
        stmt = select(PlayerPosition).where(PlayerPosition.room_id == room_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ── Vehicle Sync Operations ────────────────────────────────────────────────

    async def upsert_vehicle_sync(self, player_id: uuid.UUID, vehicle_id: uuid.UUID, data: dict[str, Any]) -> VehicleSync:
        stmt = select(VehicleSync).where(
            VehicleSync.player_id == player_id,
            VehicleSync.vehicle_id == vehicle_id,
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            for key, value in data.items():
                setattr(existing, key, value)
            await self._session.flush()
            return existing

        sync = VehicleSync(player_id=player_id, vehicle_id=vehicle_id, **data)
        self._session.add(sync)
        await self._session.flush()
        return sync

    async def get_vehicle_sync(self, player_id: uuid.UUID, vehicle_id: uuid.UUID) -> VehicleSync | None:
        stmt = select(VehicleSync).where(
            VehicleSync.player_id == player_id,
            VehicleSync.vehicle_id == vehicle_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Presence Operations ────────────────────────────────────────────────────

    async def upsert_presence(self, player_id: uuid.UUID, data: dict[str, Any]) -> PlayerPresence:
        stmt = select(PlayerPresence).where(PlayerPresence.player_id == player_id)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            for key, value in data.items():
                setattr(existing, key, value)
            await self._session.flush()
            return existing

        presence = PlayerPresence(player_id=player_id, **data)
        self._session.add(presence)
        await self._session.flush()
        return presence

    async def get_presence(self, player_id: uuid.UUID) -> PlayerPresence | None:
        stmt = select(PlayerPresence).where(PlayerPresence.player_id == player_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_online_friends(self, player_id: uuid.UUID) -> list[PlayerPresence]:
        stmt = select(PlayerPresence).where(
            PlayerPresence.player_id != player_id,
            PlayerPresence.status != PresenceStatus.OFFLINE,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ── Friend Presence Operations ─────────────────────────────────────────────

    async def upsert_friend_presence(
        self,
        player_id: uuid.UUID,
        friend_player_id: uuid.UUID,
        data: dict[str, Any],
    ) -> FriendPresence:
        stmt = select(FriendPresence).where(
            FriendPresence.player_id == player_id,
            FriendPresence.friend_player_id == friend_player_id,
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            for key, value in data.items():
                setattr(existing, key, value)
            await self._session.flush()
            return existing

        fp = FriendPresence(player_id=player_id, friend_player_id=friend_player_id, **data)
        self._session.add(fp)
        await self._session.flush()
        return fp

    # ── Chat Message Operations ────────────────────────────────────────────────

    async def create_chat_message(self, data: dict[str, Any]) -> MultiplayerChatMessage:
        msg = MultiplayerChatMessage(**data)
        self._session.add(msg)
        await self._session.flush()
        return msg

    async def get_room_messages(
        self, room_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[MultiplayerChatMessage]:
        stmt = (
            select(MultiplayerChatMessage)
            .where(MultiplayerChatMessage.room_id == room_id)
            .order_by(MultiplayerChatMessage.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ── Rate Limit Operations ──────────────────────────────────────────────────

    async def get_or_create_rate_limit(
        self, player_id: uuid.UUID, event_type: str, window_start: datetime
    ) -> RateLimitRecord:
        stmt = select(RateLimitRecord).where(
            RateLimitRecord.player_id == player_id,
            RateLimitRecord.event_type == event_type,
            RateLimitRecord.window_start == window_start,
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            existing.message_count += 1
            await self._session.flush()
            return existing

        record = RateLimitRecord(
            player_id=player_id,
            event_type=event_type,
            window_start=window_start,
            message_count=1,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    # ── Statistics ─────────────────────────────────────────────────────────────

    async def get_total_rooms(self) -> int:
        stmt = select(func.count()).select_from(MultiplayerRoom).where(
            MultiplayerRoom.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_active_connections(self) -> int:
        stmt = select(func.count()).select_from(WebSocketSession).where(
            WebSocketSession.connection_status == ConnectionStatus.CONNECTED,
            WebSocketSession.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_total_messages(self) -> int:
        stmt = select(func.count()).select_from(MultiplayerChatMessage)
        result = await self._session.execute(stmt)
        return result.scalar_one()
