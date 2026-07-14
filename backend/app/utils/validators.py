"""Input validation helpers."""

import re
from app.utils.constants import (
    MIN_USERNAME_LENGTH,
    MAX_USERNAME_LENGTH,
    MAX_MESSAGE_LENGTH,
    MAX_CLUB_NAME_LENGTH,
    MIN_CLUB_NAME_LENGTH,
    ITEM_RARITY,
    VEHICLE_TYPES,
    MISSION_TYPES,
)


def validate_username(username: str) -> tuple[bool, str]:
    """Validate a username.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not username or not username.strip():
        return False, "Username is required"
    if len(username) < MIN_USERNAME_LENGTH:
        return False, f"Username must be at least {MIN_USERNAME_LENGTH} characters"
    if len(username) > MAX_USERNAME_LENGTH:
        return False, f"Username must be at most {MAX_USERNAME_LENGTH} characters"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """Validate an email address."""
    if not email or not email.strip():
        return False, "Email is required"
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Validate a password strength."""
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 128:
        return False, "Password must be at most 128 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    return True, ""


def validate_chat_message(message: str) -> tuple[bool, str]:
    """Validate a chat message."""
    if not message or not message.strip():
        return False, "Message cannot be empty"
    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"Message must be at most {MAX_MESSAGE_LENGTH} characters"
    return True, ""


def validate_club_name(name: str) -> tuple[bool, str]:
    """Validate a club name."""
    if not name or not name.strip():
        return False, "Club name is required"
    if len(name) < MIN_CLUB_NAME_LENGTH:
        return False, f"Club name must be at least {MIN_CLUB_NAME_LENGTH} characters"
    if len(name) > MAX_CLUB_NAME_LENGTH:
        return False, f"Club name must be at most {MAX_CLUB_NAME_LENGTH} characters"
    if not re.match(r"^[a-zA-Z0-9 _-]+$", name):
        return False, "Club name contains invalid characters"
    return True, ""


def validate_vehicle_type(vehicle_type: str) -> tuple[bool, str]:
    """Validate a vehicle type."""
    if vehicle_type not in VEHICLE_TYPES:
        return False, f"Invalid vehicle type. Must be one of: {', '.join(VEHICLE_TYPES)}"
    return True, ""


def validate_item_rarity(rarity: str) -> tuple[bool, str]:
    """Validate item rarity."""
    if rarity not in ITEM_RARITY:
        return False, f"Invalid rarity. Must be one of: {', '.join(ITEM_RARITY)}"
    return True, ""


def validate_mission_type(mission_type: str) -> tuple[bool, str]:
    """Validate mission type."""
    if mission_type not in MISSION_TYPES:
        return False, f"Invalid mission type. Must be one of: {', '.join(MISSION_TYPES)}"
    return True, ""


def validate_positive_integer(value: int, field_name: str = "value") -> tuple[bool, str]:
    """Validate that a value is a positive integer."""
    if not isinstance(value, int) or value < 0:
        return False, f"{field_name} must be a positive integer"
    return True, ""


def validate_amount(amount: float, min_val: float = 0, max_val: float = float("inf"), field_name: str = "amount") -> tuple[bool, str]:
    """Validate a numeric amount within a range."""
    if not isinstance(amount, (int, float)):
        return False, f"{field_name} must be a number"
    if amount < min_val:
        return False, f"{field_name} must be at least {min_val}"
    if amount > max_val:
        return False, f"{field_name} must be at most {max_val}"
    return True, ""
