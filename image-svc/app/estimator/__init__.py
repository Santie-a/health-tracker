"""Pluggable food estimators.

A backend only has to identify foods and rough portions (``Detection``s);
mapping those to macros is shared (``build_estimate``) so the response shape
stays identical across backends.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..config import Settings
from .base import Detection, FoodEstimator, build_estimate

if TYPE_CHECKING:
    from nutrition_core import MacroTable

__all__ = ["Detection", "FoodEstimator", "build_estimate", "make_estimator"]


def make_estimator(settings: Settings, table: "MacroTable") -> FoodEstimator:
    if settings.backend == "vlm":
        from .vlm import VLMEstimator

        return VLMEstimator(settings, table)
    from .stub import StubEstimator

    return StubEstimator(settings, table)
