"""All DB access for training. Services depend on this, not on raw sessions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Exercise, ExerciseMuscle, TrainingSession, TrainingSet


async def add(session: AsyncSession, obj: TrainingSession) -> TrainingSession:
    session.add(obj)
    await session.flush()  # assign id + child ids without ending the request txn
    return obj


async def list_sessions(
    session: AsyncSession,
    type_: str | None = None,
    frm: datetime | None = None,
    to: datetime | None = None,
    limit: int = 100,
) -> list[TrainingSession]:
    stmt = select(TrainingSession).options(selectinload(TrainingSession.sets))
    if type_ is not None:
        stmt = stmt.where(TrainingSession.type == type_)
    if frm is not None:
        stmt = stmt.where(TrainingSession.ts >= frm)
    if to is not None:
        stmt = stmt.where(TrainingSession.ts <= to)
    stmt = stmt.order_by(TrainingSession.ts.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get(session: AsyncSession, session_id: int) -> TrainingSession | None:
    stmt = (
        select(TrainingSession)
        .options(selectinload(TrainingSession.sets))
        .where(TrainingSession.id == session_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


# --- exercise catalog --------------------------------------------------------

async def add_exercise(session: AsyncSession, ex: Exercise) -> Exercise:
    session.add(ex)
    await session.flush()
    return ex


async def get_exercise_by_slug(session: AsyncSession, slug: str) -> Exercise | None:
    return (
        await session.execute(
            select(Exercise).options(selectinload(Exercise.muscles)).where(Exercise.slug == slug)
        )
    ).scalar_one_or_none()


async def search_exercises(
    session: AsyncSession,
    q: str | None = None,
    muscle: str | None = None,
    category: str | None = None,
    limit: int = 50,
) -> list[Exercise]:
    stmt = (
        select(Exercise)
        .options(selectinload(Exercise.muscles))
        .where(Exercise.is_active.is_(True))
    )
    if q:
        stmt = stmt.where(or_(Exercise.name.ilike(f"%{q}%"), Exercise.aliases.any(q)))
    if muscle:
        stmt = stmt.where(Exercise.muscles.any(ExerciseMuscle.muscle == muscle))
    if category:
        stmt = stmt.where(Exercise.category == category)
    stmt = stmt.order_by(Exercise.name).limit(limit)
    return list((await session.execute(stmt)).scalars().all())


async def load_catalog(session: AsyncSession) -> list[Exercise]:
    """All active exercises with muscles loaded — for stats + name resolution."""
    return list(
        (
            await session.execute(
                select(Exercise)
                .options(selectinload(Exercise.muscles))
                .where(Exercise.is_active.is_(True))
            )
        ).scalars().all()
    )


async def load_sets_for_stats(session: AsyncSession, frm: datetime, to: datetime):
    """Working sets in range (warmups excluded) joined to their session timestamp."""
    stmt = (
        select(
            TrainingSet.exercise,
            TrainingSet.exercise_id,
            TrainingSet.reps,
            TrainingSet.weight_kg,
            TrainingSet.added_weight_kg,
            TrainingSession.ts,
        )
        .join(TrainingSession, TrainingSet.session_id == TrainingSession.id)
        .where(
            TrainingSession.ts >= frm,
            TrainingSession.ts < to,
            TrainingSet.is_warmup.is_(False),
        )
    )
    return (await session.execute(stmt)).all()
