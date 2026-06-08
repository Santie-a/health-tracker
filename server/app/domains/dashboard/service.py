"""Aggregate one day across telemetry, training, nutrition, and recommendations."""

from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime, time, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.nutrition import service as nutrition_service
from app.domains.recommendations import service as recommendations_service
from app.domains.telemetry import service as telemetry_service
from app.domains.training import service as training_service

from .schemas import DashboardOut, TelemetrySummary

# metric -> which rollup field is meaningful (additive sum vs average)
_SUM_METRICS = {"steps", "energy_expenditure"}


async def _metric(session: AsyncSession, metric: str, day, start, end) -> float | None:
    rows = await telemetry_service.get_daily(session, metric, start, end)
    row = next((r for r in rows if r.day == day), None)
    if row is None:
        return None
    return row.sum if metric in _SUM_METRICS else row.avg


async def get_dashboard(session: AsyncSession, day: date_cls) -> DashboardOut:
    start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    telemetry = TelemetrySummary(
        steps=await _metric(session, "steps", day, start, end),
        avg_stress=await _metric(session, "stress", day, start, end),
        avg_heart_rate=await _metric(session, "heart_rate", day, start, end),
        avg_spo2=await _metric(session, "spo2", day, start, end),
        energy_expenditure=await _metric(session, "energy_expenditure", day, start, end),
        sleep=await telemetry_service.get_sleep(session, day),
    )

    training = await training_service.list_sessions(session, None, start, end, limit=50)
    nutrition = await nutrition_service.get_day(session, day)
    recs = await recommendations_service.get_for_date(session, day)

    return DashboardOut(
        date=day,
        telemetry=telemetry,
        training=training,
        nutrition_totals=nutrition.totals,
        meals=nutrition.meals,
        recommendations=recs.recommendations,
    )
