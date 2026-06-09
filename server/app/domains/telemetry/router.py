"""Thin HTTP layer for telemetry reads. Validation + status codes only."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_token
from app.core.db import get_session

from . import service
from .schemas import BodyCompositionPoint, DailyRollup, SleepNight, TelemetryPoint

router = APIRouter(prefix="/telemetry", tags=["telemetry"], dependencies=[Depends(require_token)])
body_router = APIRouter(
    prefix="/body-composition", tags=["telemetry"], dependencies=[Depends(require_token)]
)


@router.get("", response_model=list[TelemetryPoint])
async def list_points(
    metric: str = Query(..., description="e.g. steps | stress | spo2 | heart_rate | energy_expenditure"),
    frm: datetime | None = Query(None, alias="from", description="ISO start (inclusive)."),
    to: datetime | None = Query(None, description="ISO end (inclusive)."),
    limit: int = Query(1000, ge=1, le=50000),
    session: AsyncSession = Depends(get_session),
) -> list[TelemetryPoint]:
    return await service.get_points(session, metric, frm, to, limit)


@router.get("/daily", response_model=list[DailyRollup])
async def daily_rollup(
    metric: str = Query(...),
    frm: datetime | None = Query(None, alias="from"),
    to: datetime | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[DailyRollup]:
    return await service.get_daily(session, metric, frm, to)


@router.get("/sleep", response_model=list[SleepNight])
async def sleep_series(
    frm: datetime | None = Query(None, alias="from", description="ISO start (inclusive)."),
    to: datetime | None = Query(None, description="ISO end (inclusive)."),
    session: AsyncSession = Depends(get_session),
) -> list[SleepNight]:
    """Per-night sleep summaries (total + stages) for the sleep trend."""
    return await service.get_sleep_series(session, frm, to)


@body_router.get("", response_model=list[BodyCompositionPoint])
async def body_composition(
    frm: datetime | None = Query(None, alias="from", description="ISO start (inclusive)."),
    to: datetime | None = Query(None, description="ISO end (inclusive)."),
    session: AsyncSession = Depends(get_session),
) -> list[BodyCompositionPoint]:
    """Smart-scale series (weight, body fat %, skeletal muscle, BMR) for trends."""
    return await service.get_body_composition(session, frm, to)
