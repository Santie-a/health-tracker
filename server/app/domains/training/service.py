"""Training business logic. The only layer with domain rules (e.g. session load)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date as date_cls
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timerange import range_bounds

from . import repository
from .models import Exercise, ExerciseMuscle, TrainingSession, TrainingSet
from .muscles import SECONDARY_CREDIT, muscle_group
from .schemas import (
    AddSetsIn,
    ExerciseIn,
    ExerciseOut,
    ExerciseStat,
    ExerciseUpdate,
    MuscleVolume,
    TrainingSessionIn,
    TrainingSessionOut,
    TrainingSessionUpdate,
    TrainingSetUpdate,
    TrainingStats,
    WeeklyMuscleSets,
)


class DuplicateExercise(Exception):
    """Raised when an exercise slug already exists."""


def slugify(name: str) -> str:
    return name.lower().replace("-", " ").replace("'", "").strip().replace(" ", "_")


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def _name_index(exercises: list[Exercise]) -> dict[str, Exercise]:
    """Normalized name/alias -> Exercise, for resolving free-text set labels."""
    idx: dict[str, Exercise] = {}
    for ex in exercises:
        idx.setdefault(_norm(ex.name), ex)
        for alias in ex.aliases or []:
            idx.setdefault(_norm(alias), ex)
    return idx


def compute_load(duration_min: int | None, rpe: float | None, explicit: float | None) -> float | None:
    """Session load = duration_min × RPE (a simple sRPE training-load proxy).
    An explicit value always wins; otherwise it's derived when both inputs exist."""
    if explicit is not None:
        return explicit
    if duration_min is not None and rpe is not None:
        return round(duration_min * float(rpe), 2)
    return None


def _as_utc(ts: datetime) -> datetime:
    return ts if ts.tzinfo is not None else ts.replace(tzinfo=timezone.utc)


async def create_session(session: AsyncSession, payload: TrainingSessionIn) -> TrainingSessionOut:
    # Build sets up front and pass them to the constructor so the relationship is a
    # loaded collection — otherwise serializing a session with zero sets lazy-loads
    # under async (MissingGreenlet).
    sets = [
        TrainingSet(
            exercise=s.exercise,
            set_no=s.set_no,
            reps=s.reps,
            weight_kg=s.weight_kg,
            distance_m=s.distance_m,
            pace=s.pace,
            rpe=s.rpe,
            is_warmup=s.is_warmup,
            added_weight_kg=s.added_weight_kg,
        )
        for s in payload.sets
    ]
    obj = TrainingSession(
        ts=_as_utc(payload.ts),
        type=payload.type,
        duration_min=payload.duration_min,
        rpe=payload.rpe,
        load=compute_load(payload.duration_min, payload.rpe, payload.load),
        notes=payload.notes,
        source="manual",
        sets=sets,
    )
    await repository.add(session, obj)
    return TrainingSessionOut.model_validate(obj)


async def list_sessions(
    session: AsyncSession, type_: str | None, frm: datetime | None, to: datetime | None, limit: int
) -> list[TrainingSessionOut]:
    rows = await repository.list_sessions(session, type_, frm, to, limit)
    return [TrainingSessionOut.model_validate(r) for r in rows]


async def get_session(session: AsyncSession, session_id: int) -> TrainingSessionOut | None:
    obj = await repository.get(session, session_id)
    return TrainingSessionOut.model_validate(obj) if obj else None


# --- exercise catalog --------------------------------------------------------

async def create_exercise(session: AsyncSession, payload: ExerciseIn) -> ExerciseOut:
    slug = slugify(payload.name)
    if await repository.get_exercise_by_slug(session, slug) is not None:
        raise DuplicateExercise(slug)

    # Ensure the primary_muscle is represented as a primary row, then merge in the
    # supplied muscle rows (de-duped).
    rows = []
    seen = set()
    if payload.primary_muscle:
        rows.append(ExerciseMuscle(muscle=payload.primary_muscle, role="primary"))
        seen.add((payload.primary_muscle, "primary"))
    for m in payload.muscles:
        if (m.muscle, m.role) in seen:
            continue
        seen.add((m.muscle, m.role))
        rows.append(ExerciseMuscle(muscle=m.muscle, role=m.role))

    ex = Exercise(
        name=payload.name,
        slug=slug,
        category=payload.category,
        primary_muscle=payload.primary_muscle,
        equipment=payload.equipment,
        is_unilateral=payload.is_unilateral,
        is_bodyweight=payload.is_bodyweight,
        aliases=payload.aliases,
        muscles=rows,
    )
    await repository.add_exercise(session, ex)
    return ExerciseOut.model_validate(ex)


async def search_exercises(
    session: AsyncSession, q: str | None, muscle: str | None, category: str | None, limit: int
) -> list[ExerciseOut]:
    rows = await repository.search_exercises(session, q, muscle, category, limit)
    return [ExerciseOut.model_validate(r) for r in rows]


async def update_exercise(
    session: AsyncSession, exercise_id: int, payload: ExerciseUpdate
) -> ExerciseOut | None:
    ex = await repository.get_exercise(session, exercise_id)
    if ex is None:
        return None
    data = payload.model_dump(exclude_unset=True)

    # Renaming regenerates the slug; guard the unique constraint against other rows.
    if "name" in data and data["name"]:
        slug = slugify(data["name"])
        existing = await repository.get_exercise_by_slug(session, slug)
        if existing is not None and existing.id != ex.id:
            raise DuplicateExercise(slug)
        ex.slug = slug

    # `muscles` (when supplied) replaces the set wholesale; primary_muscle is folded in
    # as a primary row to mirror create_exercise.
    muscles = data.pop("muscles", None)
    for field, value in data.items():
        setattr(ex, field, value)
    if muscles is not None:
        rows, seen = [], set()
        primary = data.get("primary_muscle", ex.primary_muscle)
        if primary:
            rows.append(ExerciseMuscle(muscle=primary, role="primary"))
            seen.add((primary, "primary"))
        for m in muscles:
            if (m.muscle, m.role) in seen:
                continue
            seen.add((m.muscle, m.role))
            rows.append(ExerciseMuscle(muscle=m.muscle, role=m.role))
        ex.muscles = rows  # cascade delete-orphan clears the old rows

    await session.flush()
    fresh = await repository.get_exercise(session, exercise_id)
    return ExerciseOut.model_validate(fresh)


async def delete_exercise(session: AsyncSession, exercise_id: int) -> str | None:
    """Hard-delete when no logged set references the exercise; otherwise soft-delete
    (is_active=False) to preserve historical sets. Returns the action, or None if
    the exercise doesn't exist."""
    ex = await repository.get_exercise(session, exercise_id)
    if ex is None:
        return None
    if await repository.count_sets_for_exercise(session, exercise_id) > 0:
        ex.is_active = False
        await session.flush()
        return "deactivated"
    await repository.delete_exercise(session, ex)
    return "deleted"


# --- per-set logging ---------------------------------------------------------

async def add_sets(
    session: AsyncSession, session_id: int, payload: AddSetsIn
) -> TrainingSessionOut | None:
    obj = await repository.get(session, session_id)
    if obj is None:
        return None
    index = _name_index(await repository.load_catalog(session))
    for s in payload.sets:
        match = index.get(_norm(s.exercise))
        obj.sets.append(
            TrainingSet(
                exercise=s.exercise,
                exercise_id=match.id if match else None,
                set_no=s.set_no,
                reps=s.reps,
                weight_kg=s.weight_kg,
                distance_m=s.distance_m,
                pace=s.pace,
                rpe=s.rpe,
                is_warmup=s.is_warmup,
                added_weight_kg=s.added_weight_kg,
            )
        )
    await session.flush()
    return TrainingSessionOut.model_validate(obj)


# --- edit / delete (v1.1) ----------------------------------------------------

async def update_session(
    session: AsyncSession, session_id: int, payload: TrainingSessionUpdate
) -> TrainingSessionOut | None:
    obj = await repository.get(session, session_id)
    if obj is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    if "ts" in data and data["ts"] is not None:
        data["ts"] = _as_utc(data["ts"])
    for field, value in data.items():
        setattr(obj, field, value)
    # Recompute load unless the caller pinned it: any change to duration/rpe (or an
    # explicit load) flows through compute_load with the post-edit values.
    if {"duration_min", "rpe", "load"} & data.keys():
        obj.load = compute_load(obj.duration_min, obj.rpe, data.get("load", obj.load))
    await session.flush()
    return TrainingSessionOut.model_validate(obj)


async def delete_session(session: AsyncSession, session_id: int) -> bool:
    obj = await repository.get(session, session_id)
    if obj is None:
        return False
    await repository.delete(session, obj)
    return True


async def update_set(
    session: AsyncSession, session_id: int, set_id: int, payload: TrainingSetUpdate
) -> TrainingSessionOut | None:
    s = await repository.get_set(session, session_id, set_id)
    if s is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(s, field, value)
    # Re-resolve the catalog link when the free-text exercise label changes.
    if "exercise" in data:
        index = _name_index(await repository.load_catalog(session))
        match = index.get(_norm(s.exercise or ""))
        s.exercise_id = match.id if match else None
    await session.flush()
    obj = await repository.get(session, session_id)
    return TrainingSessionOut.model_validate(obj)


async def delete_set(
    session: AsyncSession, session_id: int, set_id: int
) -> TrainingSessionOut | None:
    s = await repository.get_set(session, session_id, set_id)
    if s is None:
        return None
    await repository.delete_set(session, s)
    obj = await repository.get(session, session_id)
    return TrainingSessionOut.model_validate(obj)


# --- strength stats ----------------------------------------------------------

def _monday(d: date_cls) -> date_cls:
    return d - timedelta(days=d.weekday())


async def get_stats(session: AsyncSession, frm: date_cls, to: date_cls) -> TrainingStats:
    start, end = range_bounds(frm, to)  # local calendar days → UTC instants (APP_TIMEZONE)

    catalog = await repository.load_catalog(session)
    by_id = {ex.id: ex for ex in catalog}
    name_idx = _name_index(catalog)
    rows = await repository.load_sets_for_stats(session, start, end)

    weekly: dict[tuple[date_cls, str], float] = defaultdict(float)
    volume: dict[str, float] = defaultdict(float)
    push = pull = upper = lower = 0
    per_ex: dict[str, dict] = {}
    unresolved: set[str] = set()

    for r in rows:
        ex = by_id.get(r.exercise_id) or name_idx.get(_norm(r.exercise or ""))
        day = r.ts.date()
        week = _monday(day)
        reps = r.reps or 0
        weight = float(r.weight_kg or 0) + float(r.added_weight_kg or 0)

        key = ex.slug if ex else f"~{_norm(r.exercise or 'unknown')}"
        pe = per_ex.setdefault(
            key,
            {"name": ex.name if ex else (r.exercise or "unknown"),
             "slug": ex.slug if ex else None,
             "sets": 0, "top": None, "e1rm": None, "date": None},
        )
        pe["sets"] += 1
        if weight > 0:
            pe["top"] = weight if pe["top"] is None else max(pe["top"], weight)
            if reps > 0:
                e1rm = round(weight * (1 + reps / 30), 1)
                if pe["e1rm"] is None or e1rm > pe["e1rm"]:
                    pe["e1rm"], pe["date"] = e1rm, day

        if ex is None:
            unresolved.add(r.exercise or "unknown")
            continue

        for em in ex.muscles:
            credit = 1.0 if em.role == "primary" else SECONDARY_CREDIT
            weekly[(week, em.muscle)] += credit
            volume[em.muscle] += reps * weight * credit
        if ex.category == "push":
            push += 1
        elif ex.category == "pull":
            pull += 1
        grp = muscle_group(ex.primary_muscle or "")
        if grp == "upper":
            upper += 1
        elif grp == "lower":
            lower += 1

    return TrainingStats(
        **{"from": frm},
        to=to,
        weekly_sets_per_muscle=sorted(
            (WeeklyMuscleSets(week=w, muscle=m, sets=round(c, 1)) for (w, m), c in weekly.items()),
            key=lambda x: (x.week, x.muscle),
        ),
        volume_load_per_muscle=sorted(
            (MuscleVolume(muscle=m, volume_load=round(v, 1)) for m, v in volume.items()),
            key=lambda x: x.muscle,
        ),
        push_pull_ratio=round(push / pull, 2) if pull else None,
        upper_lower_ratio=round(upper / lower, 2) if lower else None,
        per_exercise=sorted(
            (
                ExerciseStat(
                    exercise=pe["name"], slug=pe["slug"], sets=pe["sets"],
                    top_weight_kg=pe["top"], best_e1rm=pe["e1rm"], best_e1rm_date=pe["date"],
                )
                for pe in per_ex.values()
            ),
            key=lambda x: x.exercise,
        ),
        unresolved_exercises=sorted(unresolved),
    )
