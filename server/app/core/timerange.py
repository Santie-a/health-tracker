"""Local-day → UTC instant bounds for day-scoped reads.

The gateway stores timestamps as UTC instants, but the (single) user navigates in their
local calendar days. Bucketing "a day" by UTC instead of the configured `APP_TIMEZONE`
drops local-evening entries into the next day — e.g. a meal logged at 18:00 local in a
UTC-6 zone is the 00:00Z instant of the *next* date, so a UTC-day query for "today" misses
it. These helpers turn a local calendar date into the [start, end) UTC instants spanning
it, so the `ts >= start AND ts < end` filters bucket by the user's day.

`APP_TIMEZONE` defaults to UTC, which preserves the original naive behavior.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from app.core.config import get_settings


def tz_name() -> str:
    """The configured IANA timezone name (for SQL `date_trunc`/`AT TIME ZONE`)."""
    return get_settings().app_timezone


def app_tz() -> ZoneInfo:
    """The configured local timezone. ZoneInfo caches instances by key, so this is cheap."""
    return ZoneInfo(tz_name())


def _local_midnight_utc(day: date) -> datetime:
    """The UTC instant of local midnight beginning `day` (DST-correct via ZoneInfo)."""
    return datetime.combine(day, time.min, tzinfo=app_tz()).astimezone(timezone.utc)


def day_bounds(day: date) -> tuple[datetime, datetime]:
    """[start, end) UTC instants spanning the local calendar `day`."""
    return _local_midnight_utc(day), _local_midnight_utc(day + timedelta(days=1))


def range_bounds(frm: date, to: date) -> tuple[datetime, datetime]:
    """[start, end) UTC instants spanning local days `frm`..`to` inclusive."""
    return _local_midnight_utc(frm), _local_midnight_utc(to + timedelta(days=1))
