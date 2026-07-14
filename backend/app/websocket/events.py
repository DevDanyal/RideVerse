"""WebSocket event type definitions."""

from enum import Enum


class WSEventType(str, Enum):
    """WebSocket event type constants."""

    AUTH = "auth"
    CHAT = "chat"
    POSITION = "position"
    VEHICLE = "vehicle"
    TYPING = "typing"
    NOTIFICATION = "notification"
    MISSION_UPDATE = "mission_update"
    WEATHER_UPDATE = "weather_update"
    TRAFFIC_UPDATE = "traffic_update"
    POLICE_ALERT = "police_alert"
    FRIEND_REQUEST = "friend_request"
    CLUB_MESSAGE = "club_message"
    MARKETPLACE_UPDATE = "marketplace_update"
    SYSTEM_BROADCAST = "system_broadcast"
    PING = "ping"
    PONG = "pong"


class WSChannel(str, Enum):
    """WebSocket channel constants."""

    GLOBAL = "global"
    WORLD = "world"
    CHAT = "chat"
    CLUB = "club"
    PARTY = "party"
    TRADE = "trade"
    POLICE = "police"
    SYSTEM = "system"


class WSConnectionState(str, Enum):
    """WebSocket connection state constants."""

    CONNECTING = "connecting"
    AUTHENTICATED = "authenticated"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
