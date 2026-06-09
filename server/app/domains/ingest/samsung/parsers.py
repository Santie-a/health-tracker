"""Per-data-type parsers (tasks 3.2.1–3.2.8).

Each parser turns raw CSV bytes into upsert-ready row dicts + a ParseStats, and is
row-resilient: a malformed row is skipped and counted, never aborting the file.
Column names are the real line-2 headers from the export (see SAMSUNG_FILES.md).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from . import codes
from .reader import (
    ParseStats,
    iter_rows,
    parse_epoch_ms,
    parse_local_ts,
    to_float,
    to_int,
)

# Column-name prefixes for the files that namespace their headers.
_SLEEP = "com.samsung.health.sleep."
_SPO2 = "com.samsung.health.oxygen_saturation."
_CAL = "com.samsung.shealth.calories_burned."
_HR = "com.samsung.health.heart_rate."
_EX = "com.samsung.health.exercise."


@dataclass
class ParseResult:
    kind: str  # 'telemetry' | 'body_composition' | 'sleep' | 'training_swim'
    rows: list[dict]
    stats: ParseStats


# --- 3.2.1 weight -> body_composition ----------------------------------------

def parse_weight(data: bytes) -> ParseResult:
    stats = ParseStats()
    rows: list[dict] = []
    for line, r in iter_rows(data):
        try:
            ts = parse_local_ts(r["start_time"], r["time_offset"])
        except Exception as exc:
            stats.skip(line, str(exc))
            continue
        rows.append(
            {
                "ts": ts,
                "weight_kg": to_float(r.get("weight")),
                "body_fat_pct": to_float(r.get("body_fat")),
                "skeletal_muscle_kg": to_float(r.get("skeletal_muscle_mass")),
                "bmr_kcal": to_int(r.get("basal_metabolic_rate")),
            }
        )
        stats.ok += 1
    return ParseResult("body_composition", rows, stats)


# --- 3.2.2 sleep stage enrichment + sleep sessions ---------------------------

def parse_sleep_stage(data: bytes) -> dict[str, dict[str, int]]:
    """Return {sleep_id: {deep_min, rem_min, light_min, awake_min}} by summing
    per-stage segment minutes. Stage codes verified empirically (codes.py)."""
    acc: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for _line, r in iter_rows(data):
        col = codes.SLEEP_STAGE.get((r.get("stage") or "").strip())
        if col is None:
            continue
        try:
            start = parse_local_ts(r["start_time"], r["time_offset"])
            end = parse_local_ts(r["end_time"], r["time_offset"])
        except Exception:
            continue
        acc[r["sleep_id"]][col] += (end - start).total_seconds() / 60.0
    return {sid: {c: int(round(v)) for c, v in d.items()} for sid, d in acc.items()}


def parse_sleep(data: bytes, stage_map: dict[str, dict[str, int]] | None = None) -> ParseResult:
    stage_map = stage_map or {}
    stats = ParseStats()
    rows: list[dict] = []
    for line, r in iter_rows(data):
        try:
            offset = r[_SLEEP + "time_offset"]
            start_ts = parse_local_ts(r[_SLEEP + "start_time"], offset)
            end_ts = parse_local_ts(r[_SLEEP + "end_time"], offset)
        except Exception as exc:
            stats.skip(line, str(exc))
            continue

        # Bare columns give rem/light for older nights; stage enrichment (when the
        # sleep_stage file was uploaded) gives all four and takes precedence.
        rem = to_int(r.get("total_rem_duration"))
        light = to_int(r.get("total_light_duration"))
        deep = awake = None
        stages = stage_map.get(r.get(_SLEEP + "datauuid", ""))
        if stages:
            deep = stages.get("deep_min")
            awake = stages.get("awake_min")
            light = stages.get("light_min", light)
            rem = stages.get("rem_min", rem)

        rows.append(
            {
                "start_ts": start_ts,
                "end_ts": end_ts,
                "total_min": to_int(r.get("sleep_duration")),
                "deep_min": deep,
                "rem_min": rem,
                "light_min": light,
                "awake_min": awake,
                "efficiency": to_float(r.get("efficiency")),
            }
        )
        stats.ok += 1
    return ParseResult("sleep", rows, stats)


# --- 3.2.3–3.2.7 telemetry ----------------------------------------------------

def _telemetry_point(ts, metric, unit, value) -> dict:
    return {"ts": ts, "metric": metric, "value": value, "unit": unit, "source": codes.SOURCE}


def parse_stress(data: bytes) -> ParseResult:
    metric, unit = codes.METRIC_STRESS
    stats = ParseStats()
    rows: list[dict] = []
    for line, r in iter_rows(data):
        value = to_float(r.get("score"))
        if value is None:
            stats.skip(line, "missing score")
            continue
        try:
            ts = parse_local_ts(r["start_time"], r["time_offset"])
        except Exception as exc:
            stats.skip(line, str(exc))
            continue
        rows.append(_telemetry_point(ts, metric, unit, value))
        stats.ok += 1
    return ParseResult("telemetry", rows, stats)


def parse_spo2(data: bytes) -> ParseResult:
    metric, unit = codes.METRIC_SPO2
    stats = ParseStats()
    rows: list[dict] = []
    for line, r in iter_rows(data):
        value = to_float(r.get(_SPO2 + "spo2"))
        if value is None or value <= 0:
            stats.skip(line, "missing/invalid spo2")
            continue
        try:
            ts = parse_local_ts(r[_SPO2 + "start_time"], r[_SPO2 + "time_offset"])
        except Exception as exc:
            stats.skip(line, str(exc))
            continue
        rows.append(_telemetry_point(ts, metric, unit, value))
        stats.ok += 1
    return ParseResult("telemetry", rows, stats)


def parse_heart_rate(data: bytes) -> ParseResult:
    metric, unit = codes.METRIC_HEART_RATE
    stats = ParseStats()
    rows: list[dict] = []
    for line, r in iter_rows(data):
        value = to_float(r.get(_HR + "heart_rate"))
        if value is None or value <= 0:
            stats.skip(line, "missing/invalid heart_rate")
            continue
        try:
            ts = parse_local_ts(r[_HR + "start_time"], r[_HR + "time_offset"])
        except Exception as exc:
            stats.skip(line, str(exc))
            continue
        rows.append(_telemetry_point(ts, metric, unit, value))
        stats.ok += 1
    return ParseResult("telemetry", rows, stats)


def _parse_daily_telemetry(data, *, ts_col, value_fn, metric, unit) -> ParseResult:
    """Daily-summary metrics (steps, energy): multiple device rows per day_time —
    aggregate to ONE row per day taking the MAX (avoids double-counting phone +
    watch, which both tally the same activity)."""
    stats = ParseStats()
    per_day: dict = {}
    for line, r in iter_rows(data):
        try:
            ts = parse_epoch_ms(r[ts_col])
        except Exception as exc:
            stats.skip(line, str(exc))
            continue
        value = value_fn(r)
        if value is None:
            stats.skip(line, "missing value")
            continue
        if ts not in per_day or value > per_day[ts]:
            per_day[ts] = value
    rows = [_telemetry_point(ts, metric, unit, v) for ts, v in per_day.items()]
    stats.ok = len(rows)
    return ParseResult("telemetry", rows, stats)


def parse_steps(data: bytes) -> ParseResult:
    metric, unit = codes.METRIC_STEPS
    return _parse_daily_telemetry(
        data, ts_col="day_time", value_fn=lambda r: to_float(r.get("step_count")),
        metric=metric, unit=unit,
    )


def parse_calories(data: bytes) -> ParseResult:
    metric, unit = codes.METRIC_ENERGY

    def total_kcal(r: dict) -> float | None:
        rest = to_float(r.get(_CAL + "rest_calorie"))
        active = to_float(r.get(_CAL + "active_calorie"))
        if rest is None and active is None:
            return None
        return (rest or 0.0) + (active or 0.0)

    return _parse_daily_telemetry(
        data, ts_col=_CAL + "day_time", value_fn=total_kcal, metric=metric, unit=unit,
    )


# --- 3.2.8 exercise -> training_sessions (swim only) -------------------------

def parse_swims(data: bytes) -> ParseResult:
    stats = ParseStats()
    rows: list[dict] = []
    for line, r in iter_rows(data):
        if (r.get(_EX + "exercise_type") or "").strip() not in codes.SWIM_EXERCISE_TYPES:
            continue  # not a swim — silently ignored, not a skip/error
        try:
            ts = parse_local_ts(r[_EX + "start_time"], r[_EX + "time_offset"])
        except Exception as exc:
            stats.skip(line, str(exc))
            continue
        dur_ms = to_float(r.get(_EX + "duration"))
        rows.append(
            {
                "ts": ts,
                "type": "swim",
                "duration_min": int(round(dur_ms / 60000)) if dur_ms else None,
                "kcal": to_float(r.get(_EX + "calorie")),
                "avg_hr": to_int(r.get(_EX + "mean_heart_rate")),
                "max_hr": to_int(r.get(_EX + "max_heart_rate")),
                "distance_m": to_float(r.get(_EX + "distance")),
                "source": codes.SOURCE,
            }
        )
        stats.ok += 1
    return ParseResult("training_swim", rows, stats)
