"""Pydantic request/response models for the goals API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

GoalType = Literal["gain_muscle", "gain_weight", "lose_fat", "recomp", "maintain", "improve_sleep"]
GoalStatus = Literal["active", "achieved", "abandoned"]
GoalMetric = Literal["weight_kg", "skeletal_muscle_kg", "body_fat_pct", "sleep_min", "sleep_efficiency"]
ProgressStatus = Literal[
    "on_track", "behind", "ahead", "too_fast", "stalled", "achieved", "no_target", "no_data"
]


class GoalIn(BaseModel):
    """Create a goal. Most fields are optional — only `type` is required; the
    service fills sensible defaults (category, metric, baseline, nutrition knobs)
    from the type and current body composition."""

    type: GoalType
    metric: GoalMetric | None = None
    baseline_value: float | None = None
    target_value: float | None = None
    target_rate_per_week: float | None = None
    target_date: date | None = None
    calorie_delta: int | None = Field(None, description="Surplus(+)/deficit(-) kcal vs TDEE to aim for.")
    protein_g_per_kg: float | None = Field(None, ge=0, le=4)
    notes: str | None = None


class GoalUpdate(BaseModel):
    """Patch an existing goal. `status` flips a goal to achieved/abandoned."""

    status: GoalStatus | None = None
    metric: GoalMetric | None = None
    baseline_value: float | None = None
    target_value: float | None = None
    target_rate_per_week: float | None = None
    target_date: date | None = None
    calorie_delta: int | None = None
    protein_g_per_kg: float | None = Field(None, ge=0, le=4)
    notes: str | None = None


class GoalOut(BaseModel):
    id: int
    type: GoalType
    category: Literal["body", "sleep"]
    status: GoalStatus
    metric: GoalMetric | None = None
    baseline_value: float | None = None
    target_value: float | None = None
    target_rate_per_week: float | None = None
    start_date: date
    target_date: date | None = None
    calorie_delta: int | None = None
    protein_g_per_kg: float | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GoalProgressOut(BaseModel):
    """Computed progress for a goal: the fitted trend over its metric vs target."""

    status: ProgressStatus
    metric: GoalMetric | None = None
    baseline_value: float | None = None
    current_value: float | None = None
    target_value: float | None = None
    actual_rate_per_week: float | None = None
    target_rate_per_week: float | None = None
    pct_complete: float | None = Field(None, description="0..1 along baseline→target, when both known.")
    projected_date: date | None = Field(None, description="Date the current trend reaches the target.")
    days_elapsed: int = 0
    n_readings: int = 0
    summary: str = ""


class GoalWithProgressOut(GoalOut):
    progress: GoalProgressOut
