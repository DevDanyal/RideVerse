"""WebSocket channel management."""

from dataclasses import dataclass, field
from app.websocket.manager import manager


@dataclass
class ChannelConfig:
    """Configuration for a WebSocket channel."""

    name: str
    max_members: int = 1000
    requires_auth: bool = True
    description: str = ""


DEFAULT_CHANNELS: dict[str, ChannelConfig] = {
    "global": ChannelConfig(name="global", description="Global chat channel"),
    "world": ChannelConfig(name="world", description="World state updates", requires_auth=True),
    "club": ChannelConfig(name="club", description="Club chat", requires_auth=True),
    "party": ChannelConfig(name="party", description="Party chat", requires_auth=True),
    "trade": ChannelConfig(name="trade", description="Trade channel", requires_auth=True),
    "police": ChannelConfig(name="police", description="Police alerts", requires_auth=True),
    "system": ChannelConfig(name="system", description="System broadcasts", requires_auth=False),
}


class ChannelManager:
    """Manages channel subscriptions and configurations."""

    def __init__(self):
        self._channels: dict[str, ChannelConfig] = dict(DEFAULT_CHANNELS)

    def get_channel(self, channel_name: str) -> ChannelConfig | None:
        """Get channel config by name."""
        return self._channels.get(channel_name)

    def create_channel(self, config: ChannelConfig) -> None:
        """Create a new channel."""
        self._channels[config.name] = config

    def delete_channel(self, channel_name: str) -> bool:
        """Delete a channel."""
        if channel_name in self._channels and channel_name not in DEFAULT_CHANNELS:
            del self._channels[channel_name]
            return True
        return False

    def list_channels(self) -> list[ChannelConfig]:
        """List all channels."""
        return list(self._channels.values())

    def join_channel(self, player_id: str, channel_name: str) -> bool:
        """Subscribe a player to a channel."""
        config = self._channels.get(channel_name)
        if not config:
            return False
        manager.subscribe(player_id, channel_name)
        return True

    def leave_channel(self, player_id: str, channel_name: str) -> bool:
        """Unsubscribe a player from a channel."""
        manager.unsubscribe(player_id, channel_name)
        return True


channel_manager = ChannelManager()
