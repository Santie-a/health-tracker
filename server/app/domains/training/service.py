"""Training business logic. The only layer with domain rules (e.g. session load)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from . import repository
from .models import TrainingSession, TrainingSet
from .schemas import TrainingSessionIn, TrainingSessionOut


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
