"""Pydantic request/response models for training (manual logging).

Phase 4 is the basic surface: create a session with optional inline sets, list
and fetch sessions. Catalog resolution (exercise_id) and strength stats come in
Phase 7; the free-text `exercise` label is the source of truth until then.
"""

from __future__ import annotations

from datetime import date, datetime
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


class AddSetsIn(BaseModel):
    sets: list[TrainingSetIn] = Field(..., min_length=1)


# --- exercise catalog ---------------------------------------------------------

ExerciseCategory = Literal["push", "pull", "squat", "hinge", "carry", "core", "swim", "other"]
MuscleRole = Literal["primary", "secondary"]


class ExerciseMuscleIn(BaseModel):
    muscle: str
    role: MuscleRole = "primary"


class ExerciseMuscleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    muscle: str
    role: str


class ExerciseIn(BaseModel):
    name: str
    category: ExerciseCategory | None = None
    primary_muscle: str | None = None
    equipment: str | None = None
    is_unilateral: bool = False
    is_bodyweight: bool = False
    aliases: list[str] | None = None
    muscles: list[ExerciseMuscleIn] = []


class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    category: str | None
    primary_muscle: str | None
    equipment: str | None
    is_unilateral: bool
    is_bodyweight: bool
    aliases: list[str] | None
    is_active: bool
    muscles: list[ExerciseMuscleOut]


# --- strength stats -----------------------------------------------------------

class WeeklyMuscleSets(BaseModel):
    week: date  # Monday of the ISO week (UTC)
    muscle: str
    sets: float  # credited working sets (primary 1.0 + secondary 0.5)


class MuscleVolume(BaseModel):
    muscle: str
    volume_load: float  # Σ reps × weight, credited


class ExerciseStat(BaseModel):
    exercise: str            # catalog name or as-logged label
    slug: str | None
    sets: int
    top_weight_kg: float | None
    best_e1rm: float | None  # Epley estimated 1RM
    best_e1rm_date: date | None


class TrainingStats(BaseModel):
    from_: date = Field(alias="from")
    to: date
    weekly_sets_per_muscle: list[WeeklyMuscleSets]
    volume_load_per_muscle: list[MuscleVolume]
    push_pull_ratio: float | None
    upper_lower_ratio: float | None
    per_exercise: list[ExerciseStat]
    unresolved_exercises: list[str]  # free-text labels not in the catalog

    model_config = ConfigDict(populate_by_name=True)
