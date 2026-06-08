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
    grams: float | None
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
