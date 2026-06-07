"""Pydantic request/response models for training (manual logging).

Phase 4 is the basic surface: create a session with optional inline sets, list
and fetch sessions. Catalog resolution (exercise_id) and strength stats come in
Phase 7; the free-text `exercise` label is the source of truth until then.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SessionType = Literal["swim", "gym"]


class TrainingSetIn(BaseModel):
    exercise: str = Field(..., description="Free-text exercise / stroke, e.g. 'bench press', 'freestyle'.")
    set_no: int | None = None
    reps: int | None = None
    weight_kg: float | None = None
    distance_m: float | None = None  # swim
    pace: str | None = None  # swim, e.g. '1:45/100m'
    rpe: float | None = Field(None, ge=0, le=10)
    is_warmup: bool = False
    added_weight_kg: float | None = None  # weighted bodyweight (dips/pull-ups)


class TrainingSessionIn(BaseModel):
    ts: datetime = Field(..., description="Session start (UTC ISO; naive is assumed UTC).")
    type: SessionType
    duration_min: int | None = None
    rpe: float | None = Field(None, ge=0, le=10)
    load: float | None = Field(None, description="Optional; auto-computed as duration_min × rpe when omitted.")
    notes: str | None = None
    sets: list[TrainingSetIn] = []


class TrainingSetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise: str
    set_no: int | None
    reps: int | None
    weight_kg: float | None
    distance_m: float | None
    pace: str | None
    rpe: float | None
    is_warmup: bool
    added_weight_kg: float | None


class TrainingSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ts: datetime
    type: str
    duration_min: int | None
    rpe: float | None
    load: float | None
    notes: str | None
    source: str  # 'manual' | 'samsung_health'
    # watch-import metrics (null for manually logged sessions)
    kcal: float | None
    avg_hr: int | None
    max_hr: int | None
    distance_m: float | None
    sets: list[TrainingSetOut]
