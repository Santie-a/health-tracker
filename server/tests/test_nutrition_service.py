"""DB-free tests for nutrition logic: macro resolution, totals, image-svc mapping."""

from __future__ import annotations

import pytest
from nutrition_core import MacroTable, default_macro_csv

from app.domains.nutrition.schemas import MealItemIn
from app.domains.nutrition.service import compute_totals, resolve_item
from app.integrations import image_svc
from app.core.config import Settings


@pytest.fixture(scope="module")
def table() -> MacroTable:
    return MacroTable.from_csv(default_macro_csv())


def test_resolve_item_estimates_from_food_and_grams(table):
    item = MealItemIn(food="chicken breast", grams=200)
    mi = resolve_item(item, table)
    assert mi.estimated is True
    assert mi.source == "manual"
    assert mi.kcal and mi.kcal > 0
    assert mi.protein_g and mi.protein_g > 0


def test_explicit_macros_are_not_overridden(table):
    item = MealItemIn(food="mystery shake", grams=100, kcal=250, protein_g=30, carbs_g=10, fat_g=5)
    mi = resolve_item(item, table)
    assert mi.estimated is False
    assert (mi.kcal, mi.protein_g) == (250, 30)


def test_unresolvable_food_left_without_macros(table):
    item = MealItemIn(food="zzz-not-a-real-food", grams=100)
    mi = resolve_item(item, table)
    assert mi.estimated is False
    assert mi.kcal is None


def test_compute_totals_sums_and_skips_none(table):
    items = [resolve_item(MealItemIn(food="chicken breast", grams=100), table),
             resolve_item(MealItemIn(food="zzz", grams=100), table)]  # second has no macros
    totals = compute_totals(items)
    assert totals.kcal > 0
    assert totals.protein_g > 0


def test_image_svc_map_items_renames_grams_est():
    data = {"items": [{"food": "rice", "grams_est": 150, "kcal": 195, "protein_g": 4,
                       "carbs_g": 42, "fat_g": 0.4, "confidence": 0.8}]}
    mapped = image_svc.map_items(data)
    assert mapped[0]["food"] == "rice"
    assert mapped[0]["grams"] == 150
    assert "grams_est" not in mapped[0]


@pytest.mark.asyncio
async def test_estimate_returns_not_ok_when_unconfigured():
    settings = Settings(image_svc_url="")
    res = await image_svc.estimate(settings, b"\x89PNG", "x.png", "image/png")
    assert res.ok is False
    assert res.error
