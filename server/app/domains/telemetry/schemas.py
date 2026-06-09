"""Pydantic request/response models for the telemetry read API."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class TelemetryPoint(BaseModel):
    ts: datetime
    metric: str
    value: float
    unit: str | None = None
    source: str


class DailyRollup(BaseModel):
    """One day's rollup for a metric. `sum` is meaningful for additive metrics
    (steps, energy_expenditure); `avg`/`min`/`max` for the rest."""

    day: date
    metric: str
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    sum: float | None = None
    count: int


class SleepSummary(BaseModel):
    model_config = {"from_attributes": True}

    total_min: int | None = None
    deep_min: int | None = None
    rem_min: int | None = None
    light_min: int | None = None
    awake_min: int | None = None
    efficiency: float | None = None


class SleepNight(SleepSummary):
    """A night's sleep summary tagged with the calendar day it ended on (for trends)."""

    day: date


class BodyCompositionPoint(BaseModel):
    """One smart-scale reading (sparse periodic series)."""

    ts: datetime
    weight_kg: float | None = None
    body_fat_pct: float | None = None
    skeletal_muscle_kg: float | None = None
    bmr_kcal: int | None = None
