"""DB-free tests for training catalog helpers (slug, name resolution, week start)."""

from __future__ import annotations

from datetime import date

from app.domains.training.seed import SEED, _slug
from app.domains.training.service import _monday, _name_index, slugify


def test_slugify():
    assert slugify("Bench Press") == "bench_press"
    assert slugify("Pull-up") == "pull_up"
    assert slugify("Romanian Deadlift") == "romanian_deadlift"


def test_seed_slug_matches_service_slugify():
    # the seed loader and the create endpoint must agree on slugs
    for name, *_ in SEED:
        assert _slug(name) == slugify(name)


def test_monday_is_week_start():
    assert _monday(date(2026, 6, 5)) == date(2026, 6, 1)   # Fri -> Mon
    assert _monday(date(2026, 6, 1)) == date(2026, 6, 1)   # Mon -> Mon
    assert _monday(date(2026, 6, 7)) == date(2026, 6, 1)   # Sun -> Mon


class _FakeMuscle:
    def __init__(self, name, role):
        self.muscle, self.role = name, role


class _FakeExercise:
    def __init__(self, name, aliases):
        self.name, self.aliases = name, aliases
        self.muscles = []


def test_name_index_includes_aliases_and_normalizes():
    ex = _FakeExercise("Bench Press", ["flat bench", "BENCH"])
    idx = _name_index([ex])
    assert idx["bench press"] is ex
    assert idx["flat bench"] is ex
    assert idx["bench"] is ex  # alias normalized to lowercase
