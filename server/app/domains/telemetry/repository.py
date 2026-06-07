"""All DB access for telemetry. Services depend on this, not on raw sessions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Telemetry


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
