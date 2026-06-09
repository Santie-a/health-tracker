"""Parser + reader unit tests (no DB). Small inline CSVs mirroring the real
export layout (metadata line 1, header line 2). Column names and stage codes are
the ones verified against the real export."""

from __future__ import annotations

from datetime import datetime, timezone

from app.domains.ingest.samsung import parsers
from app.domains.ingest.samsung.reader import (
    parse_epoch_ms,
    parse_local_ts,
    parse_offset,
    peek_data_type,
)


def _csv(data_type: str, header: list[str], rows: list[list[str]]) -> bytes:
    lines = [f"{data_type},6320001,{len(header)}", ",".join(header)]
    lines += [",".join(r) for r in rows]
    return ("\r\n".join(lines) + "\r\n").encode("utf-8-sig")


# --- reader -------------------------------------------------------------------

def test_peek_data_type_reads_metadata_line():
    data = _csv("com.samsung.shealth.stress", ["start_time"], [["x"]])
    assert peek_data_type(data) == "com.samsung.shealth.stress"


def test_parse_offset():
    assert parse_offset("UTC-0500").total_seconds() == -5 * 3600
    assert parse_offset("UTC+0000").total_seconds() == 0
    assert parse_offset("UTC+0530").total_seconds() == 5.5 * 3600


def test_parse_local_ts_converts_to_utc():
    # 06:00 at UTC-0500 -> 11:00 UTC
    ts = parse_local_ts("2024-01-02 06:00:00.000", "UTC-0500")
    assert ts == datetime(2024, 1, 2, 11, 0, tzinfo=timezone.utc)


def test_parse_epoch_ms():
    assert parse_epoch_ms("1704171600000") == datetime.fromtimestamp(1704171600, tz=timezone.utc)


# --- weight -------------------------------------------------------------------

def test_parse_weight():
    data = _csv(
        "com.samsung.health.weight",
        ["start_time", "time_offset", "weight", "body_fat", "skeletal_muscle_mass", "basal_metabolic_rate"],
        [["2024-01-02 06:00:00.000", "UTC-0500", "80.5", "18.2", "35.1", "1700"]],
    )
    res = parsers.parse_weight(data)
    assert res.kind == "body_composition"
    assert res.stats.ok == 1
    row = res.rows[0]
    assert row["weight_kg"] == 80.5
    assert row["body_fat_pct"] == 18.2
    assert row["skeletal_muscle_kg"] == 35.1
    assert row["bmr_kcal"] == 1700
    assert row["ts"] == datetime(2024, 1, 2, 11, 0, tzinfo=timezone.utc)


# --- sleep + stage enrichment -------------------------------------------------

_STAGE_HEADER = ["start_time", "end_time", "sleep_id", "stage", "time_offset"]


def _stage_rows():
    o = "UTC-0500"
    return _csv(
        "com.samsung.health.sleep_stage",
        _STAGE_HEADER,
        [
            ["2024-01-02 00:00:00.000", "2024-01-02 01:00:00.000", "SID1", "40002", o],  # light 60
            ["2024-01-02 01:00:00.000", "2024-01-02 01:30:00.000", "SID1", "40003", o],  # deep 30
            ["2024-01-02 01:30:00.000", "2024-01-02 02:00:00.000", "SID1", "40004", o],  # rem 30
            ["2024-01-02 02:00:00.000", "2024-01-02 02:10:00.000", "SID1", "40001", o],  # awake 10
        ],
    )


def test_parse_sleep_stage_aggregates_by_code():
    m = parsers.parse_sleep_stage(_stage_rows())
    assert m["SID1"] == {"light_min": 60, "deep_min": 30, "rem_min": 30, "awake_min": 10}


def test_parse_sleep_uses_stage_enrichment_over_bare_columns():
    P = "com.samsung.health.sleep."
    data = _csv(
        "com.samsung.shealth.sleep",
        [P + "start_time", P + "end_time", P + "time_offset", P + "datauuid",
         "efficiency", "sleep_duration", "total_rem_duration", "total_light_duration"],
        [["2024-01-01 23:00:00.000", "2024-01-02 07:00:00.000", "UTC-0500", "SID1",
          "90", "130", "20", "50"]],
    )
    stage_map = parsers.parse_sleep_stage(_stage_rows())
    res = parsers.parse_sleep(data, stage_map)
    row = res.rows[0]
    assert row["total_min"] == 130
    assert row["efficiency"] == 90.0
    # stage-derived values win over the bare rem/light columns
    assert row["deep_min"] == 30
    assert row["awake_min"] == 10
    assert row["light_min"] == 60
    assert row["rem_min"] == 30


def test_parse_sleep_without_stages_falls_back_to_bare_columns():
    P = "com.samsung.health.sleep."
    data = _csv(
        "com.samsung.shealth.sleep",
        [P + "start_time", P + "end_time", P + "time_offset", P + "datauuid",
         "efficiency", "sleep_duration", "total_rem_duration", "total_light_duration"],
        [["2024-01-01 23:00:00.000", "2024-01-02 07:00:00.000", "UTC-0500", "NOSTAGE",
          "88", "120", "22", "70"]],
    )
    row = parsers.parse_sleep(data, {}).rows[0]
    assert row["rem_min"] == 22
    assert row["light_min"] == 70
    assert row["deep_min"] is None
    assert row["awake_min"] is None


# --- telemetry ----------------------------------------------------------------

def test_parse_stress():
    data = _csv("com.samsung.shealth.stress", ["start_time", "time_offset", "score"],
                [["2024-01-02 06:00:00.000", "UTC-0500", "42"]])
    res = parsers.parse_stress(data)
    assert res.kind == "telemetry"
    assert res.rows[0]["metric"] == "stress"
    assert res.rows[0]["value"] == 42.0
    assert res.rows[0]["unit"] == "index"


def test_parse_spo2_skips_invalid():
    P = "com.samsung.health.oxygen_saturation."
    data = _csv("com.samsung.shealth.tracker.oxygen_saturation",
                [P + "start_time", P + "time_offset", P + "spo2"],
                [["2024-01-02 06:00:00.000", "UTC-0500", "96"],
                 ["2024-01-02 07:00:00.000", "UTC-0500", "0"]])
    res = parsers.parse_spo2(data)
    assert res.stats.ok == 1
    assert res.stats.skipped == 1
    assert res.rows[0]["value"] == 96.0


def test_parse_steps_dedupes_per_day_taking_max():
    # two device rows for the same day_time -> one row, max value (no double count)
    data = _csv("com.samsung.shealth.tracker.pedometer_day_summary",
                ["day_time", "step_count"],
                [["1704171600000", "100"], ["1704171600000", "250"]])
    res = parsers.parse_steps(data)
    assert len(res.rows) == 1
    assert res.rows[0]["value"] == 250.0
    assert res.rows[0]["metric"] == "steps"


def test_parse_calories_sums_rest_and_active():
    P = "com.samsung.shealth.calories_burned."
    data = _csv("com.samsung.shealth.calories_burned.details",
                [P + "day_time", P + "rest_calorie", P + "active_calorie"],
                [["1704171600000", "1400", "200"]])
    res = parsers.parse_calories(data)
    assert res.rows[0]["value"] == 1600.0
    assert res.rows[0]["metric"] == "energy_expenditure"


def test_parse_heart_rate():
    P = "com.samsung.health.heart_rate."
    data = _csv("com.samsung.shealth.tracker.heart_rate",
                [P + "start_time", P + "time_offset", P + "heart_rate"],
                [["2024-01-02 06:00:00.000", "UTC-0500", "71"]])
    res = parsers.parse_heart_rate(data)
    assert res.rows[0]["value"] == 71.0
    assert res.rows[0]["unit"] == "bpm"


# --- swims --------------------------------------------------------------------

def test_parse_swims_filters_to_swim_type_only():
    P = "com.samsung.health.exercise."
    data = _csv(
        "com.samsung.shealth.exercise",
        [P + "start_time", P + "time_offset", P + "exercise_type", P + "duration",
         P + "calorie", P + "mean_heart_rate", P + "max_heart_rate", P + "distance"],
        [
            ["2024-01-02 06:00:00.000", "UTC-0500", "14001", "2760000", "300", "120", "150", "1800"],
            ["2024-01-02 09:00:00.000", "UTC-0500", "1002", "1800000", "200", "140", "165", "5000"],
        ],
    )
    res = parsers.parse_swims(data)
    assert res.kind == "training_swim"
    assert len(res.rows) == 1  # only the 14001 swim
    row = res.rows[0]
    assert row["type"] == "swim"
    assert row["duration_min"] == 46  # 2_760_000 ms
    assert row["kcal"] == 300.0
    assert row["avg_hr"] == 120
    assert row["distance_m"] == 1800.0
    assert row["source"] == "samsung_health"
