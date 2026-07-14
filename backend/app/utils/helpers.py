"""Common helper functions."""

import uuid
import hashlib
import time
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def generate_short_id() -> str:
    """Generate a short 8-character ID."""
    return uuid.uuid4().hex[:8]


def format_currency(amount: int | float, currency: str = "$") -> str:
    """Format a numeric amount as currency string."""
    if amount < 0:
        return f"-{currency}{abs(amount):,.2f}"
    return f"{currency}{amount:,.2f}"


def parse_currency(value: str, currency: str = "$") -> float:
    """Parse a currency string back to a float."""
    cleaned = value.replace(currency, "").replace(",", "").strip()
    return float(cleaned)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 (placeholder — use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed


def timestamp_now() -> float:
    """Return current Unix timestamp."""
    return time.time()


def sanitize_input(value: str, max_length: int = 255) -> str:
    """Trim and truncate user input."""
    return value.strip()[:max_length]


def chunk_list(items: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of given size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, with override taking precedence."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
