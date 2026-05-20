from datetime import UTC, datetime


def get_current_datetime_utc() -> datetime:
    """Return current datetime in UTC format."""
    return datetime.now(UTC)
