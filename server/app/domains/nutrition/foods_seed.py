"""Seed the foods + food_portions catalog from the shared nutrition_core CSV.

Single source of truth: the same per-100g table the matcher uses, stamped with the
same TABLE_VERSION, so image and manual paths agree. Portion presets aren't in the
CSV, so a small curated set is added for common foods (by slug, skipped if absent).
"""

from __future__ import annotations

import csv

import nutrition_core
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Food, FoodPortion


def slugify(name: str) -> str:
    return name.lower().replace("-", " ").replace("'", "").strip().replace(" ", "_")


# Curated portion presets keyed by food slug: (label, grams, is_default).
PORTIONS: dict[str, list[tuple[str, float, bool]]] = {
    "rice": [("1 cup cooked", 158, True)],
    "white_rice": [("1 cup cooked", 158, True)],
    "brown_rice": [("1 cup cooked", 195, True)],
    "bread": [("1 slice", 28, True)],
    "banana": [("1 medium", 118, True)],
    "egg": [("1 large", 50, True)],
    "chicken_breast": [("1 fillet", 174, True), ("100 g", 100, False)],
    "oats": [("1 cup cooked", 234, True), ("1/2 cup dry", 40, False)],
    "milk": [("1 cup", 244, True)],
    "peanut_butter": [("1 tbsp", 16, True)],
    # Colombian staples — "1 unidad" (one piece) presets for finger foods.
    "arepa": [("1 unidad", 80, True)],
    "arepa_de_huevo": [("1 unidad", 120, True)],
    "arepa_de_queso": [("1 unidad", 90, True)],
    "empanada": [("1 unidad", 45, True)],
    "patacon": [("1 unidad", 50, True)],
    "platano_maduro": [("1 tajada", 60, True)],
    "bunuelo": [("1 unidad", 40, True)],
    "pandebono": [("1 unidad", 50, True)],
    "pan_de_yuca": [("1 unidad", 45, True)],
    "almojabana": [("1 unidad", 70, True)],
    "tamal": [("1 unidad", 250, True)],
    "oblea": [("1 unidad", 60, True)],
    "bocadillo": [("1 unidad", 25, True)],
}


async def seed_foods(session: AsyncSession) -> int:
    """Insert foods missing by slug from the CSV. Returns how many were added."""
    version = nutrition_core.TABLE_VERSION
    existing = set((await session.execute(select(Food.slug))).scalars().all())

    added = 0
    with nutrition_core.default_macro_csv().open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            name = raw["name"].strip()
            slug = slugify(name)
            if not name or slug in existing:
                continue
            aliases = [a.strip() for a in (raw.get("aliases") or "").split(";") if a.strip()]
            portions = [
                FoodPortion(label=lbl, grams=g, is_default=d)
                for lbl, g, d in PORTIONS.get(slug, [])
            ]
            session.add(
                Food(
                    name=name,
                    slug=slug,
                    aliases=aliases or None,
                    kcal_100g=float(raw["kcal"]),
                    protein_100g=float(raw["protein_g"]),
                    carbs_100g=float(raw["carbs_g"]),
                    fat_100g=float(raw["fat_g"]),
                    default_grams=(portions[0].grams if portions else None),
                    table_version=version,
                    portions=portions,
                )
            )
            existing.add(slug)
            added += 1
    if added:
        await session.flush()
    return added
