"""Tunable thresholds for the recommendation rules — kept in one place so they're
easy to adjust without touching rule logic (server/TODO.md)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    # recovery
    low_sleep_min: int = 360       # < 6h sleep flags a deload
    high_stress: float = 70.0      # daily avg stress index above this flags recovery

    # protein
    protein_g_per_kg: float = 1.6  # target g protein per kg bodyweight on training days
    default_protein_g: float = 120.0  # fallback target when bodyweight is unknown

    # calorie balance
    calorie_goal: float | None = None   # optional fixed goal when TDEE telemetry is absent
    calorie_tolerance: float = 200.0    # |intake - reference| within this = "balanced"

    # training balance (weekly, from strength stats)
    imbalance_low: float = 0.5   # ratio below this = under-trained side
    imbalance_high: float = 2.0  # ratio above this = over-trained side

    # goal progress
    progress_kcal_bump: int = 150          # daily kcal nudge when a body goal stalls
    sleep_goal_tolerance_min: float = 30.0  # within this of the sleep goal = "met"


DEFAULT = Thresholds()
