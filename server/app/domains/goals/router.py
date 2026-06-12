"""Thin HTTP layer for goals: CRUD plus progress (the fitted trend vs target)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_token
from app.core.db import get_session

from . import service
from .schemas import GoalIn, GoalOut, GoalProgressOut, GoalUpdate, GoalWithProgressOut

router = APIRouter(prefix="/goals", tags=["goals"], dependencies=[Depends(require_token)])


@router.get("", response_model=list[GoalOut])
async def list_goals(
    status_: str | None = Query(None, alias="status", description="Filter by active|achieved|abandoned."),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[GoalOut]:
    return await service.list_goals(session, status_, limit)


@router.get("/active", response_model=list[GoalWithProgressOut])
async def active_goals(
    session: AsyncSession = Depends(get_session),
) -> list[GoalWithProgressOut]:
    """The current active goal(s) (at most one body + one sleep) with live progress."""
    return await service.list_active_with_progress(session)


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalIn,
    session: AsyncSession = Depends(get_session),
) -> GoalOut:
    """Create a goal. Unspecified fields are filled from the goal type (category,
    metric, surplus/deficit, protein target, baseline from latest body comp)."""
    try:
        return await service.create_goal(session, payload)
    except service.DuplicateActiveGoal as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An active {exc.category} goal already exists. Mark it achieved/abandoned first.",
        )


@router.get("/{goal_id}", response_model=GoalWithProgressOut)
async def get_goal(
    goal_id: int,
    session: AsyncSession = Depends(get_session),
) -> GoalWithProgressOut:
    goal = await service.get_goal_with_progress(session, goal_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found.")
    return goal


@router.get("/{goal_id}/progress", response_model=GoalProgressOut)
async def goal_progress(
    goal_id: int,
    session: AsyncSession = Depends(get_session),
) -> GoalProgressOut:
    from . import repository

    goal = await repository.get(session, goal_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found.")
    return await service.progress_for(session, goal)


@router.patch("/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    session: AsyncSession = Depends(get_session),
) -> GoalOut:
    """Edit a goal or change its status (active|achieved|abandoned)."""
    try:
        goal = await service.update_goal(session, goal_id, payload)
    except service.DuplicateActiveGoal as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An active {exc.category} goal already exists.",
        )
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found.")
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    if not await service.delete_goal(session, goal_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found.")
