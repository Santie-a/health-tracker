"""Public API contract.

The gateway stores whatever this service returns, so this shape is stable:
improving the model later must not change it. New fields may be added, but
existing fields keep their meaning.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    food: str = Field(description="Identified food name (matched to the macro table).")
    grams_est: float = Field(ge=0, description="Estimated edible portion in grams.")
    kcal: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1, description="Model confidence for this item.")


class Totals(BaseModel):
    kcal: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)


class EstimateResponse(BaseModel):
    items: list[FoodItem]
    totals: Totals
    model_version: str = Field(description="Which model/backend produced this estimate.")
    table_version: str = Field(description="Which macro-table version was used.")


class HealthResponse(BaseModel):
    status: str = "ok"
    backend: str
    cuda_available: bool
    device_name: str | None = None
    model: str
    model_loaded: bool
