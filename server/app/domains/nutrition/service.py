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
from .foods_seed import slugify
from .schemas import (
    AddItemsIn,
    DayNutrition,
    FoodOut,
    FoodResolveOut,
    MealCreateResponse,
    MealIn,
    MealItemAddIn,
    MealItemIn,
    MealOut,
    Totals,
)


class BadItem(Exception):
    """Raised when an add-item payload can't be resolved (maps to 400)."""


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


# --- foods catalog & serving-based entry -------------------------------------

async def search_foods(session: AsyncSession, q: str | None, limit: int) -> list[FoodOut]:
    rows = await repository.search_foods(session, q, limit)
    return [FoodOut.model_validate(r) for r in rows]


async def recent_foods(session: AsyncSession, limit: int) -> list[FoodOut]:
    rows = await repository.recent_foods(session, limit)
    return [FoodOut.model_validate(r) for r in rows]


async def resolve_food(session: AsyncSession, name: str, table: MacroTable) -> FoodResolveOut:
    """Best-effort: resolve a typed name via the shared matcher, then map the
    canonical macro name to a catalog Food (same source, so the slug lines up)."""
    row = table.lookup(name)
    if row is None:
        return FoodResolveOut(matched=False, query=name)
    food = await repository.get_food_by_slug(session, slugify(row.name))
    return FoodResolveOut(matched=food is not None, query=name,
                          food=FoodOut.model_validate(food) if food else None)


async def _build_added_item(session: AsyncSession, item: MealItemAddIn, table: MacroTable) -> MealItem:
    kcal, protein, carbs, fat = item.kcal, item.protein_g, item.carbs_g, item.fat_g
    grams = item.grams
    estimated = False

    if item.food_id is not None:
        food = await repository.get_food(session, item.food_id)
        if food is None:
            raise BadItem(f"food_id {item.food_id} not found")
        # Resolve grams from a portion preset or qty × default serving.
        if grams is None and item.portion_label is not None:
            portion = next((p for p in food.portions if p.label == item.portion_label), None)
            if portion is None:
                raise BadItem(f"portion '{item.portion_label}' not found for {food.name}")
            grams = float(portion.grams) * (item.qty or 1)
            estimated = True
        elif grams is None and item.qty is not None and food.default_grams is not None:
            grams = float(food.default_grams) * item.qty
            estimated = True
        # Compute macros from per-100g unless explicitly provided.
        if kcal is None and grams is not None:
            factor = grams / 100.0
            kcal = round(float(food.kcal_100g or 0) * factor, 1)
            protein = round(float(food.protein_100g or 0) * factor, 1)
            carbs = round(float(food.carbs_100g or 0) * factor, 1)
            fat = round(float(food.fat_100g or 0) * factor, 1)
            estimated = True
        return MealItem(
            food=item.food or food.name, food_id=food.id, grams=grams, qty=item.qty,
            portion_label=item.portion_label, kcal=kcal, protein_g=protein, carbs_g=carbs,
            fat_g=fat, estimated=estimated, source="estimate" if estimated else "manual",
        )

    # Free-text path: need a name or a raw kcal value.
    if not item.food and kcal is None:
        raise BadItem("item needs food_id, food, or kcal")
    if kcal is None and grams is not None and item.food:
        row = table.lookup(item.food)
        if row is not None:
            kcal, protein, carbs, fat = row.scale(grams)
            estimated = True
    return MealItem(
        food=item.food or "item", grams=grams, qty=item.qty, portion_label=item.portion_label,
        kcal=kcal, protein_g=protein, carbs_g=carbs, fat_g=fat,
        estimated=estimated, source="estimate" if estimated else "manual",
    )


async def add_items(
    session: AsyncSession, meal_id: int, payload: AddItemsIn, table: MacroTable
) -> MealOut | None:
    meal = await repository.get(session, meal_id)
    if meal is None:
        return None
    for item in payload.items:
        meal.items.append(await _build_added_item(session, item, table))
    await session.flush()
    return MealOut.model_validate(meal)


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
