from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    FOGGY = "foggy"
    SNOWY = "snowy"
    WINDY = "windy"


class WeatherResponse(BaseModel):
    """Current weather data."""

    current_weather: WeatherCondition
    temperature: float = Field(default=20.0, description="Celsius")
    wind_speed: float = Field(default=0.0, ge=0, description="km/h")
    wind_direction: float = Field(default=0.0, ge=0, le=360, description="Degrees")
    humidity: float = Field(default=50.0, ge=0, le=100, description="Percentage")
    visibility: float = Field(default=1000.0, ge=0, description="Meters")
    precipitation: float = Field(default=0.0, ge=0, description="mm/h")
    updated_at: datetime | None = None


class ForecastEntry(BaseModel):
    """A single forecast entry."""

    time: datetime
    weather: WeatherCondition
    temperature: float
    wind_speed: float
    precipitation: float


class ForecastResponse(BaseModel):
    """Weather forecast for the coming hours."""

    forecast: list[ForecastEntry] = Field(default_factory=list)
    city: str = ""
