"""Deterministic placeholder estimator.

No model, no GPU. Picks a stable pseudo-meal from the macro table keyed on the
image bytes, so the gateway/frontend can integrate against the real response
shape before the vision-LLM is wired. Confidence is capped low to make clear
these numbers are not real detections.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from ..config import Settings
from nutrition_core import MacroTable
from .base import Detection, FoodEstimator

if TYPE_CHECKING:
    from PIL.Image import Image

# Plausible portion sizes (g) to cycle through deterministically.
_PORTIONS = (120.0, 150.0, 180.0, 200.0, 80.0, 100.0)


class StubEstimator(FoodEstimator):
    name = "stub"

    def __init__(self, settings: Settings, table: MacroTable):
        self._settings = settings
        self.table = table
        self._names = table.names

    def detect(self, image: "Image") -> list[Detection]:
        # Hash the pixels so the same photo always yields the same fake meal.
        digest = hashlib.sha256(image.tobytes()).digest()
        n_items = 1 + (digest[0] % 3)  # 1..3 items
        detections: list[Detection] = []
        seen: set[str] = set()
        for k in range(n_items):
            name = self._names[digest[k + 1] % len(self._names)]
            if name in seen:
                continue
            seen.add(name)
            grams = _PORTIONS[digest[k + 4] % len(_PORTIONS)]
            confidence = 0.2 + (digest[k + 7] % 20) / 100.0  # 0.20..0.39
            detections.append(Detection(food=name, grams_est=grams, confidence=confidence))
        return detections
