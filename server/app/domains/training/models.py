"""ORM models for training.

Base tables (`training_sessions`, `training_sets`) mirror initdb. Extension
columns and the catalog tables (`exercises`, `exercise_muscles`) are added by
Alembic migrations 0002 (strength) and 0003 (swim/cardio session metrics) — see
db/TODO.md "Schema additions". Models here reflect the FINAL post-migration state.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Allowed values kept as CHECK constraints (not native enums) so new values need
# no ALTER TYPE — matches the initdb convention.
_SESSION_TYPES = ("swim", "gym")
_EXERCISE_CATEGORIES = ("push", "pull", "squat", "hinge", "carry", "core", "swim", "other")
_MUSCLE_ROLES = ("primary", "secondary")


class TrainingSession(Base):
    __tablename__ = "training_sessions"
    __table_args__ = (
        CheckConstraint(
            "type IN ('swim', 'gym')", name="training_sessions_type_check"
        ),
        CheckConstraint("rpe >= 0 AND rpe <= 10", name="training_sessions_rpe_check"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    duration_min: Mapped[int | None] = mapped_column(Integer)
    rpe: Mapped[float | None] = mapped_column(Numeric(3, 1))
    load: Mapped[float | None] = mapped_column(Numeric(8, 2))
    notes: Mapped[str | None] = mapped_column(Text)

    # --- 0003 extension: Samsung swim/cardio import metrics (all nullable) ------
    kcal: Mapped[float | None] = mapped_column(Numeric(7, 2))
    avg_hr: Mapped[int | None] = mapped_column(Integer)
    max_hr: Mapped[int | None] = mapped_column(Integer)
    distance_m: Mapped[float | None] = mapped_column(Numeric(8, 2))
    # 'manual' (logged by user) | 'samsung_health' (watch import).
    source: Mapped[str] = mapped_column(Text, nullable=False, server_default="manual")

    sets: Mapped[list[TrainingSet]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class TrainingSet(Base):
    __tablename__ = "training_sets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("training_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise: Mapped[str] = mapped_column(Text, nullable=False)  # as-logged label / fallback
    set_no: Mapped[int | None] = mapped_column(Integer)
    reps: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(6, 2))
    distance_m: Mapped[float | None] = mapped_column(Numeric(8, 2))  # swim
    pace: Mapped[str | None] = mapped_column(Text)  # swim, e.g. '1:45/100m'

    # --- 0002 extension: link to catalog + richer per-set fields ---------------
    exercise_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("exercises.id"), index=True
    )
    is_warmup: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    rpe: Mapped[float | None] = mapped_column(Numeric(3, 1))
    added_weight_kg: Mapped[float | None] = mapped_column(Numeric(6, 2))  # weighted bodyweight

    session: Mapped[TrainingSession] = relationship(back_populates="sets")
    catalog_exercise: Mapped[Exercise | None] = relationship(back_populates="sets")


class Exercise(Base):
    """Exercise catalog (0002). Free-text logging still works; this drives stats."""

    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint(
            "category IN ('push','pull','squat','hinge','carry','core','swim','other')",
            name="exercises_category_check",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(Text)
    primary_muscle: Mapped[str | None] = mapped_column(Text)
    equipment: Mapped[str | None] = mapped_column(Text)
    is_unilateral: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_bodyweight: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    aliases: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    muscles: Mapped[list[ExerciseMuscle]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan"
    )
    sets: Mapped[list[TrainingSet]] = relationship(back_populates="catalog_exercise")


class ExerciseMuscle(Base):
    """Muscle taxonomy junction (0002): credits primary + fractional secondary."""

    __tablename__ = "exercise_muscles"
    __table_args__ = (
        UniqueConstraint("exercise_id", "muscle", name="exercise_muscles_uq"),
        CheckConstraint("role IN ('primary','secondary')", name="exercise_muscles_role_check"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    muscle: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False, server_default="primary")

    exercise: Mapped[Exercise] = relationship(back_populates="muscles")
