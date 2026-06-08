"""All DB access for nutrition."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Meal


async def add(session: AsyncSession, meal: Meal) -> Meal:
    session.add(meal)
    await session.flush()
    return meal


async def list_in_range(session: AsyncSession, frm: datetime, to: datetime) -> list[Meal]:
    stmt = (
        select(Meal)
        .options(selectinload(Meal.items))
        .where(Meal.ts >= frm, Meal.ts < to)
        .order_by(Meal.ts)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get(session: AsyncSession, meal_id: int) -> Meal | None:
    stmt = select(Meal).options(selectinload(Meal.items)).where(Meal.id == meal_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
