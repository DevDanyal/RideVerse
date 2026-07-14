"""DateTime utility functions."""

from datetime import datetime, timedelta, timezone


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def timestamp() -> float:
    """Return current UTC timestamp as a float."""
    return utc_now().timestamp()


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime to string."""
    if dt is None:
        return ""
    return dt.strftime(fmt)


def parse_datetime(value: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime | None:
    """Parse a datetime string."""
    if not value:
        return None
    try:
        return datetime.strptime(value, fmt)
    except ValueError:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None


def days_ago(days: int) -> datetime:
    """Return a datetime that is N days in the past."""
    return utc_now() - timedelta(days=days)


def hours_ago(hours: int) -> datetime:
    """Return a datetime that is N hours in the past."""
    return utc_now() - timedelta(hours=hours)


def minutes_ago(minutes: int) -> datetime:
    """Return a datetime that is N minutes in the past."""
    return utc_now() - timedelta(minutes=minutes)


def is_expired(expires_at: datetime) -> bool:
    """Check if a datetime has passed."""
    if expires_at is None:
        return False
    return utc_now() > expires_at


def time_remaining(expires_at: datetime) -> timedelta | None:
    """Return the time remaining until a datetime, or None if expired."""
    if expires_at is None:
        return None
    remaining = expires_at - utc_now()
    if remaining.total_seconds() < 0:
        return None
    return remaining


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """Check if two datetimes are on the same calendar day."""
    return dt1.date() == dt2.date()


def is_same_week(dt1: datetime, dt2: datetime) -> bool:
    """Check if two datetimes are in the same ISO week."""
    return dt1.isocalendar()[:2] == dt2.isocalendar()[:2]


def is_same_month(dt1: datetime, dt2: datetime) -> bool:
    """Check if two datetimes are in the same month and year."""
    return dt1.year == dt2.year and dt1.month == dt2.month


def start_of_day(dt: datetime | None = None) -> datetime:
    """Return the start of the day (midnight) for a given datetime."""
    dt = dt or utc_now()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime | None = None) -> datetime:
    """Return the end of the day (23:59:59) for a given datetime."""
    dt = dt or utc_now()
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def start_of_week(dt: datetime | None = None) -> datetime:
    """Return the start of the ISO week (Monday) for a given datetime."""
    dt = dt or utc_now()
    return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def start_of_month(dt: datetime | None = None) -> datetime:
    """Return the first day of the month for a given datetime."""
    dt = dt or utc_now()
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def cooldown_remaining(last_action: datetime, cooldown_seconds: int) -> int:
    """Return seconds remaining on a cooldown, or 0 if ready."""
    if last_action is None:
        return 0
    elapsed = (utc_now() - last_action).total_seconds()
    remaining = cooldown_seconds - elapsed
    return max(0, int(remaining))
