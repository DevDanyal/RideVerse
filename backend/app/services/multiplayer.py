"""Multiplayer service — orchestrates room, session, position, and presence logic."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.multiplayer import (
    ConnectionStatus,
    PresenceStatus,
    RoomStatus,
    RoomType,
)
from app.repositories.multiplayer import MultiplayerRepository

logger = logging.getLogger(__name__)


class MultiplayerService:
    """Orchestrates multiplayer operations including rooms, sessions, and persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = MultiplayerRepository(session)
        self._session = session

    # ── Room Operations ────────────────────────────────────────────────────────

    async def create_room(
        self,
        player_id: uuid.UUID,
        room_name: str,
        room_type: str = "quick_play",
        max_players: int = 16,
        region: str = "global",
        password: str | None = None,
        map_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a new multiplayer room."""
        if not room_name or len(room_name) > 100:
            raise ValidationError("Room name must be 1-100 characters")
        if max_players < 2 or max_players > 100:
            raise ValidationError("Max players must be 2-100")

        existing = await self._repo.get_player_room_membership(player_id)
        if existing is not None:
            raise ValidationError("You are already in a room. Leave first.")

        room = await self._repo.create_room(
            {
                "room_name": room_name,
                "room_type": room_type,
                "room_status": RoomStatus.WAITING,
                "max_players": max_players,
                "current_player_count": 1,
                "region": region,
                "host_player_id": player_id,
                "map_name": map_name,
            }
        )

        await self._repo.add_room_member(room.id, player_id, is_host=True)

        logger.info("Room created: %s by %s", room.id, player_id)

        room_type_val = room.room_type.value if hasattr(room.room_type, "value") else str(room.room_type)
        room_status_val = room.room_status.value if hasattr(room.room_status, "value") else str(room.room_status)

        return {
            "id": room.id,
            "room_name": room.room_name,
            "room_type": room_type_val,
            "room_status": room_status_val,
            "max_players": room.max_players,
            "current_player_count": 1,
            "region": room.region,
            "host_player_id": room.host_player_id,
            "map_name": room.map_name,
            "created_at": room.created_at,
        }

    async def get_room(self, room_id: uuid.UUID) -> dict[str, Any]:
        """Get room details."""
        room = await self._repo.get_room_by_id(room_id)
        if room is None:
            raise NotFoundError("Room not found")

        members = await self._repo.get_room_members(room_id)
        room_type_val = room.room_type.value if hasattr(room.room_type, "value") else str(room.room_type)
        room_status_val = room.room_status.value if hasattr(room.room_status, "value") else str(room.room_status)
        return {
            "id": room.id,
            "room_name": room.room_name,
            "room_type": room_type_val,
            "room_status": room_status_val,
            "max_players": room.max_players,
            "current_player_count": len(members),
            "region": room.region,
            "host_player_id": room.host_player_id,
            "map_name": room.map_name,
            "members": [
                {
                    "player_id": m.player_id,
                    "is_host": m.is_host,
                    "is_ready": m.is_ready,
                    "joined_at": m.joined_at,
                }
                for m in members
            ],
            "created_at": room.created_at,
        }

    async def list_rooms(
        self,
        room_type: str | None = None,
        region: str | None = None,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        """List rooms with pagination."""
        total = await self._repo.count_rooms(room_type=room_type, region=region)
        rooms = await self._repo.list_rooms(
            room_type=room_type,
            region=region,
            status=status,
            skip=(page - 1) * per_page,
            limit=per_page,
        )
        return {
            "rooms": [
                {
                    "id": r.id,
                    "room_name": r.room_name,
                    "room_type": r.room_type.value if hasattr(r.room_type, "value") else str(r.room_type),
                    "room_status": r.room_status.value if hasattr(r.room_status, "value") else str(r.room_status),
                    "max_players": r.max_players,
                    "current_player_count": r.current_player_count,
                    "region": r.region,
                    "has_password": r.password_hash is not None,
                    "map_name": r.map_name,
                    "created_at": r.created_at,
                }
                for r in rooms
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": max(1, -(-total // per_page)),
        }

    async def update_room(
        self,
        room_id: uuid.UUID,
        player_id: uuid.UUID,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update room settings (host only)."""
        room = await self._repo.get_room_by_id(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        if room.host_player_id != player_id:
            raise ValidationError("Only the host can update room settings")

        allowed = {"room_name", "max_players", "room_status", "map_name"}
        filtered = {k: v for k, v in kwargs.items() if v is not None and k in allowed}
        if not filtered:
            return await self.get_room(room_id)

        updated = await self._repo.update_room(room_id, **filtered)
        if updated is None:
            raise NotFoundError("Room not found")

        return await self.get_room(room_id)

    async def delete_room(self, room_id: uuid.UUID, player_id: uuid.UUID) -> bool:
        """Delete a room (host only)."""
        room = await self._repo.get_room_by_id(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        if room.host_player_id != player_id:
            raise ValidationError("Only the host can delete the room")

        return await self._repo.delete_room(room_id)

    # ── WebSocket Session Operations ───────────────────────────────────────────

    async def register_session(
        self,
        player_id: uuid.UUID,
        connection_id: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        """Register a new WebSocket session."""
        now = datetime.now(timezone.utc)
        session = await self._repo.create_ws_session(
            {
                "player_id": player_id,
                "connection_id": connection_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "connected_at": now,
                "last_heartbeat": now,
                "connection_status": ConnectionStatus.CONNECTED,
            }
        )
        return {
            "id": session.id,
            "player_id": session.player_id,
            "connection_id": session.connection_id,
            "connection_status": session.connection_status.value,
            "connected_at": session.connected_at,
        }

    async def close_session(self, connection_id: str) -> bool:
        """Mark a WebSocket session as disconnected."""
        return await self._repo.close_ws_session(connection_id)

    async def update_heartbeat(self, connection_id: str) -> None:
        """Update the last heartbeat time for a session."""
        await self._repo.update_ws_session(
            connection_id,
            last_heartbeat=datetime.now(timezone.utc),
        )

    async def get_player_sessions(self, player_id: uuid.UUID) -> list[dict[str, Any]]:
        """Get all WebSocket sessions for a player."""
        sessions = await self._repo.get_ws_sessions_by_player(player_id)
        return [
            {
                "id": s.id,
                "connection_id": s.connection_id,
                "room_id": s.room_id,
                "connection_status": s.connection_status.value,
                "connected_at": s.connected_at,
                "last_heartbeat": s.last_heartbeat,
                "messages_sent": s.messages_sent,
                "messages_received": s.messages_received,
            }
            for s in sessions
        ]

    # ── Position Operations ────────────────────────────────────────────────────

    async def update_player_position(
        self,
        player_id: uuid.UUID,
        room_id: uuid.UUID | None,
        position_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update or create a player's position record."""
        position_data["room_id"] = room_id
        position_data["last_updated"] = datetime.now(timezone.utc)
        position = await self._repo.upsert_player_position(player_id, position_data)
        return {
            "player_id": position.player_id,
            "position_x": position.position_x,
            "position_y": position.position_y,
            "position_z": position.position_z,
            "speed": position.speed,
            "is_in_vehicle": position.is_in_vehicle,
            "last_updated": position.last_updated,
        }

    async def get_player_position(self, player_id: uuid.UUID) -> dict[str, Any] | None:
        """Get a player's last known position."""
        position = await self._repo.get_player_position(player_id)
        if position is None:
            return None
        return {
            "player_id": position.player_id,
            "position_x": position.position_x,
            "position_y": position.position_y,
            "position_z": position.position_z,
            "rotation_x": position.rotation_x,
            "rotation_y": position.rotation_y,
            "rotation_z": position.rotation_z,
            "speed": position.speed,
            "is_in_vehicle": position.is_in_vehicle,
            "vehicle_id": position.vehicle_id,
            "last_updated": position.last_updated,
        }

    async def get_room_positions(self, room_id: uuid.UUID) -> list[dict[str, Any]]:
        """Get all player positions in a room."""
        positions = await self._repo.get_room_positions(room_id)
        return [
            {
                "player_id": p.player_id,
                "position_x": p.position_x,
                "position_y": p.position_y,
                "position_z": p.position_z,
                "speed": p.speed,
                "is_in_vehicle": p.is_in_vehicle,
            }
            for p in positions
        ]

    # ── Vehicle Sync Operations ────────────────────────────────────────────────

    async def update_vehicle_sync(
        self,
        player_id: uuid.UUID,
        room_id: uuid.UUID | None,
        vehicle_id: uuid.UUID,
        vehicle_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update or create a vehicle sync record."""
        vehicle_data["room_id"] = room_id
        vehicle_data["last_updated"] = datetime.now(timezone.utc)
        sync = await self._repo.upsert_vehicle_sync(player_id, vehicle_id, vehicle_data)
        return {
            "player_id": sync.player_id,
            "vehicle_id": sync.vehicle_id,
            "speed": sync.speed,
            "health": sync.health,
            "fuel": sync.fuel,
            "last_updated": sync.last_updated,
        }

    # ── Presence Operations ────────────────────────────────────────────────────

    async def update_presence(
        self,
        player_id: uuid.UUID,
        status: str,
        status_message: str | None = None,
    ) -> dict[str, Any]:
        """Update a player's presence status."""
        presence = await self._repo.upsert_presence(
            player_id,
            {
                "status": status,
                "last_seen": datetime.now(timezone.utc),
                "status_message": status_message,
            },
        )
        status_val = presence.status.value if hasattr(presence.status, "value") else str(presence.status)
        return {
            "player_id": presence.player_id,
            "status": status_val,
            "last_seen": presence.last_seen,
            "status_message": presence.status_message,
        }

    async def get_presence(self, player_id: uuid.UUID) -> dict[str, Any] | None:
        """Get a player's presence."""
        presence = await self._repo.get_presence(player_id)
        if presence is None:
            return None
        status_val = presence.status.value if hasattr(presence.status, "value") else str(presence.status)
        return {
            "player_id": presence.player_id,
            "status": status_val,
            "last_seen": presence.last_seen,
            "current_room_id": presence.current_room_id,
            "status_message": presence.status_message,
        }

    # ── Chat Operations ────────────────────────────────────────────────────────

    async def save_chat_message(
        self,
        room_id: uuid.UUID,
        player_id: uuid.UUID,
        message: str,
        message_type: str = "chat",
    ) -> dict[str, Any]:
        """Persist a chat message."""
        msg = await self._repo.create_chat_message(
            {
                "room_id": room_id,
                "player_id": player_id,
                "message": message,
                "message_type": message_type,
            }
        )
        return {
            "message_id": msg.id,
            "room_id": msg.room_id,
            "player_id": msg.player_id,
            "message": msg.message,
            "message_type": msg.message_type,
            "created_at": msg.created_at,
        }

    async def get_room_messages(
        self, room_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get chat history for a room."""
        messages = await self._repo.get_room_messages(room_id, skip=skip, limit=limit)
        return [
            {
                "message_id": m.id,
                "player_id": m.player_id,
                "message": m.message,
                "message_type": m.message_type,
                "created_at": m.created_at,
            }
            for m in messages
        ]

    # ── Statistics ─────────────────────────────────────────────────────────────

    async def get_statistics(self) -> dict[str, Any]:
        """Get multiplayer statistics."""
        total_rooms = await self._repo.get_total_rooms()
        active_connections = await self._repo.get_active_connections()
        total_messages = await self._repo.get_total_messages()
        return {
            "total_rooms": total_rooms,
            "active_rooms": 0,
            "total_connections": active_connections,
            "active_connections": active_connections,
            "total_messages": total_messages,
            "peak_concurrent": 0,
        }
