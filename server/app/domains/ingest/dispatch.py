"""Map a Samsung data-type identifier to its parser. Returns None for files we
deliberately don't ingest (sleep_stage is handled separately as enrichment)."""

from __future__ import annotations

from .samsung import codes, parsers
from .samsung.parsers import ParseResult

_DISPATCH = {
    codes.DT_WEIGHT: parsers.parse_weight,
    codes.DT_STRESS: parsers.parse_stress,
    codes.DT_SPO2: parsers.parse_spo2,
    codes.DT_STEPS: parsers.parse_steps,
    codes.DT_CALORIES: parsers.parse_calories,
    codes.DT_HEART_RATE: parsers.parse_heart_rate,
    codes.DT_EXERCISE: parsers.parse_swims,
}


def parse(data_type: str, data: bytes, stage_map: dict) -> ParseResult | None:
    if data_type == codes.DT_SLEEP:
        return parsers.parse_sleep(data, stage_map)
    fn = _DISPATCH.get(data_type)
    return fn(data) if fn else None
