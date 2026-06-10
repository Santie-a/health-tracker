"""Local-day → UTC bounds. Guards the nutrition off-by-one: an entry logged in the
local evening (a next-UTC-day instant) must bucket into the local day."""

from datetime import date, datetime, timezone

import pytest

from app.core import timerange
from app.core.config import get_settings


@pytest.fixture
def costa_rica(monkeypatch):
    """APP_TIMEZONE = UTC-6, no DST. env var beats the .env file in pydantic-settings."""
    monkeypatch.setenv("APP_TIMEZONE", "America/Costa_Rica")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_day_bounds_uses_local_zone(costa_rica):
    start, end = timerange.day_bounds(date(2026, 6, 9))
    # local midnight is 06:00Z; the window is [Jun 9 06:00Z, Jun 10 06:00Z).
    assert start == datetime(2026, 6, 9, 6, tzinfo=timezone.utc)
    assert end == datetime(2026, 6, 10, 6, tzinfo=timezone.utc)


def test_local_evening_entry_belongs_to_local_day(costa_rica):
    # A meal logged 18:00 local on Jun 9 is the 00:00Z Jun 10 instant — the exact case
    # that the old UTC-day query dropped into Jun 10.
    meal_ts = datetime(2026, 6, 10, 0, tzinfo=timezone.utc)
    start, end = timerange.day_bounds(date(2026, 6, 9))
    assert start <= meal_ts < end


def test_range_bounds_is_inclusive_of_both_ends(costa_rica):
    start, end = timerange.range_bounds(date(2026, 6, 1), date(2026, 6, 7))
    assert start == datetime(2026, 6, 1, 6, tzinfo=timezone.utc)
    assert end == datetime(2026, 6, 8, 6, tzinfo=timezone.utc)  # through end of Jun 7 local


def test_default_utc_preserves_naive_behavior(monkeypatch):
    monkeypatch.setenv("APP_TIMEZONE", "UTC")
    get_settings.cache_clear()
    try:
        start, end = timerange.day_bounds(date(2026, 6, 9))
        assert start == datetime(2026, 6, 9, 0, tzinfo=timezone.utc)
        assert end == datetime(2026, 6, 10, 0, tzinfo=timezone.utc)
    finally:
        get_settings.cache_clear()
