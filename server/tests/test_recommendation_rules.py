"""Table-driven tests for the recommendation engine (pure, no DB).

Verifies the manual-primary / telemetry-optional contract: rules fire on manual
data alone, and missing telemetry signals are skipped (not errors)."""

from __future__ import annotations

from datetime import date

import pytest

from app.domains.recommendations.rules import (
    DayContext,
    generate,
    rule_calorie_balance,
    rule_protein,
    rule_recovery,
    rule_training_balance,
    rule_two_a_day,
)
from app.domains.recommendations.thresholds import DEFAULT, Thresholds

DAY = date(2026, 6, 5)


def ctx(**kw) -> DayContext:
    return DayContext(date=DAY, **kw)


# --- recovery -----------------------------------------------------------------

def test_recovery_fires_on_low_sleep():
    rec = rule_recovery(ctx(sleep_min=300), DEFAULT)
    assert rec and rec.code == "reduce_intensity" and "sleep" in rec.signals


def test_recovery_fires_on_high_stress():
    rec = rule_recovery(ctx(avg_stress=85), DEFAULT)
    assert rec and "stress" in rec.signals


def test_recovery_skipped_when_no_telemetry():
    # no sleep, no stress -> rule simply doesn't fire (telemetry optional)
    assert rule_recovery(ctx(), DEFAULT) is None


def test_recovery_quiet_when_well_rested():
    assert rule_recovery(ctx(sleep_min=480, avg_stress=30), DEFAULT) is None


# --- protein ------------------------------------------------------------------

def test_protein_gap_uses_bodyweight_when_present():
    rec = rule_protein(ctx(did_gym=True, protein_g=90, weight_kg=80), DEFAULT)
    assert rec and rec.code == "protein_gap"
    assert "weight" in rec.signals  # target = 1.6 * 80 = 128 > 90


def test_protein_uses_default_target_without_weight():
    rec = rule_protein(ctx(did_gym=True, protein_g=90), DEFAULT)  # default 120 > 90
    assert rec and rec.code == "protein_gap" and "weight" not in rec.signals


def test_protein_quiet_when_target_met():
    assert rule_protein(ctx(did_gym=True, protein_g=200, weight_kg=80), DEFAULT) is None


def test_protein_skipped_on_rest_day():
    assert rule_protein(ctx(protein_g=50), DEFAULT) is None


def test_protein_skipped_without_logged_protein():
    assert rule_protein(ctx(did_gym=True), DEFAULT) is None


# --- calorie balance ----------------------------------------------------------

def test_calorie_uses_tdee_when_present():
    rec = rule_calorie_balance(ctx(kcal_in=2600, energy_expenditure=2000), DEFAULT)
    assert rec and rec.code == "calorie_surplus" and "tdee" in rec.signals


def test_calorie_deficit():
    rec = rule_calorie_balance(ctx(kcal_in=1500, energy_expenditure=2200), DEFAULT)
    assert rec and rec.code == "calorie_deficit"


def test_calorie_balanced_within_tolerance():
    rec = rule_calorie_balance(ctx(kcal_in=2050, energy_expenditure=2000), DEFAULT)
    assert rec and rec.code == "calorie_balanced"


def test_calorie_falls_back_to_goal_without_tdee():
    t = Thresholds(calorie_goal=2000.0)
    rec = rule_calorie_balance(ctx(kcal_in=2600), t)
    assert rec and rec.code == "calorie_surplus"


def test_calorie_skipped_without_intake_or_reference():
    assert rule_calorie_balance(ctx(energy_expenditure=2000), DEFAULT) is None  # no intake
    assert rule_calorie_balance(ctx(kcal_in=2000), DEFAULT) is None  # no tdee, no goal


# --- two-a-day ----------------------------------------------------------------

def test_two_a_day_fires_only_when_both():
    assert rule_two_a_day(ctx(did_swim=True, did_gym=True), DEFAULT).code == "two_a_day"
    assert rule_two_a_day(ctx(did_gym=True), DEFAULT) is None


# --- training balance ---------------------------------------------------------

def test_balance_flags_push_heavy():
    rec = rule_training_balance(ctx(push_pull_ratio=3.0), DEFAULT)
    assert rec and rec.code == "training_imbalance" and "push-heavy" in rec.detail


def test_balance_flags_lower_heavy():
    rec = rule_training_balance(ctx(upper_lower_ratio=0.3), DEFAULT)
    assert rec and "lower-heavy" in rec.detail


def test_balance_quiet_when_proportionate():
    assert rule_training_balance(ctx(push_pull_ratio=1.1, upper_lower_ratio=1.0), DEFAULT) is None


def test_balance_skipped_without_training():
    assert rule_training_balance(ctx(), DEFAULT) is None


# --- engine -------------------------------------------------------------------

def test_engine_runs_on_manual_data_alone():
    # no telemetry at all — still produces manual-driven recommendations
    recs = generate(ctx(did_swim=True, did_gym=True, protein_g=80, weight_kg=80))
    codes = {r.code for r in recs}
    assert "two_a_day" in codes
    assert "protein_gap" in codes
    # recovery + calorie rules need telemetry -> absent
    assert "reduce_intensity" not in codes


def test_engine_empty_context_yields_nothing():
    assert generate(ctx()) == []


def test_engine_full_context():
    recs = generate(ctx(sleep_min=300, avg_stress=80, did_gym=True, did_swim=True,
                        protein_g=90, weight_kg=80, kcal_in=2600, energy_expenditure=2000))
    codes = {r.code for r in recs}
    assert codes == {"reduce_intensity", "protein_gap", "calorie_surplus", "two_a_day"}
