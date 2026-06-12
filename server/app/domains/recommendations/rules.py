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
    # weekly training balance (from strength stats; manual)
    push_pull_ratio: float | None = None
    upper_lower_ratio: float | None = None
    # active goals (optional): the user's intent, so advice can be directional.
    # Body goal — drives calorie/protein direction and progress nudges.
    goal_type: str | None = None                 # gain_muscle | gain_weight | lose_fat | recomp | maintain
    goal_calorie_delta: int | None = None        # desired surplus(+)/deficit(-) kcal vs TDEE
    goal_protein_g_per_kg: float | None = None   # protein target override (e.g. 2.0 on a cut)
    goal_metric: str | None = None
    goal_target_rate_per_week: float | None = None
    goal_actual_rate_per_week: float | None = None
    goal_progress_status: str | None = None      # on_track | behind | ahead | too_fast | stalled | achieved | no_data
    # Sleep goal — nightly target the recovery advice can hold the user to.
    sleep_goal_target_min: float | None = None


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
    # A goal's protein target (e.g. 2.0 g/kg to hold muscle on a cut) overrides the default.
    per_kg = ctx.goal_protein_g_per_kg or t.protein_g_per_kg
    if ctx.weight_kg:
        target = round(ctx.weight_kg * per_kg)
        basis = f"{per_kg:g} g/kg × {ctx.weight_kg:.0f} kg"
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


def _calorie_balance_neutral(
    ctx: DayContext, t: Thresholds, reference: float, ref_label: str, signals: list[str]
) -> Recommendation:
    """The original goal-agnostic balance: states surplus/deficit factually."""
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


def rule_calorie_balance(ctx: DayContext, t: Thresholds) -> Recommendation | None:
    """Intake vs the energy target. With an active body goal this is DIRECTIONAL —
    it judges whether intake supports the surplus/deficit the goal calls for. Without
    a goal it falls back to the neutral, descriptive balance."""
    if ctx.kcal_in is None:
        return None
    if ctx.energy_expenditure is not None:
        base, base_label, signals = ctx.energy_expenditure, "TDEE", ["intake", "tdee"]
    elif t.calorie_goal is not None:
        base, base_label, signals = t.calorie_goal, "goal", ["intake"]
    else:
        return None

    delta = ctx.goal_calorie_delta
    if delta is None:  # no goal intent → original neutral statement
        return _calorie_balance_neutral(ctx, t, base, base_label, signals)

    signals = signals + ["goal"]
    target = base + delta if base_label == "TDEE" else base
    aim = (
        f"target {target:.0f} kcal ({base_label} {base:.0f} {delta:+d})"
        if base_label == "TDEE"
        else f"target {target:.0f} kcal"
    )
    gap = ctx.kcal_in - target  # >0 over the target intake, <0 under it

    if abs(gap) <= t.calorie_tolerance:
        return Recommendation(
            code="calorie_on_goal", category="nutrition", severity="info",
            title="Intake matches your goal",
            detail=f"Intake {ctx.kcal_in:.0f} kcal ≈ {aim}.",
            signals=signals,
        )
    # The miss only matters when it works against the goal's direction.
    if delta > 0 and gap < 0:
        return Recommendation(
            code="calorie_under_surplus", category="nutrition", severity="warning",
            title="Under your surplus target",
            detail=(
                f"Intake {ctx.kcal_in:.0f} kcal is {-gap:.0f} under {aim}. "
                f"You won't gain at this intake — add ~{-gap:.0f} kcal."
            ),
            signals=signals,
        )
    if delta < 0 and gap > 0:
        return Recommendation(
            code="calorie_over_deficit", category="nutrition", severity="warning",
            title="Over your deficit target",
            detail=(
                f"Intake {ctx.kcal_in:.0f} kcal is {gap:.0f} over {aim}. "
                f"Trim ~{gap:.0f} kcal to keep losing."
            ),
            signals=signals,
        )
    if delta == 0:
        direction = "over" if gap > 0 else "under"
        return Recommendation(
            code="calorie_maintenance_drift", category="nutrition", severity="info",
            title="Drifting from maintenance",
            detail=f"Intake {ctx.kcal_in:.0f} kcal is {abs(gap):.0f} {direction} {aim}.",
            signals=signals,
        )
    # Miss is in the helpful direction (extra surplus on a bulk / deeper cut) — affirm.
    return Recommendation(
        code="calorie_supports_goal", category="nutrition", severity="info",
        title="Intake supports your goal",
        detail=f"Intake {ctx.kcal_in:.0f} kcal vs {aim} — direction matches your {ctx.goal_type or 'goal'}.",
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


def rule_training_balance(ctx: DayContext, t: Thresholds) -> Recommendation | None:
    """This week's push:pull / upper:lower skew (from logged sets). Pure manual."""
    flags: list[str] = []
    if ctx.push_pull_ratio is not None:
        if ctx.push_pull_ratio > t.imbalance_high:
            flags.append(f"push:pull {ctx.push_pull_ratio:g} (push-heavy — add pulling)")
        elif ctx.push_pull_ratio < t.imbalance_low:
            flags.append(f"push:pull {ctx.push_pull_ratio:g} (pull-heavy — add pressing)")
    if ctx.upper_lower_ratio is not None:
        if ctx.upper_lower_ratio > t.imbalance_high:
            flags.append(f"upper:lower {ctx.upper_lower_ratio:g} (upper-heavy — add legs)")
        elif ctx.upper_lower_ratio < t.imbalance_low:
            flags.append(f"upper:lower {ctx.upper_lower_ratio:g} (lower-heavy — add upper)")
    if not flags:
        return None
    return Recommendation(
        code="training_imbalance",
        category="training",
        severity="info",
        title="Training balance (this week)",
        detail="; ".join(flags) + ".",
        signals=["training"],
    )


def _gaining(ctx: DayContext) -> bool:
    """True when the body goal intends to add weight/muscle (vs lose)."""
    if ctx.goal_target_rate_per_week is not None:
        return ctx.goal_target_rate_per_week > 0
    return ctx.goal_type in ("gain_muscle", "gain_weight")


def rule_goal_progress(ctx: DayContext, t: Thresholds) -> Recommendation | None:
    """Compare the fitted body-metric trend against the goal's target rate and nudge:
    stalled -> push harder, too_fast -> ease off, achieved -> celebrate. Needs a
    computed progress status (set only when an active body goal + readings exist)."""
    status = ctx.goal_progress_status
    if status is None or ctx.goal_type is None:
        return None

    rate = ctx.goal_actual_rate_per_week
    tgt = ctx.goal_target_rate_per_week
    unit = "kg" if (ctx.goal_metric or "").endswith("_kg") else ""
    rate_txt = f"{rate:+.2f} {unit}/wk".strip() if rate is not None else "no clear trend"
    tgt_txt = f"{tgt:+.2f} {unit}/wk".strip() if tgt is not None else "target"
    gaining = _gaining(ctx)

    if status == "achieved":
        return Recommendation(
            code="goal_achieved", category="nutrition", severity="info",
            title="Goal reached",
            detail="You've hit this goal's target — set the next one to keep progressing.",
            signals=["goal"],
        )
    if status == "stalled":
        nudge = (
            f"add ~{t.progress_kcal_bump} kcal/day to restart the gain"
            if gaining
            else f"tighten the deficit ~{t.progress_kcal_bump} kcal/day or add steps"
        )
        return Recommendation(
            code="goal_stalled", category="nutrition", severity="warning",
            title="Progress has stalled",
            detail=f"{ctx.goal_metric or 'metric'} is flat ({rate_txt}) vs {tgt_txt}. Try to {nudge}.",
            signals=["goal", "weight"],
        )
    if status == "too_fast":
        ease = (
            "trim the surplus to limit fat gain"
            if gaining
            else "ease the deficit to protect muscle"
        )
        return Recommendation(
            code="goal_too_fast", category="nutrition", severity="warning",
            title="Moving faster than target",
            detail=f"Trending {rate_txt} vs {tgt_txt}. Consider easing off — {ease}.",
            signals=["goal", "weight"],
        )
    if status == "behind":
        return Recommendation(
            code="goal_behind", category="nutrition", severity="info",
            title="Behind your target pace",
            detail=f"Trending {rate_txt} vs {tgt_txt}. On track to be late unless intake/effort rises.",
            signals=["goal", "weight"],
        )
    return None


def rule_sleep_goal(ctx: DayContext, t: Thresholds) -> Recommendation | None:
    """Hold the user to an explicit sleep goal (e.g. 7.5 h), catching the 6–7.5 h band
    the deload rule (< 6 h) ignores. Needs an active sleep goal + last night's sleep."""
    if ctx.sleep_goal_target_min is None or ctx.sleep_min is None:
        return None
    shortfall = ctx.sleep_goal_target_min - ctx.sleep_min
    if shortfall <= t.sleep_goal_tolerance_min:
        return None
    return Recommendation(
        code="sleep_below_goal",
        category="recovery",
        severity="warning",
        title="Short of your sleep goal",
        detail=(
            f"Slept {ctx.sleep_min / 60:.1f}h vs your {ctx.sleep_goal_target_min / 60:.1f}h goal "
            f"({shortfall:.0f} min short). Protect tonight's sleep window."
        ),
        signals=["sleep", "goal"],
    )


RULES = [
    rule_recovery,
    rule_sleep_goal,
    rule_protein,
    rule_calorie_balance,
    rule_goal_progress,
    rule_two_a_day,
    rule_training_balance,
]


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
