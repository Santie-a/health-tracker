"""Telemetry business logic. Thin for now — read-only queries over complementary
watch data. Heavier rollup/derivation logic can grow here without touching HTTP."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from . import repository
from .schemas import DailyRollup, TelemetryPoint


async def get_points(
    session: AsyncSession, metric: str, frm: datetime | None, to: datetime | None, limit: int
) -> list[TelemetryPoint]:
    rows = await repository.query_points(session, metric, frm, to, limit)
    return [
        TelemetryPoint(ts=r.ts, metric=r.metric, value=r.value, unit=r.unit, source=r.source)
        for r in rows
    ]


async def get_daily(
    session: AsyncSession, metric: str, frm: datetime | None, to: datetime | None
) -> list[DailyRollup]:
    rows = await repository.query_daily(session, metric, frm, to)
    return [
        DailyRollup(
            day=r["day"].date(),
            metric=metric,
            avg=float(r["avg"]) if r["avg"] is not None else None,
            min=float(r["min"]) if r["min"] is not None else None,
            max=float(r["max"]) if r["max"] is not None else None,
            sum=float(r["sum"]) if r["sum"] is not None else None,
            count=r["count"],
        )
        for r in rows
    ]
