"""Pydantic models for the recommendations API."""

from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    code: str
    category: str
    severity: str
    title: str
    detail: str
    signals: list[str] = []


class RecommendationsOut(BaseModel):
    date: date_cls
    generated_at: datetime | None = None
    recommendations: list[RecommendationItem]
    context: dict | None = None


class FeedbackIn(BaseModel):
    date: date_cls
    feedback: str
