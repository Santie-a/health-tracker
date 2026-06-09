"""Estimator interface + the shared detection->macros assembler."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..schemas import EstimateResponse, FoodItem, Totals

if TYPE_CHECKING:  # avoid importing Pillow at module load
    from PIL.Image import Image

    from nutrition_core import MacroTable


@dataclass(frozen=True)
class Detection:
    """What a backend reports for one food on the plate."""

    food: str
    grams_est: float
    confidence: float


class FoodEstimator(ABC):
    """Identify foods + rough portions from a single plate photo."""

    #: Human-readable backend id, surfaced on /health.
    name: str = "base"

    @property
    def loaded(self) -> bool:
        """Whether the underlying model is resident (always True for stub)."""
        return True

    def warmup(self) -> None:
        """Optionally load the model ahead of the first request."""

    @abstractmethod
    def detect(self, image: "Image") -> list[Detection]:
        ...


def build_estimate(
    detections: list[Detection],
    table: "MacroTable",
    *,
    model_version: str,
    table_version: str,
) -> EstimateResponse:
    """Map raw detections through the macro table into the public response.

    Unknown foods are kept (so nothing silently vanishes) with zero macros and
    their name suffixed ``(unmatched)`` to signal the gateway/UI to prompt for a
    manual correction.
    """
    items: list[FoodItem] = []
    for det in detections:
        row = table.lookup(det.food)
        if row is None:
            items.append(
                FoodItem(
                    food=f"{det.food} (unmatched)",
                    grams_est=round(det.grams_est, 1),
                    kcal=0.0,
                    protein_g=0.0,
                    carbs_g=0.0,
                    fat_g=0.0,
                    confidence=min(det.confidence, 0.3),
                )
            )
            continue
        kcal, protein, carbs, fat = row.scale(det.grams_est)
        items.append(
            FoodItem(
                food=row.name,
                grams_est=round(det.grams_est, 1),
                kcal=kcal,
                protein_g=protein,
                carbs_g=carbs,
                fat_g=fat,
                confidence=round(det.confidence, 2),
            )
        )

    totals = Totals(
        kcal=round(sum(i.kcal for i in items), 1),
        protein_g=round(sum(i.protein_g for i in items), 1),
        carbs_g=round(sum(i.carbs_g for i in items), 1),
        fat_g=round(sum(i.fat_g for i in items), 1),
    )
    return EstimateResponse(
        items=items,
        totals=totals,
        model_version=model_version,
        table_version=table_version,
    )
