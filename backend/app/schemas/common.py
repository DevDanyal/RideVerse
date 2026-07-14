from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Generic envelope for successful responses."""

    success: bool = True
    message: str = "OK"
    data: T | None = None


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """Generic envelope for error responses."""

    success: bool = False
    message: str = "An error occurred"
    error_code: str = "UNKNOWN"
    errors: list[ErrorDetail] = Field(default_factory=list)


class PaginationParams(BaseModel):
    """Query-string pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list of items."""

    items: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    total_pages: int = 0


class IDResponse(BaseModel):
    """Return a single UUID identifier."""

    id: uuid.UUID
