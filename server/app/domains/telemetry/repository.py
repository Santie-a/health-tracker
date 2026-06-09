"""All DB access for telemetry. Services depend on this, not on raw sessions."""

from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import BodyComposition, SleepSession, Telemetry


async def query_points(
    session: AsyncSession,
    metric: str,
    frm: datetime | None = None,
    to: datetime | None = None,
    limit: int = 1000,
) -> list[Telemetry]:
    stmt = select(Telemetry).where(Telemetry.metric == metric)
    if frm is not None:
        stmt = stmt.where(Telemetry.ts >= frm)
    if to is not None:
        stmt = stmt.where(Telemetry.ts <= to)
    stmt = stmt.order_by(Telemetry.ts).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def query_daily(
    session: AsyncSession,
    metric: str,
    frm: datetime | None = None,
    to: datetime | None = None,
) -> list[dict]:
    """On-the-fly daily rollup via date_trunc (Timescale optimizes this). The
    `telemetry_daily` continuous aggregate can replace this later for scale."""
    day = func.date_trunc("day", Telemetry.ts).label("day")
    stmt = (
        select(
            day,
            func.avg(Telemetry.value).label("avg"),
            func.min(Telemetry.value).label("min"),
            func.max(Telemetry.value).label("max"),
            func.sum(Telemetry.value).label("sum"),
            func.count().label("count"),
        )
        .where(Telemetry.metric == metric)
    )
    if frm is not None:
        stmt = stmt.where(Telemetry.ts >= frm)
    if to is not None:
        stmt = stmt.where(Telemetry.ts <= to)
    stmt = stmt.group_by(day).order_by(day)
    result = await session.execute(stmt)
    return [dict(row._mapping) for row in result]


async def query_sleep_series(
    session: AsyncSession, frm: datetime | None = None, to: datetime | None = None
) -> list[SleepSession]:
    """Nights ordered by when they ended, for the sleep trend."""
    stmt = select(SleepSession)
    if frm is not None:
        stmt = stmt.where(SleepSession.end_ts >= frm)
    if to is not None:
        stmt = stmt.where(SleepSession.end_ts <= to)
    stmt = stmt.order_by(SleepSession.end_ts)
    return list((await session.execute(stmt)).scalars().all())


async def query_body_composition(
    session: AsyncSession, frm: datetime | None = None, to: datetime | None = None
) -> list[BodyComposition]:
    """Smart-scale readings ordered by time, for weight/body-fat/muscle trends."""
    stmt = select(BodyComposition)
    if frm is not None:
        stmt = stmt.where(BodyComposition.ts >= frm)
    if to is not None:
        stmt = stmt.where(BodyComposition.ts <= to)
    stmt = stmt.order_by(BodyComposition.ts)
    return list((await session.execute(stmt)).scalars().all())


async def sleep_for_day(session: AsyncSession, day: date_cls) -> SleepSession | None:
    """The night that ended on `day` (longest session if more than one)."""
    start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    stmt = (
        select(SleepSession)
        .where(SleepSession.end_ts >= start, SleepSession.end_ts < end)
        .order_by(SleepSession.total_min.desc().nullslast())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()
