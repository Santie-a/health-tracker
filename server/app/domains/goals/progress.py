"""Goal progress math — pure functions, no I/O.

Fits a least-squares line to a metric's readings (weight, muscle, sleep) to get an
actual weekly rate of change, then classifies it against the goal's target rate or
target value: on_track / behind / ahead / too_fast / stalled / achieved. Kept
separate from the service so it's unit-testable without a database, mirroring the
recommendations engine split (rules.py vs service.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .schemas import GoalProgressOut

# Below this fraction of the target rate, the trend is "flat" for practical purposes.
_STALL_FRACTION = 0.15
# A trend faster than this multiple of target is "too_fast" (fat-gain risk on a bulk).
_TOO_FAST_RATIO = 1.75
_AHEAD_RATIO = 1.3
_ON_TRACK_LOW = 0.7


@dataclass(frozen=True)
class Reading:
    day: date
    value: float


def _linear_fit(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    """Ordinary least squares -> (slope_per_unit_x, intercept). None if x has no spread."""
    n = len(points)
    if n < 2:
        return None
    sx = sum(x for x, _ in points)
    sy = sum(y for _, y in points)
    sxx = sum(x * x for x, _ in points)
    sxy = sum(x * y for x, y in points)
    denom = n * sxx - sx * sx
    if denom == 0:  # all readings on the same day
        return None
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    return slope, intercept


def _classify(
    actual_rate: float,
    target_rate: float | None,
    baseline: float | None,
    target: float | None,
    current: float | None,
) -> str:
    # Reached the target value (in the desired direction)?
    if target is not None and baseline is not None and current is not None and target != baseline:
        desired_dir = 1.0 if target > baseline else -1.0
        if (current - target) * desired_dir >= 0:
            return "achieved"

    if target_rate is not None and target_rate != 0:
        # Stalled: barely moving relative to the intended pace.
        if abs(actual_rate) < _STALL_FRACTION * abs(target_rate):
            return "stalled"
        ratio = actual_rate / target_rate  # negative => moving the wrong way
        if ratio < _ON_TRACK_LOW:
            return "behind"
        if ratio <= _AHEAD_RATIO:
            return "on_track"
        if ratio <= _TOO_FAST_RATIO:
            return "ahead"
        return "too_fast"

    # No rate target — judge by direction toward the target value, if any.
    if target is not None and baseline is not None and target != baseline:
        desired_dir = 1.0 if target > baseline else -1.0
        if abs(actual_rate) < 1e-6:
            return "stalled"
        return "on_track" if (actual_rate * desired_dir) > 0 else "behind"

    return "no_target"


def _project(
    last_day: date, current: float | None, target: float | None, slope_per_day: float
) -> date | None:
    """Date the current trend crosses the target value, or None if it never will."""
    if current is None or target is None or abs(slope_per_day) < 1e-9:
        return None
    days = (target - current) / slope_per_day
    if days <= 0:  # already past it, or trending away
        return None
    if days > 3650:  # >10y out: effectively "not on this trajectory"
        return None
    return last_day + timedelta(days=round(days))


def _summarize(status: str, metric: str | None, actual_rate: float | None) -> str:
    unit = {"weight_kg": "kg", "skeletal_muscle_kg": "kg", "body_fat_pct": "%",
            "sleep_min": "min", "sleep_efficiency": "%"}.get(metric or "", "")
    rate = f"{actual_rate:+.2f} {unit}/wk" if actual_rate is not None else "no trend yet"
    return {
        "on_track": f"On track ({rate}).",
        "behind": f"Behind pace ({rate}).",
        "ahead": f"Ahead of pace ({rate}).",
        "too_fast": f"Faster than target ({rate}) — risk of unwanted gain/loss.",
        "stalled": f"Stalled ({rate}).",
        "achieved": "Target reached.",
        "no_target": f"Trending {rate}; no numeric target set.",
        "no_data": "Not enough readings to show a trend yet.",
    }.get(status, rate)


def compute(
    readings: list[Reading],
    *,
    metric: str | None,
    baseline_value: float | None,
    target_value: float | None,
    target_rate_per_week: float | None,
    start_date: date,
    today: date,
) -> GoalProgressOut:
    """Fit the readings and classify progress. Telemetry is optional everywhere, so
    sparse/empty series degrade to a 'no_data' result rather than raising."""
    days_elapsed = max((today - start_date).days, 0)
    pts = sorted(readings, key=lambda r: r.day)
    n = len(pts)

    if n == 0:
        return GoalProgressOut(
            status="no_data", metric=metric, baseline_value=baseline_value,
            target_value=target_value, target_rate_per_week=target_rate_per_week,
            days_elapsed=days_elapsed, n_readings=0, summary=_summarize("no_data", metric, None),
        )

    current = pts[-1].value
    base = baseline_value if baseline_value is not None else pts[0].value
    last_day = pts[-1].day

    # Fit on (days-since-first-reading, value) so x is in days.
    origin = pts[0].day
    fit = _linear_fit([((p.day - origin).days, p.value) for p in pts])
    actual_rate = round(fit[0] * 7, 3) if fit else None

    if actual_rate is None:
        status = "no_data"
    else:
        status = _classify(actual_rate, target_rate_per_week, base, target_value, current)

    pct = None
    if target_value is not None and base is not None and target_value != base:
        pct = (current - base) / (target_value - base)
        pct = max(0.0, min(1.0, pct))

    projected = (
        _project(last_day, current, target_value, fit[0]) if fit else None
    )

    return GoalProgressOut(
        status=status,
        metric=metric,
        baseline_value=round(base, 2) if base is not None else None,
        current_value=round(current, 2),
        target_value=target_value,
        actual_rate_per_week=actual_rate,
        target_rate_per_week=target_rate_per_week,
        pct_complete=round(pct, 3) if pct is not None else None,
        projected_date=projected,
        days_elapsed=days_elapsed,
        n_readings=n,
        summary=_summarize(status, metric, actual_rate),
    )
