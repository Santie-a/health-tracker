"""The rule-based recommendation engine (pure functions, no I/O).

Design principle (IMPLEMENTATION_PLAN.md "Objective & data philosophy"): MANUAL
data is primary; every TELEMETRY signal is OPTIONAL. Each rule fires only when its
required inputs exist and is otherwise skipped — so recommendations still run on
manual data alone when the watch hasn't synced.

A rule is ``(DayContext, Thresholds) -> Recommendation | None``. The engine runs
them all, guarding each so one failing rule never aborts the daily pass.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date as date_cls

from .thresholds import DEFAULT, Thresholds

log = logging.getLogger("server.recommendations")


@dataclass
class DayContext:
    """Aggregated metrics for one day. Telemetry-derived fields are Optional."""

    date: date_cls
    # telemetry (complementary, optional)
    sleep_min: int | None = None
    avg_stress: float | None = None
    energy_expenditure: float | None = None  # TDEE
    weight_kg: float | None = None
    # manual (primary)
    did_swim: bool = False
    did_gym: bool = False
    total_training_load: float | None = None
    protein_g: float | None = None
    kcal_in: float | None = None


@dataclass
class Recommendation:
    code: str
    category: str   # recovery | nutrition | training | hydration
    severity: str   # info | warning
    title: str
    detail: str
    signals: list[str] = field(default_factory=list)


def _trained(ctx: DayContext) -> bool:
    return ctx.did_gym or ctx.did_swim or bool(ctx.total_training_load)


def rule_recovery(ctx: DayContext, t: Thresholds) -> Recommendation | None:
    """Low sleep or high stress -> ease today's session. Needs sleep and/or stress."""
    reasons, signals = [], []
    if ctx.sleep_min is not None and ctx.sleep_min < t.low_sleep_min:
        reasons.append(f"slept {ctx.sleep_min / 60:.1f}h (< {t.low_sleep_min / 60:.0f}h)")
        signals.append("sleep")
    if ctx.avg_stress is not None and ctx.avg_stress > t.high_stress:
        reasons.append(f"avg stress {ctx.avg_stress:.0f} (> {t.high_stress:.0f})")
        signals.append("stress")
    if not reasons:
        return None
    return Recommendation(
        code="reduce_intensity",
        category="recovery",
        severity="warning",
        title="Consider an easier session today",
        detail="Recovery looks low: " + "; ".join(reasons) + ". Reduce gym intensity or deload.",
        signals=signals,
    )


def rule_protein(ctx: DayContext, t: Thresholds) -> Recommendation | None:
    """Training day + protein under target -> flag the gap. Needs logged protein."""
    if ctx.protein_g is None or not _trained(ctx):
        return None
    if ctx.weight_kg:
        target = round(ctx.weight_kg * t.protein_g_per_kg)
        basis = f"{t.protein_g_per_kg:g} g/kg × {ctx.weight_kg:.0f} kg"
        signals = ["protein", "weight"]
    else:
        target = round(t.default_protein_g)
        basis = "default target"
        signals = ["protein"]
    if ctx.protein_g >= target:
        return None
    gap = round(target - ctx.protein_g)
    return Recommendation(
        code="protein_gap",
        category="nutrition",
        severity="warning",
        title="Protein gap on a training day",
        detail=f"Logged {ctx.protein_g:.0f} g vs target {target} g ({basis}). Add ~{gap} g.",
        signals=signals,
    )


def rule_calorie_balance(ctx: DayContext, t: Thresholds) -> Recommendation | None:
    """Intake vs expenditure (TDEE) or a fixed goal. Neutral severity — the user's
    cut/bulk intent is unknown, so this just states the balance factually."""
    if ctx.kcal_in is None:
        return None
    if ctx.energy_expenditure is not None:
        reference, ref_label, signals = ctx.energy_expenditure, "expenditure", ["intake", "tdee"]
    elif t.calorie_goal is not None:
        reference, ref_label, signals = t.calorie_goal, "goal", ["intake"]
    else:
        return None
    balance = ctx.kcal_in - reference
    if abs(balance) <= t.calorie_tolerance:
        return Recommendation(
            code="calorie_balanced", category="nutrition", severity="info",
            title="Calories balanced",
            detail=f"Intake {ctx.kcal_in:.0f} kcal ≈ {ref_label} {reference:.0f} kcal.",
            signals=signals,
        )
    if balance > 0:
        return Recommendation(
            code="calorie_surplus", category="nutrition", severity="info",
            title="Calorie surplus",
            detail=f"Intake {ctx.kcal_in:.0f} kcal is {balance:.0f} over {ref_label} ({reference:.0f}).",
            signals=signals,
        )
    return Recommendation(
        code="calorie_deficit", category="nutrition", severity="info",
        title="Calorie deficit",
        detail=f"Intake {ctx.kcal_in:.0f} kcal is {-balance:.0f} under {ref_label} ({reference:.0f}).",
        signals=signals,
    )


def rule_two_a_day(ctx: DayContext, t: Thresholds) -> Recommendation | None:
    """Swim + gym same day -> hydration & carb-timing reminder (pure manual)."""
    if not (ctx.did_swim and ctx.did_gym):
        return None
    return Recommendation(
        code="two_a_day",
        category="hydration",
        severity="info",
        title="Two-a-day: fuel and hydrate",
        detail="Swim and gym today — prioritize hydration and time carbs around both sessions.",
        signals=["training"],
    )


RULES = [rule_recovery, rule_protein, rule_calorie_balance, rule_two_a_day]


def generate(ctx: DayContext, thresholds: Thresholds = DEFAULT) -> list[Recommendation]:
    """Run every rule, guarding each so one failure never aborts the pass."""
    out: list[Recommendation] = []
    for rule in RULES:
        try:
            rec = rule(ctx, thresholds)
        except Exception:
            log.exception("Recommendation rule %s failed for %s", rule.__name__, ctx.date)
            continue
        if rec is not None:
            out.append(rec)
    return out
