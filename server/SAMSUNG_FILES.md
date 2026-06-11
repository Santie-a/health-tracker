# Samsung Health — CSV files used by the server

Quick-reference index of which export CSVs the ingest pipeline reads. Ingest mappings
and parser quirks are in [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
("Samsung Health ingestion").

> Filenames in the export carry a timestamp suffix, e.g.
> `com.samsung.shealth.sleep.20260607134546.csv`. Match on the **data-type prefix**
> (the part before the timestamp), not the exact name — the suffix changes every export.

---

## ✅ Files used (9)

| # | Data-type prefix | → Target | Maps to |
| --- | --- | --- | --- |
| 1 | `com.samsung.health.weight` | `body_composition` | weight, body-fat %, skeletal muscle (kg), BMR |
| 2 | `com.samsung.shealth.sleep` | `sleep_sessions` | start/end, total/rem/light min, efficiency |
| 3 | `com.samsung.health.sleep_stage` | enrich `sleep_sessions` | per-stage segments → deep/rem/light/awake min (join `sleep_id`) |
| 4 | `com.samsung.shealth.stress` | `telemetry` metric=`stress` | `score` per reading |
| 5 | `com.samsung.shealth.tracker.oxygen_saturation` | `telemetry` metric=`spo2` | `spo2` per reading |
| 6 | `com.samsung.shealth.tracker.pedometer_day_summary` | `telemetry` metric=`steps` | daily `step_count` (dedupe device rows/day) |
| 7 | `com.samsung.shealth.calories_burned.details` | `telemetry` metric=`energy_expenditure` | daily TDEE = `rest_calorie + active_calorie` |
| 8 | `com.samsung.shealth.tracker.heart_rate` | `telemetry` metric=`heart_rate` | `heart_rate` per reading (~65k rows, batch) |
| 9 | `com.samsung.shealth.exercise` | `training_sessions` | swim sessions: duration, calorie, HR (map `exercise_type`) |

**Parser quirks (all files):** metadata on line 1 / real header on line 2 /
encoding `utf-8-sig`; `start_time` is local text + separate `time_offset` col
(`UTC-0500`) → combine to UTC; `day_time` is epoch-**milliseconds**.

---

## ❌ Files deliberately skipped

**Binary-sidecar-only** (no usable value column, just `.bin`/sidecar refs):
`com.samsung.health.hrv`, `com.samsung.health.movement`,
`com.samsung.health.oxygen_saturation.raw`, `com.samsung.shealth.stress.histogram`,
`com.samsung.shealth.sleep_raw_data`, `com.samsung.shealth.sleep_data`.

**Superseded:** `com.samsung.shealth.step_daily_trend` (using `pedometer_day_summary`),
`com.samsung.shealth.tracker.pedometer_step_count` (per-interval; daily summary used).

**Not relevant to the app:** `device_profile`, `height`, `user_profile`,
`activity.day_summary`, `activity.goal`, `activity_level`, `alerted_stress`,
`floors_climbed`, `tracker.floors_day_summary`, `badge`, `best_records`, `breathing`,
`respiratory_rate`, `food_goal`, `goal_history`, `insight.message_notification`,
`insight_message`, `mood`, `permission`, `preferences`, `program.sleep_coaching.*`,
`report`, `rewards`, `service_preferences`, `sleep_combined`, `sleep_goal`,
`sleep_snoring`, `social.*`, `vitality_score`, and all `exercise.*` sub-files
(`extension`, `max_heart_rate`, `periodization_*`, `program*`, `program_schedule`,
`program_summary`, `recovery_heart_rate`, `weather`).

> `mood` and `vitality_score` are candidates to revisit later as recommendation signals.
