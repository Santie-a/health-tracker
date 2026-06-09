"""Telemetry business logic. Thin for now — read-only queries over complementary
watch data. Heavier rollup/derivation logic can grow here without touching HTTP."""

from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from . import repository
from .schemas import (
    BodyCompositionPoint,
    DailyRollup,
    SleepNight,
    SleepSummary,
    TelemetryPoint,
)


async def get_points(
    session: AsyncSession, metric: str, frm: datetime | None, to: datetime | None, limit: int
) -> list[TelemetryPoint]:
    rows = await repository.query_points(session, metric, frm, to, limit)
    return [
        TelemetryPoint(ts=r.ts, metric=r.metric, value=r.value, unit=r.unit, source=r.source)
        for r in rows
    ]


async def get_sleep(session: AsyncSession, day: date_cls) -> SleepSummary | None:
    row = await repository.sleep_for_day(session, day)
    return SleepSummary.model_validate(row) if row else None


async def get_sleep_series(
    session: AsyncSession, frm: datetime | None, to: datetime | None
) -> list[SleepNight]:
    rows = await repository.query_sleep_series(session, frm, to)
    return [
        SleepNight(
            day=r.end_ts.date(),
            total_min=r.total_min,
            deep_min=r.deep_min,
            rem_min=r.rem_min,
            light_min=r.light_min,
            awake_min=r.awake_min,
            efficiency=float(r.efficiency) if r.efficiency is not None else None,
        )
        for r in rows
    ]


async def get_body_composition(
    session: AsyncSession, frm: datetime | None, to: datetime | None
) -> list[BodyCompositionPoint]:
    rows = await repository.query_body_composition(session, frm, to)
    return [
        BodyCompositionPoint(
            ts=r.ts,
            weight_kg=float(r.weight_kg) if r.weight_kg is not None else None,
            body_fat_pct=float(r.body_fat_pct) if r.body_fat_pct is not None else None,
            skeletal_muscle_kg=(
                float(r.skeletal_muscle_kg) if r.skeletal_muscle_kg is not None else None
            ),
            bmr_kcal=r.bmr_kcal,
        )
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
