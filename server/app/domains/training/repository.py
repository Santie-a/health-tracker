"""All DB access for training. Services depend on this, not on raw sessions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import TrainingSession


async def add(session: AsyncSession, obj: TrainingSession) -> TrainingSession:
    session.add(obj)
    await session.flush()  # assign id + child ids without ending the request txn
    return obj


async def list_sessions(
    session: AsyncSession,
    type_: str | None = None,
    frm: datetime | None = None,
    to: datetime | None = None,
    limit: int = 100,
) -> list[TrainingSession]:
    stmt = select(TrainingSession).options(selectinload(TrainingSession.sets))
    if type_ is not None:
        stmt = stmt.where(TrainingSession.type == type_)
    if frm is not None:
        stmt = stmt.where(TrainingSession.ts >= frm)
    if to is not None:
        stmt = stmt.where(TrainingSession.ts <= to)
    stmt = stmt.order_by(TrainingSession.ts.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get(session: AsyncSession, session_id: int) -> TrainingSession | None:
    stmt = (
        select(TrainingSession)
        .options(selectinload(TrainingSession.sets))
        .where(TrainingSession.id == session_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
