"""Thin HTTP layer for recommendations."""

from __future__ import annotations

from datetime import date as date_cls

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_token
from app.core.db import get_session

from . import service
from .schemas import FeedbackIn, RecommendationsOut

router = APIRouter(
    prefix="/recommendations", tags=["recommendations"], dependencies=[Depends(require_token)]
)


@router.get("", response_model=RecommendationsOut)
async def get_recommendations(
    date: date_cls = Query(..., description="Day to fetch (YYYY-MM-DD, UTC)."),
    session: AsyncSession = Depends(get_session),
) -> RecommendationsOut:
    """Today's recommendations. Generated + stored lazily on first request for a day."""
    return await service.get_for_date(session, date)


@router.post("/run", response_model=RecommendationsOut)
async def run_recommendations(
    date: date_cls = Query(..., description="Day to (re)generate."),
    session: AsyncSession = Depends(get_session),
) -> RecommendationsOut:
    """Force a regenerate + store (the daily-pass trigger)."""
    return await service.generate_for_date(session, date, store=True)


@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def submit_feedback(
    payload: FeedbackIn,
    session: AsyncSession = Depends(get_session),
) -> None:
    ok = await service.set_feedback(session, payload.date, payload.feedback)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations stored for that date yet.",
        )
