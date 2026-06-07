"""DB-free tests for training service logic (session load heuristic)."""

from __future__ import annotations

from app.domains.training.service import compute_load


def test_explicit_load_wins():
    assert compute_load(60, 8.0, 999.0) == 999.0


def test_load_derived_from_duration_and_rpe():
    assert compute_load(60, 8.0, None) == 480.0


def test_load_none_when_inputs_missing():
    assert compute_load(None, 8.0, None) is None
    assert compute_load(60, None, None) is None
    assert compute_load(None, None, None) is None
