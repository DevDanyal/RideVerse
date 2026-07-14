"""Serialization/deserialization helpers."""

from datetime import datetime, date
from typing import Any


def serialize_datetime(dt: datetime) -> str | None:
    """Serialize a datetime to ISO 8601 string."""
    if dt is None:
        return None
    return dt.isoformat()


def deserialize_datetime(value: str | None) -> datetime | None:
    """Deserialize an ISO 8601 string to datetime."""
    if value is None:
        return None
    return datetime.fromisoformat(value)


def serialize_date(d: date) -> str | None:
    """Serialize a date to ISO 8601 string."""
    if d is None:
        return None
    return d.isoformat()


def model_to_dict(model: Any, exclude: set[str] | None = None) -> dict:
    """Convert a SQLAlchemy model instance to a dictionary.

    Args:
        model: SQLAlchemy model instance.
        exclude: Set of field names to exclude.

    Returns:
        Dictionary representation of the model.
    """
    exclude = exclude or set()
    result = {}
    for column in model.__table__.columns:
        if column.name not in exclude:
            value = getattr(model, column.name)
            if isinstance(value, datetime):
                value = serialize_datetime(value)
            elif isinstance(value, date):
                value = serialize_date(value)
            result[column.name] = value
    return result


def dict_to_model(model_class: Any, data: dict) -> Any:
    """Create a model instance from a dictionary.

    Args:
        model_class: SQLAlchemy model class.
        data: Dictionary of field values.

    Returns:
        New model instance.
    """
    return model_class(**{k: v for k, v in data.items() if hasattr(model_class, k)})


def paginate_list(items: list, page: int = 1, page_size: int = 20) -> dict:
    """Paginate a list of items.

    Args:
        items: Full list of items.
        page: Page number (1-indexed).
        page_size: Items per page.

    Returns:
        dict with items, total, page, page_size, and total_pages.
    """
    total = len(items)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def serialize_response(data: Any, message: str = "Success") -> dict:
    """Wrap data in a standard API response envelope."""
    return {
        "status": "success",
        "message": message,
        "data": data,
    }


def serialize_error(message: str, errors: list[str] | None = None) -> dict:
    """Create a standard error response."""
    return {
        "status": "error",
        "message": message,
        "errors": errors or [],
    }


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
