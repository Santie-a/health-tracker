"""Nutrition business logic: macro resolution, totals, manual + photo meals.

Manual entry resolves food names through the shared nutrition_core matcher (same
table image-svc uses), so a typed "rice" and a photographed "rice" land on the
same macros. The photo path proxies to image-svc and degrades to an empty manual
meal when the GPU box is unreachable — never an error.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

from nutrition_core import MacroTable
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.integrations import image_svc

from . import repository
from .models import Meal, MealItem
from .schemas import (
    DayNutrition,
    MealCreateResponse,
    MealIn,
    MealItemIn,
    MealOut,
    Totals,
)


def _as_utc(ts: datetime) -> datetime:
    return ts if ts.tzinfo is not None else ts.replace(tzinfo=timezone.utc)


def resolve_item(item: MealItemIn, table: MacroTable) -> MealItem:
    """Build a MealItem, estimating macros from food+grams via the shared matcher
    when explicit macros aren't supplied."""
    kcal, protein, carbs, fat = item.kcal, item.protein_g, item.carbs_g, item.fat_g
    estimated = False
    if kcal is None and item.grams is not None:
        row = table.lookup(item.food)
        if row is not None:
            kcal, protein, carbs, fat = row.scale(item.grams)
            estimated = True
    return MealItem(
        food=item.food,
        grams=item.grams,
        kcal=kcal,
        protein_g=protein,
        carbs_g=carbs,
        fat_g=fat,
        estimated=estimated,
        source="manual",
    )


def compute_totals(items: list[MealItem]) -> Totals:
    t = Totals()
    for it in items:
        t.kcal += float(it.kcal or 0)
        t.protein_g += float(it.protein_g or 0)
        t.carbs_g += float(it.carbs_g or 0)
        t.fat_g += float(it.fat_g or 0)
    # round for a clean API surface
    return Totals(
        kcal=round(t.kcal, 1),
        protein_g=round(t.protein_g, 1),
        carbs_g=round(t.carbs_g, 1),
        fat_g=round(t.fat_g, 1),
    )


async def create_manual_meal(session: AsyncSession, payload: MealIn, table: MacroTable) -> MealOut:
    # Pass items into the constructor so the relationship is a loaded collection —
    # otherwise serializing a meal with zero items lazy-loads under async (errors).
    items = [resolve_item(item, table) for item in payload.items]
    meal = Meal(ts=_as_utc(payload.ts), name=payload.name, source="manual", items=items)
    await repository.add(session, meal)
    return MealOut.model_validate(meal)


async def create_photo_meal(
    session: AsyncSession,
    settings: Settings,
    image: bytes,
    filename: str,
    content_type: str | None,
    name: str | None,
    ts: datetime,
) -> MealCreateResponse:
    result = await image_svc.estimate(settings, image, filename, content_type)

    if not result.ok:
        # Degrade, don't fail: create an empty manual meal to add items to by hand.
        meal = Meal(ts=_as_utc(ts), name=name, source="manual", items=[])
        await repository.add(session, meal)
        return MealCreateResponse(
            meal=MealOut.model_validate(meal),
            degraded=True,
            note=f"image service unavailable ({result.error}); add items manually.",
        )

    items = [
        MealItem(
            food=it["food"],
            grams=it.get("grams"),
            kcal=it.get("kcal"),
            protein_g=it.get("protein_g"),
            carbs_g=it.get("carbs_g"),
            fat_g=it.get("fat_g"),
            estimated=True,  # grams are a model estimate
            source="image",
        )
        for it in result.items
    ]
    meal = Meal(ts=_as_utc(ts), name=name, source="image", items=items)
    await repository.add(session, meal)
    return MealCreateResponse(meal=MealOut.model_validate(meal), degraded=False)


async def get_day(session: AsyncSession, day) -> DayNutrition:
    start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    meals = await repository.list_in_range(session, start, end)
    all_items = [it for m in meals for it in m.items]
    return DayNutrition(
        date=day,
        meals=[MealOut.model_validate(m) for m in meals],
        totals=compute_totals(all_items),
    )
