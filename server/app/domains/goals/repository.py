"""All DB access for goals: the goal rows themselves plus the metric time-series
(body composition / sleep) used to compute progress. Services depend on this, not
on raw sessions."""

from __future__ import annotations

from datetime import date as date_cls

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timerange import app_tz, range_bounds
from app.domains.telemetry.models import BodyComposition, SleepSession

from .models import Goal
from .progress import Reading

# Which table/column each goal metric reads from, and the timestamp that anchors it.
_BODY_COLS = {
    "weight_kg": BodyComposition.weight_kg,
    "skeletal_muscle_kg": BodyComposition.skeletal_muscle_kg,
    "body_fat_pct": BodyComposition.body_fat_pct,
}
_SLEEP_COLS = {
    "sleep_min": SleepSession.total_min,
    "sleep_efficiency": SleepSession.efficiency,
}


async def add(session: AsyncSession, obj: Goal) -> Goal:
    session.add(obj)
    await session.flush()  # assign id without ending the request txn
    return obj


async def get(session: AsyncSession, goal_id: int) -> Goal | None:
    return (
        await session.execute(select(Goal).where(Goal.id == goal_id))
    ).scalar_one_or_none()


async def get_active(session: AsyncSession, category: str) -> Goal | None:
    """The single active goal for a category (body / sleep), if any."""
    return (
        await session.execute(
            select(Goal).where(Goal.category == category, Goal.status == "active")
        )
    ).scalar_one_or_none()


async def list_active(session: AsyncSession) -> list[Goal]:
    rows = await session.execute(
        select(Goal).where(Goal.status == "active").order_by(Goal.category)
    )
    return list(rows.scalars().all())


async def list_all(session: AsyncSession, status: str | None, limit: int) -> list[Goal]:
    stmt = select(Goal)
    if status is not None:
        stmt = stmt.where(Goal.status == status)
    stmt = stmt.order_by(Goal.created_at.desc()).limit(limit)
    return list((await session.execute(stmt)).scalars().all())


async def delete(session: AsyncSession, obj: Goal) -> None:
    await session.delete(obj)
    await session.flush()


async def latest_body_value(session: AsyncSession, metric: str) -> float | None:
    """Most recent non-null reading for a body metric — used to seed a baseline."""
    col = _BODY_COLS.get(metric)
    if col is None:
        return None
    val = (
        await session.execute(
            select(col).where(col.is_not(None)).order_by(BodyComposition.ts.desc()).limit(1)
        )
    ).scalar_one_or_none()
    return float(val) if val is not None else None


async def metric_series(
    session: AsyncSession, metric: str, frm: date_cls, to: date_cls
) -> list[Reading]:
    """Readings for a goal metric over [frm, to] local days, as (local-day, value).

    Body metrics come from body_composition (anchored on ts); sleep metrics from
    sleep_sessions (anchored on the night's end_ts). Telemetry is optional, so a
    metric the user hasn't logged simply yields an empty series."""
    start, end = range_bounds(frm, to)
    tz = app_tz()

    if metric in _BODY_COLS:
        col = _BODY_COLS[metric]
        rows = (
            await session.execute(
                select(BodyComposition.ts, col)
                .where(col.is_not(None), BodyComposition.ts >= start, BodyComposition.ts < end)
                .order_by(BodyComposition.ts)
            )
        ).all()
        return [Reading(day=ts.astimezone(tz).date(), value=float(v)) for ts, v in rows]

    if metric in _SLEEP_COLS:
        col = _SLEEP_COLS[metric]
        rows = (
            await session.execute(
                select(SleepSession.end_ts, col)
                .where(col.is_not(None), SleepSession.end_ts >= start, SleepSession.end_ts < end)
                .order_by(SleepSession.end_ts)
            )
        ).all()
        return [Reading(day=ts.astimezone(tz).date(), value=float(v)) for ts, v in rows]

    return []
