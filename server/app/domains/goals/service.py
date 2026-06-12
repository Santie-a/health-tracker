"""Goals business logic: derive sensible defaults from the goal type, enforce one
active goal per category, and compute progress from the metric series.

Design: the goal records *intent*; the recommendation engine reads it (via
`load_active` / `progress_for`) to turn descriptive signals into directional
advice. Defaults here encode conservative, evidence-based starting points (e.g. a
lean-bulk surplus ~+250 kcal at ~2.0 g/kg protein) that the user can override.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timerange import app_tz

from . import progress, repository
from .models import Goal
from .schemas import GoalIn, GoalOut, GoalProgressOut, GoalUpdate, GoalWithProgressOut


class DuplicateActiveGoal(Exception):
    """Raised when a second active goal is created/activated in a category."""

    def __init__(self, category: str):
        self.category = category
        super().__init__(category)


@dataclass(frozen=True)
class _Defaults:
    category: str
    metric: str
    calorie_delta: int | None
    protein_g_per_kg: float | None
    target_rate_per_week: float | None
    target_value: float | None = None


# Conservative defaults per goal type. Only fill fields the caller left None.
_DEFAULTS: dict[str, _Defaults] = {
    "gain_muscle": _Defaults("body", "weight_kg", 250, 2.0, 0.25),   # lean bulk
    "gain_weight": _Defaults("body", "weight_kg", 400, 1.8, 0.35),
    "lose_fat":    _Defaults("body", "weight_kg", -400, 2.0, -0.45),
    "recomp":      _Defaults("body", "weight_kg", 0, 2.0, 0.0),
    "maintain":    _Defaults("body", "weight_kg", 0, 1.6, 0.0),
    "improve_sleep": _Defaults("sleep", "sleep_min", None, None, None, target_value=450.0),  # 7.5 h
}


def _local_today():
    return datetime.now(app_tz()).date()


def category_for(goal_type: str) -> str:
    return _DEFAULTS[goal_type].category


async def create_goal(session: AsyncSession, payload: GoalIn) -> GoalOut:
    d = _DEFAULTS[payload.type]

    # One active goal per category — surface a clean 409 rather than letting the
    # partial unique index raise an opaque IntegrityError.
    if await repository.get_active(session, d.category) is not None:
        raise DuplicateActiveGoal(d.category)

    metric = payload.metric or d.metric
    baseline = payload.baseline_value
    if baseline is None and d.category == "body":
        baseline = await repository.latest_body_value(session, metric)

    goal = Goal(
        type=payload.type,
        category=d.category,
        status="active",
        metric=metric,
        baseline_value=baseline,
        target_value=payload.target_value if payload.target_value is not None else d.target_value,
        target_rate_per_week=(
            payload.target_rate_per_week
            if payload.target_rate_per_week is not None
            else d.target_rate_per_week
        ),
        target_date=payload.target_date,
        calorie_delta=payload.calorie_delta if payload.calorie_delta is not None else d.calorie_delta,
        protein_g_per_kg=(
            payload.protein_g_per_kg
            if payload.protein_g_per_kg is not None
            else d.protein_g_per_kg
        ),
        notes=payload.notes,
        start_date=_local_today(),
    )
    await repository.add(session, goal)
    return GoalOut.model_validate(goal)


async def list_goals(session: AsyncSession, status: str | None, limit: int) -> list[GoalOut]:
    rows = await repository.list_all(session, status, limit)
    return [GoalOut.model_validate(r) for r in rows]


async def update_goal(
    session: AsyncSession, goal_id: int, payload: GoalUpdate
) -> GoalOut | None:
    goal = await repository.get(session, goal_id)
    if goal is None:
        return None
    data = payload.model_dump(exclude_unset=True)

    # Re-activating a goal must respect the one-active-per-category rule.
    if data.get("status") == "active" and goal.status != "active":
        other = await repository.get_active(session, goal.category)
        if other is not None and other.id != goal.id:
            raise DuplicateActiveGoal(goal.category)

    for field, value in data.items():
        setattr(goal, field, value)
    await session.flush()
    return GoalOut.model_validate(goal)


async def delete_goal(session: AsyncSession, goal_id: int) -> bool:
    goal = await repository.get(session, goal_id)
    if goal is None:
        return False
    await repository.delete(session, goal)
    return True


async def progress_for(session: AsyncSession, goal: Goal) -> GoalProgressOut:
    """Fit the goal's metric series from its start date to today and classify it."""
    if goal.metric is None:
        return GoalProgressOut(status="no_target", summary="No metric set for this goal.")
    today = _local_today()
    readings = await repository.metric_series(session, goal.metric, goal.start_date, today)
    return progress.compute(
        readings,
        metric=goal.metric,
        baseline_value=float(goal.baseline_value) if goal.baseline_value is not None else None,
        target_value=float(goal.target_value) if goal.target_value is not None else None,
        target_rate_per_week=(
            float(goal.target_rate_per_week) if goal.target_rate_per_week is not None else None
        ),
        start_date=goal.start_date,
        today=today,
    )


async def get_goal_with_progress(
    session: AsyncSession, goal_id: int
) -> GoalWithProgressOut | None:
    goal = await repository.get(session, goal_id)
    if goal is None:
        return None
    prog = await progress_for(session, goal)
    return GoalWithProgressOut(**GoalOut.model_validate(goal).model_dump(), progress=prog)


async def list_active_with_progress(session: AsyncSession) -> list[GoalWithProgressOut]:
    goals = await repository.list_active(session)
    out: list[GoalWithProgressOut] = []
    for g in goals:
        prog = await progress_for(session, g)
        out.append(GoalWithProgressOut(**GoalOut.model_validate(g).model_dump(), progress=prog))
    return out


# --- consumed by the recommendation engine -----------------------------------

async def load_active(session: AsyncSession) -> dict[str, Goal]:
    """Active goals keyed by category ('body' / 'sleep') for the recommendations pass."""
    return {g.category: g for g in await repository.list_active(session)}
