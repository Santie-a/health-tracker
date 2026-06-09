"""All DB access for nutrition."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Food, Meal, MealItem


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


# --- foods catalog -----------------------------------------------------------

async def search_foods(session: AsyncSession, q: str | None, limit: int) -> list[Food]:
    stmt = select(Food).options(selectinload(Food.portions))
    if q:
        stmt = stmt.where(or_(Food.name.ilike(f"%{q}%"), Food.aliases.any(q)))
    stmt = stmt.order_by(Food.name).limit(limit)
    return list((await session.execute(stmt)).scalars().all())


async def get_food(session: AsyncSession, food_id: int) -> Food | None:
    return (
        await session.execute(
            select(Food).options(selectinload(Food.portions)).where(Food.id == food_id)
        )
    ).scalar_one_or_none()


async def get_food_by_slug(session: AsyncSession, slug: str) -> Food | None:
    return (
        await session.execute(
            select(Food).options(selectinload(Food.portions)).where(Food.slug == slug)
        )
    ).scalar_one_or_none()


async def recent_foods(session: AsyncSession, limit: int) -> list[Food]:
    """Distinct catalog foods from recent meal items, most-recent first (quick-add)."""
    sub = (
        select(MealItem.food_id, func.max(Meal.ts).label("last"))
        .join(Meal, MealItem.meal_id == Meal.id)
        .where(MealItem.food_id.is_not(None))
        .group_by(MealItem.food_id)
        .order_by(func.max(Meal.ts).desc())
        .limit(limit)
    )
    rows = (await session.execute(sub)).all()
    order = {r.food_id: i for i, r in enumerate(rows)}
    if not order:
        return []
    foods = (
        await session.execute(
            select(Food).options(selectinload(Food.portions)).where(Food.id.in_(order))
        )
    ).scalars().all()
    return sorted(foods, key=lambda f: order[f.id])
