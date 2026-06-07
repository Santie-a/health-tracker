"""Samsung Health magic numbers and data-type identifiers.

All verified empirically against the real export (temp/data, 2026-06-07):
- Sleep stage codes confirmed by cross-checking summed per-stage minutes against
  the sleep file's own total_light_duration / total_rem_duration (near-exact).
- Swim = exercise_type 14001 (the only swimming-distance type present).
"""

from __future__ import annotations

# --- data-type identifiers (first cell of the metadata line 1) ----------------
DT_WEIGHT = "com.samsung.health.weight"
DT_SLEEP = "com.samsung.shealth.sleep"
DT_SLEEP_STAGE = "com.samsung.health.sleep_stage"
DT_STRESS = "com.samsung.shealth.stress"
DT_SPO2 = "com.samsung.shealth.tracker.oxygen_saturation"
DT_STEPS = "com.samsung.shealth.tracker.pedometer_day_summary"
DT_CALORIES = "com.samsung.shealth.calories_burned.details"
DT_HEART_RATE = "com.samsung.shealth.tracker.heart_rate"
DT_EXERCISE = "com.samsung.shealth.exercise"

# --- sleep stage code -> our column suffix ------------------------------------
SLEEP_STAGE = {
    "40001": "awake_min",
    "40002": "light_min",
    "40003": "deep_min",
    "40004": "rem_min",
}

# --- exercise types we import as swim sessions --------------------------------
SWIM_EXERCISE_TYPES = {"14001"}

# --- telemetry metric names + units -------------------------------------------
METRIC_STRESS = ("stress", "index")
METRIC_SPO2 = ("spo2", "%")
METRIC_STEPS = ("steps", "count")
METRIC_ENERGY = ("energy_expenditure", "kcal")
METRIC_HEART_RATE = ("heart_rate", "bpm")

SOURCE = "samsung_health"
