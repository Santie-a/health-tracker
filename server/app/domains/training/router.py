"""Thin HTTP layer for training: sessions, sets, exercise catalog, strength stats."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_token
from app.core.db import get_session

from . import service
from .schemas import (
    AddSetsIn,
    ExerciseIn,
    ExerciseOut,
    ExerciseUpdate,
    SessionType,
    TrainingSessionIn,
    TrainingSessionOut,
    TrainingSessionUpdate,
    TrainingSetUpdate,
    TrainingStats,
)

router = APIRouter(prefix="/training", tags=["training"], dependencies=[Depends(require_token)])

# Separate router so /exercises isn't nested under /training/{id}.
exercises_router = APIRouter(prefix="/exercises", tags=["training"], dependencies=[Depends(require_token)])


# --- exercise catalog --------------------------------------------------------

@exercises_router.get("", response_model=list[ExerciseOut])
async def search_exercises(
    q: str | None = Query(None, description="Name/alias substring for autocomplete."),
    muscle: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[ExerciseOut]:
    return await service.search_exercises(session, q, muscle, category, limit)


@exercises_router.post("", response_model=ExerciseOut, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    payload: ExerciseIn,
    session: AsyncSession = Depends(get_session),
) -> ExerciseOut:
    try:
        return await service.create_exercise(session, payload)
    except service.DuplicateExercise as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Exercise '{exc}' already exists.",
        )


@exercises_router.patch("/{exercise_id}", response_model=ExerciseOut)
async def update_exercise(
    exercise_id: int,
    payload: ExerciseUpdate,
    session: AsyncSession = Depends(get_session),
) -> ExerciseOut:
    """Edit a catalog exercise. Renaming regenerates the slug (409 on collision)."""
    try:
        ex = await service.update_exercise(session, exercise_id, payload)
    except service.DuplicateExercise as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Exercise '{exc}' already exists.",
        )
    if ex is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found.")
    return ex


@exercises_router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Delete a catalog exercise. Soft-deletes (deactivates) instead when logged sets
    still reference it, so history stays intact. Returns the action taken."""
    action = await service.delete_exercise(session, exercise_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found.")
    return {"action": action}


# --- strength stats (registered before /{session_id} to avoid capture) -------

@router.get("/stats", response_model=TrainingStats)
async def training_stats(
    frm: date | None = Query(None, alias="from", description="Default: 8 weeks ago."),
    to: date | None = Query(None, description="Default: today."),
    session: AsyncSession = Depends(get_session),
) -> TrainingStats:
    to = to or datetime.utcnow().date()
    frm = frm or (to - timedelta(weeks=8))
    return await service.get_stats(session, frm, to)


# --- sessions ----------------------------------------------------------------

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


@router.patch("/{session_id}", response_model=TrainingSessionOut)
async def update_training(
    session_id: int,
    payload: TrainingSessionUpdate,
    session: AsyncSession = Depends(get_session),
) -> TrainingSessionOut:
    """Edit session fields; `load` recomputes from duration×rpe when unset explicitly."""
    obj = await service.update_session(session, session_id, payload)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found.")
    return obj


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training(
    session_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    if not await service.delete_session(session, session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found.")


@router.post("/{session_id}/sets", response_model=TrainingSessionOut, status_code=status.HTTP_201_CREATED)
async def add_sets(
    session_id: int,
    payload: AddSetsIn,
    session: AsyncSession = Depends(get_session),
) -> TrainingSessionOut:
    """Log sets against a session; free-text exercise names resolve to the catalog."""
    obj = await service.add_sets(session, session_id, payload)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found.")
    return obj


@router.patch("/{session_id}/sets/{set_id}", response_model=TrainingSessionOut)
async def update_set(
    session_id: int,
    set_id: int,
    payload: TrainingSetUpdate,
    session: AsyncSession = Depends(get_session),
) -> TrainingSessionOut:
    """Edit one set; returns the updated session."""
    obj = await service.update_set(session, session_id, set_id, payload)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set not found.")
    return obj


@router.delete("/{session_id}/sets/{set_id}", response_model=TrainingSessionOut)
async def delete_set(
    session_id: int,
    set_id: int,
    session: AsyncSession = Depends(get_session),
) -> TrainingSessionOut:
    """Remove one set; returns the updated session."""
    obj = await service.delete_set(session, session_id, set_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set not found.")
    return obj
