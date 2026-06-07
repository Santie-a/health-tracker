"""Thin HTTP layer for training. Validation + status codes only."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_token
from app.core.db import get_session

from . import service
from .schemas import SessionType, TrainingSessionIn, TrainingSessionOut

router = APIRouter(prefix="/training", tags=["training"], dependencies=[Depends(require_token)])


@router.post("", response_model=TrainingSessionOut, status_code=status.HTTP_201_CREATED)
async def create_training(
    payload: TrainingSessionIn,
    session: AsyncSession = Depends(get_session),
) -> TrainingSessionOut:
    return await service.create_session(session, payload)


@router.get("", response_model=list[TrainingSessionOut])
async def list_training(
    type: SessionType | None = Query(None, description="Filter by session type."),
    frm: datetime | None = Query(None, alias="from"),
    to: datetime | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
) -> list[TrainingSessionOut]:
    return await service.list_sessions(session, type, frm, to, limit)


@router.get("/{session_id}", response_model=TrainingSessionOut)
async def get_training(
    session_id: int,
    session: AsyncSession = Depends(get_session),
) -> TrainingSessionOut:
    obj = await service.get_session(session, session_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found.")
    return obj
