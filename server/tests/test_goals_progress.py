"""Tests for goal progress math (pure) and the goal-aware recommendation rules."""

from __future__ import annotations

from datetime import date, timedelta

from app.domains.goals.progress import Reading, compute
from app.domains.recommendations.rules import (
    DayContext,
    rule_calorie_balance,
    rule_goal_progress,
    rule_protein,
    rule_sleep_goal,
)
from app.domains.recommendations.thresholds import DEFAULT

START = date(2026, 5, 1)


def _series(start: date, values: list[float], step_days: int = 2) -> list[Reading]:
    return [Reading(day=start + timedelta(days=i * step_days), value=v) for i, v in enumerate(values)]


# --- progress math ------------------------------------------------------------

def test_no_data_when_too_few_readings():
    p = compute([], metric="weight_kg", baseline_value=80, target_value=85,
                target_rate_per_week=0.25, start_date=START, today=START + timedelta(days=14))
    assert p.status == "no_data" and p.n_readings == 0


def test_on_track_matches_target_rate():
    # +0.5 kg over 14 days = exactly +0.25 kg/wk, the target rate.
    readings = [
        Reading(day=START, value=80.0),
        Reading(day=START + timedelta(days=7), value=80.25),
        Reading(day=START + timedelta(days=14), value=80.5),
    ]
    p = compute(readings, metric="weight_kg", baseline_value=80.0, target_value=85.0,
                target_rate_per_week=0.25, start_date=START, today=START + timedelta(days=14))
    assert p.status == "on_track"
    assert p.actual_rate_per_week == 0.25


def test_stalled_when_flat_on_gain_goal():
    p = compute(_series(START, [80.0, 80.0, 80.01, 79.99]),
                metric="weight_kg", baseline_value=80.0, target_value=85.0,
                target_rate_per_week=0.25, start_date=START, today=START + timedelta(days=6))
    assert p.status == "stalled"


def test_too_fast_when_gaining_double_target():
    p = compute(_series(START, [80.0, 80.35, 80.7, 81.05]),
                metric="weight_kg", baseline_value=80.0, target_value=85.0,
                target_rate_per_week=0.25, start_date=START, today=START + timedelta(days=6))
    assert p.status == "too_fast"


def test_achieved_when_target_reached():
    p = compute(_series(START, [80.0, 82.0, 84.0, 85.5]),
                metric="weight_kg", baseline_value=80.0, target_value=85.0,
                target_rate_per_week=0.25, start_date=START, today=START + timedelta(days=6))
    assert p.status == "achieved"
    assert p.pct_complete == 1.0  # clamped


def test_projection_extrapolates_to_target():
    p = compute(_series(START, [80.0, 80.5, 81.0, 81.5]),
                metric="weight_kg", baseline_value=80.0, target_value=83.0,
                target_rate_per_week=1.0, start_date=START, today=START + timedelta(days=6))
    assert p.projected_date is not None and p.projected_date > START


# --- goal-aware rules ---------------------------------------------------------

def _ctx(**kw) -> DayContext:
    return DayContext(date=date(2026, 6, 5), **kw)


def test_calorie_rule_neutral_without_goal():
    rec = rule_calorie_balance(_ctx(kcal_in=2600, energy_expenditure=2500), DEFAULT)
    assert rec and rec.code == "calorie_balanced"  # within tolerance, descriptive


def test_calorie_rule_warns_when_under_surplus_target():
    rec = rule_calorie_balance(
        _ctx(kcal_in=2400, energy_expenditure=2500, goal_calorie_delta=250, goal_type="gain_muscle"),
        DEFAULT,
    )
    assert rec and rec.code == "calorie_under_surplus" and rec.severity == "warning"


def test_calorie_rule_affirms_when_surplus_met():
    rec = rule_calorie_balance(
        _ctx(kcal_in=2780, energy_expenditure=2500, goal_calorie_delta=250, goal_type="gain_muscle"),
        DEFAULT,
    )
    assert rec and rec.code == "calorie_on_goal"


def test_protein_uses_goal_override():
    # 2.0 g/kg × 80 = 160 target; logged 130 on a training day → gap flagged.
    rec = rule_protein(
        _ctx(protein_g=130, weight_kg=80, did_gym=True, goal_protein_g_per_kg=2.0), DEFAULT
    )
    assert rec and "2 g/kg" in rec.detail


def test_goal_progress_rule_nudges_on_stall():
    rec = rule_goal_progress(
        _ctx(goal_type="gain_muscle", goal_progress_status="stalled",
             goal_target_rate_per_week=0.25, goal_actual_rate_per_week=0.0, goal_metric="weight_kg"),
        DEFAULT,
    )
    assert rec and rec.code == "goal_stalled" and "kcal/day" in rec.detail


def test_sleep_goal_rule_flags_shortfall():
    rec = rule_sleep_goal(_ctx(sleep_min=390, sleep_goal_target_min=450), DEFAULT)
    assert rec and rec.code == "sleep_below_goal"


def test_sleep_goal_rule_quiet_when_met():
    assert rule_sleep_goal(_ctx(sleep_min=445, sleep_goal_target_min=450), DEFAULT) is None
