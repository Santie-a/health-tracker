"""Response model for the aggregated day view. Reuses each domain's own schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.domains.nutrition.schemas import MealOut, Totals
from app.domains.recommendations.schemas import RecommendationItem
from app.domains.telemetry.schemas import SleepSummary
from app.domains.training.schemas import TrainingSessionOut


class TelemetrySummary(BaseModel):
    steps: float | None = None
    avg_stress: float | None = None
    avg_heart_rate: float | None = None
    avg_spo2: float | None = None
    energy_expenditure: float | None = None
    sleep: SleepSummary | None = None


class DashboardOut(BaseModel):
    date: date
    telemetry: TelemetrySummary
    training: list[TrainingSessionOut]
    nutrition_totals: Totals
    meals: list[MealOut]
    recommendations: list[RecommendationItem]
