from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health status of a single system component."""

    name: str
    status: HealthStatus
    latency_ms: float = Field(default=0.0, ge=0)
    message: str = ""


class HealthResponse(BaseModel):
    """Top-level health check response."""

    status: HealthStatus
    version: str = "0.1.0"
    uptime: float = Field(default=0.0, ge=0, description="Uptime in seconds")
    components: list[ComponentHealth] = Field(default_factory=list)
