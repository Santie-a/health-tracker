"""Thin HTTP layer for the aggregated day view."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_token
from app.core.db import get_session

from . import service
from .schemas import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(require_token)])


@router.get("", response_model=DashboardOut)
async def dashboard(
    date: date = Query(..., description="Day to summarize (YYYY-MM-DD, UTC)."),
    session: AsyncSession = Depends(get_session),
) -> DashboardOut:
    """One call powering the frontend home: telemetry summary + training + nutrition
    totals + recommendations for the day."""
    return await service.get_dashboard(session, date)
