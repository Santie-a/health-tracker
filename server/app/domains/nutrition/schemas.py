"""Pydantic request/response models for nutrition (meals).

Phase 5 surface: manual meal entry (with macro resolution via nutrition_core),
photo meal entry (proxied to image-svc with manual fallback), and the daily view.
Serving/portion presets + per-item add endpoints come in Phase 7.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MealItemIn(BaseModel):
    food: str = Field(..., description="Food name; resolved against nutrition_core when macros omitted.")
    grams: float | None = Field(None, ge=0)
    # Explicit macros override resolution; omit them to estimate from food+grams.
    kcal: float | None = Field(None, ge=0)
    protein_g: float | None = Field(None, ge=0)
    carbs_g: float | None = Field(None, ge=0)
    fat_g: float | None = Field(None, ge=0)


class MealIn(BaseModel):
    ts: datetime = Field(..., description="When the meal was eaten (UTC ISO; naive assumed UTC).")
    name: str | None = None
    items: list[MealItemIn] = []


class MealItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    food: str
    food_id: int | None
    grams: float | None
    qty: float | None
    portion_label: str | None
    kcal: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    estimated: bool
    source: str | None


class Totals(BaseModel):
    kcal: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0


class MealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ts: datetime
    name: str | None
    photo_path: str | None
    source: str
    items: list[MealItemOut]


class MealCreateResponse(BaseModel):
    meal: MealOut
    # True when a photo meal degraded to manual entry (image-svc unreachable).
    degraded: bool = False
    note: str | None = None


class DayNutrition(BaseModel):
    date: date
    meals: list[MealOut]
    totals: Totals


# --- foods catalog & serving-based entry --------------------------------------

class FoodPortionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    label: str
    grams: float
    is_default: bool


class FoodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    aliases: list[str] | None
    kcal_100g: float | None
    protein_100g: float | None
    carbs_100g: float | None
    fat_100g: float | None
    default_grams: float | None
    portions: list[FoodPortionOut]


class FoodResolveOut(BaseModel):
    matched: bool
    query: str
    food: FoodOut | None = None


class MealItemAddIn(BaseModel):
    """Add an item by catalog food (food_id) with a portion×qty or grams, by
    free-text food + grams (matcher-resolved), or a raw kcal-only quick entry."""

    food_id: int | None = None
    food: str | None = None
    portion_label: str | None = None
    qty: float | None = Field(None, gt=0)
    grams: float | None = Field(None, ge=0)
    kcal: float | None = Field(None, ge=0)
    protein_g: float | None = Field(None, ge=0)
    carbs_g: float | None = Field(None, ge=0)
    fat_g: float | None = Field(None, ge=0)


class AddItemsIn(BaseModel):
    items: list[MealItemAddIn] = Field(..., min_length=1)


# --- edit (v1.1) --------------------------------------------------------------

class MealUpdate(BaseModel):
    """Partial meal edit. Only supplied fields are changed (PATCH semantics)."""

    ts: datetime | None = Field(None, description="When the meal was eaten (UTC ISO; naive assumed UTC).")
    name: str | None = None


class MealItemUpdate(BaseModel):
    """Partial item edit. Omitted fields are left untouched. When `grams` changes
    and macros aren't supplied, macros are re-estimated from the catalog/matcher."""

    food: str | None = None
    grams: float | None = Field(None, ge=0)
    qty: float | None = Field(None, gt=0)
    portion_label: str | None = None
    kcal: float | None = Field(None, ge=0)
    protein_g: float | None = Field(None, ge=0)
    carbs_g: float | None = Field(None, ge=0)
    fat_g: float | None = Field(None, ge=0)
