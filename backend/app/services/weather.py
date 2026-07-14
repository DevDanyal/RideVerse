from __future__ import annotations

from typing import Any


class WeatherService:
    """Business logic for the dynamic weather system."""

    def __init__(self) -> None:
        pass

    async def get_current_weather(self, city: str = "los_santos") -> dict[str, Any]:
        """Return the current weather conditions for a city."""
        pass

    async def get_forecast(self, city: str = "los_santos") -> list[dict[str, Any]]:
        """Return a weather forecast for the next several hours."""
        pass

    async def advance_weather(self) -> dict[str, Any]:
        """Tick the weather simulation forward (called by the game loop)."""
        pass
