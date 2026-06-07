# Server — Implementation Plan

Ordered breakdown of the gateway build into small, individually-shippable tasks.
Derived from [ARCHITECTURE.md](../ARCHITECTURE.md), [server/TODO.md](./TODO.md),
[db/TODO.md](../db/TODO.md), and the existing schema
([db/initdb/02_schema.sql](../db/initdb/02_schema.sql)). The `image-svc` app is the
reference implementation for config/auth/logging/app-factory patterns — mirror it.

Status legend: [ ] todo · [~] in progress · [x] done.

---

## Objective & data philosophy (the principle that drives every design choice)

The server is the personal health record + advisor: **you log what you do, the watch
records how your body responded, and the server turns both into daily statistics and
recommendations.**

**Manual data is the primary source of truth; telemetry is complementary.**

- **Primary (manual, user-maintained):** training sessions + per-set detail, swim
  sessions, nutrition (manual / serving / photo). These are first-class and **fully
  functional with an empty telemetry table** — the app works with the watch never
  synced and the GPU box off.
- **Complementary (telemetry, import-only, read-only context):** sleep, stress, SpO2,
  steps, resting HR, daily energy expenditure (TDEE), watch-detected swims. Imported in
  batches from Samsung exports. **Never required, never a source of truth, never blocks
  a manual action.** It exists only to enrich stats and feed the engine.

**They combine, and that join is the point:** manual answers "what did I do?", telemetry
answers "how did my body handle it?", the engine answers "what should I do next?"
(e.g. manual gym load × telemetry sleep/stress → deload flag; manual intake × telemetry
TDEE → calorie balance).

**Build implications (carry through every phase):**
1. Manual endpoints are standalone — they must work with zero telemetry present.
2. Telemetry ingest is additive and resilient — missing days / failed imports / no
   watch degrade gracefully, never break the manual app.
3. The recommendation engine treats each telemetry input as **optional**: a rule fires
   if its signal exists, is skipped+logged if not. No telemetry → recommendations still
   run on manual data alone.

---

## Critical path
A frontend-usable gateway needs Phases **0 → 1 → 3 → 4 → 5 → 6 → 8**.
Phases **2** (shared matcher) and **7** (strength stats + manual nutrition) add depth
and can land incrementally without blocking the frontend.

---

## Phase 0 — Scaffold & cross-cutting core ✅ DONE
The skeleton everything slots into. No domain logic yet.
Built on Python 3.12 venv; 5 tests pass (liveness, request-id echo, error shape, readiness).

- [x] **0.1 Project scaffold & deps.** `server/app/{main.py,core/,domains/}` per
  ARCHITECTURE; `requirements.txt`, `pytest.ini`, `.gitignore`, `.env.example`.
- [x] **0.2 `core/config.py`** — pydantic-settings: `DATABASE_URL`, `API_TOKEN`,
  `IMAGE_SVC_URL`, `IMAGE_SVC_TIMEOUT`, `LOG_LEVEL`.
- [x] **0.3 `core/logging_config.py`** — idempotent stdout logger (copied from image-svc).
- [x] **0.4 `core/auth.py`** — `HTTPBearer` + `secrets.compare_digest` dep.
- [x] **0.5 `core/db.py`** — lazy async engine (`pool_pre_ping=True`), `async_sessionmaker`,
  `get_session` dependency (commit on success / rollback on error), `ping()` for readiness.
- [x] **0.6 `main.py` app factory** — lifespan (configure logging, build+dispose engine),
  global `Exception` + `RequestValidationError` + `HTTPException` handlers (consistent
  `{detail, request_id}` shape, no stack trace to client), request-id middleware
  (`core/errors.py`), `GET /health` (liveness, no DB) + `GET /health/ready` (DB ping → 503).

## Phase 1 — Persistence foundation
- [ ] **1.1 ORM models** for existing schema across each domain's `models.py`
  (telemetry, sleep_sessions, body_composition, training_sessions, training_sets,
  meals, meal_items, recommendations). Match initdb exactly.
- [ ] **1.2 Alembic setup** — async `env.py`; baseline migration that **stamps** the
  existing initdb schema (don't recreate prod DBs). Migrations run on deploy (DEPLOY.md).
- [ ] **1.3 Migration: strength + nutrition extensions** (db/TODO.md additions):
  `exercises`, `exercise_muscles`, `foods`, `food_portions` + new `training_sets` /
  `meal_items` columns. Schema only; endpoints land in Phases 6–7.

## Phase 2 — Shared nutrition core
- [ ] **2.1 Extract `packages/nutrition_core/`** — move `usda.py` matcher + `macros.csv`
  into an installable package; `pip install -e` from both services; update image-svc
  imports; confirm image-svc tests still pass. image-svc keeps bundling its own data
  copy (network-independent).

## Phase 3 — Telemetry + Samsung ingest
- [ ] **3.1 Telemetry read path** — repository/service/router for
  `GET /telemetry?metric=&from=&to=` (raw + rollups).
- [ ] **3.2 Samsung Health ingest** — `POST /ingest/samsung`: parser per file type,
  unit mapping, dedupe, source tag, idempotent upsert. Row-resilient (skip+log bad
  rows, return ok/skipped counts). Document export steps. **Concrete file list +
  mappings below.** Suggested sub-tasks (one parser each, shared CSV reader):
  - [ ] **3.2.0 Shared Samsung CSV reader** — skip metadata line 1, header on line 2,
    `utf-8-sig`; helper to combine local `start_time`/`day_time` + `time_offset` → UTC;
    helper to read epoch-ms `day_time`. Row-resilient wrapper (skip+log+count).
  - [ ] **3.2.1 weight → `body_composition`** (`health.weight`).
  - [ ] **3.2.2 sleep → `sleep_sessions`** (`shealth.sleep`) + **stage enrichment**
    from `health.sleep_stage` (join on `sleep_id`, aggregate stage codes → deep/rem/
    light/awake min).
  - [ ] **3.2.3 stress → `telemetry`** metric=`stress` (`shealth.stress`, `score`).
  - [ ] **3.2.4 spo2 → `telemetry`** metric=`spo2` (`tracker.oxygen_saturation`).
  - [ ] **3.2.5 steps → `telemetry`** metric=`steps` (`tracker.pedometer_day_summary`;
    dedupe multiple device rows per `day_time`).
  - [ ] **3.2.6 TDEE → `telemetry`** metric=`energy_expenditure`
    (`calories_burned.details`: `rest_calorie + active_calorie`).
  - [ ] **3.2.7 heart_rate → `telemetry`** metric=`heart_rate`
    (`tracker.heart_rate`, ~65k rows — batch insert).
  - [ ] **3.2.8 exercise → `training_sessions`** (`shealth.exercise`; map
    `exercise_type` codes → swim, import duration/calorie/HR; gym sets stay manual).

## Phase 4 — Training (basic)
- [ ] **4.1 Sessions CRUD** — `POST /training` / `GET /training` for swim/gym sessions
  (+ optional inline `sets[]`).

## Phase 5 — Nutrition + image-svc bridge
- [ ] **5.1 image-svc HTTP client** — httpx with timeout + retry; on ANY failure return
  the manual-entry fallback, never 500; log cause. Stub/feature-flag so the server works
  before the GPU box exists.
- [ ] **5.2 Meals endpoints** — `POST /meals` (multipart photo → proxy → store macros,
  manual override), `GET /meals?date=` (items + totals).

## Phase 6 — Recommendations
- [ ] **6.1 Rule engine (pure functions)** — table-driven heuristics: low sleep/high
  stress → deload; high load + low protein → protein gap; calorie balance; two-a-day
  hydration/carb timing. Thresholds in a config module.
- [ ] **6.2 Daily pass + storage + endpoint** — generate → store in `recommendations`
  (jsonb, unique per date, feedback field); `GET /recommendations?date=`; guarded so a
  failed pass never kills the API.

## Phase 7 — Planned features (strength + manual nutrition)
- [ ] **7.1 Exercise catalog** — `GET /exercises` (search/autocomplete), `POST /exercises`.
- [ ] **7.2 Per-set logging** — `POST /training/{id}/sets`; resolve free-text → catalog.
- [ ] **7.3 Strength stats** — `GET /training/stats`: working sets/muscle/week (fractional
  secondary credit, exclude warmups), volume load + trend, push:pull & upper:lower,
  est. 1RM (Epley), PRs.
- [ ] **7.4 Foods seed loader** — seed `foods`/`food_portions` from nutrition_core CSV at
  migration/startup; stamp `table_version`.
- [ ] **7.5 Manual/serving nutrition** — `GET /foods?q=`, `GET /foods/resolve?name=`
  (reuse matcher), `POST /meals/{id}/items` (food_id + portion×qty OR grams, `estimated`
  flag), quick-add (recent/frequent/repeat-yesterday/raw-kcal).
- [ ] **7.6 Recommendation hooks** — feed weekly per-muscle counts + imbalance ratios
  into the engine.

## Phase 8 — Dashboard, seed, deploy
- [ ] **8.1 `GET /dashboard?date=`** — single aggregated day view (telemetry rollup +
  training + nutrition totals + recommendations) powering the frontend home.
- [ ] **8.2 Seed script** — fake data across telemetry/training-sets/meals for frontend dev.
- [ ] **8.3 Dockerfile** (multi-arch `python:3.x-slim`) + Pi5 compose entry next to
  Postgres; verify arm64 wheels; review OpenAPI `/docs` (the frontend contract).

Tests are written **alongside each domain**, not deferred (server/TODO.md "Verification"):
table-driven rules, ingest parser, error paths (image-svc offline→fallback, bad row→skip,
DB error→503, global handler shape), strength stats, serving→macro resolution.

---

## Samsung Health ingestion — format notes & scope decision

The export is real and parseable but **fiddly and version-dependent**. What the
"Download personal data" export actually produces (a ZIP):

- A folder of CSVs named `com.samsung.(s)health.<datatype>.<timestamp>.csv`, plus a
  `jsons/` subfolder of sidecar files for dense/nested data.
- **Each CSV's first line is a metadata row** (version + datatype); the real column
  header is on **line 2**. A naive `csv.DictReader` reads the wrong header — skip line 1.
- **Timestamps are messy**: epoch-milliseconds in some columns, local strings in others,
  with separate `time_offset` columns (e.g. `UTC+0200`). Must normalize to UTC.
- **Dense data lives in JSON sidecars**, not the CSV: per-minute heart rate, sleep-stage
  bins, etc. The CSV row points at a file in `jsons/` by UUID. Parsing these is the
  expensive, brittle part and drifts most across app versions.

High-value-but-tedious-to-type metrics (the reason to bother automating): **daily steps,
sleep sessions, stress, SpO2, weight/body-composition**. These mostly come from
*daily-summary* CSVs that are flat and easy — no JSON-sidecar parsing needed.

### Locked-in v1 scope (decided 2026-06-07, against the real export in `server/schema.md`)

Files to ingest and their targets (one parser each, see tasks 3.2.0–3.2.8):

| Source CSV (`com.samsung.*`) | → Target | Fields used |
| --- | --- | --- |
| `health.weight` | `body_composition` | `weight`→weight_kg, `body_fat`(%)→body_fat_pct, `skeletal_muscle_mass`(kg)→skeletal_muscle_kg, `basal_metabolic_rate`→bmr_kcal |
| `shealth.sleep` | `sleep_sessions` | `start_time`,`end_time`,`sleep_duration`→total_min,`efficiency`,`total_rem_duration`,`total_light_duration` |
| `health.sleep_stage` | enrich `sleep_sessions` | join `sleep_id`; aggregate `stage` (40001/2/3) → deep/rem/light/awake min |
| `shealth.stress` | `telemetry` metric=`stress` | `start_time`,`score` |
| `tracker.oxygen_saturation` | `telemetry` metric=`spo2` | `start_time`,`spo2` |
| `tracker.pedometer_day_summary` | `telemetry` metric=`steps` | `day_time`,`step_count` (dedupe device rows/day) |
| `calories_burned.details` | `telemetry` metric=`energy_expenditure` | `day_time`, `rest_calorie + active_calorie` |
| `tracker.heart_rate` | `telemetry` metric=`heart_rate` | `start_time`,`heart_rate` (~65k rows, batch) |
| `shealth.exercise` | `training_sessions` | `start_time`,`duration`,`calorie`,HR; map `exercise_type`→swim |

**Explicitly skipped:** binary-sidecar-only files (`hrv`, `movement`,
`oxygen_saturation.raw`, `stress.histogram`, `sleep_raw_data`, `sleep_data`); all
goals/badges/rewards/social/insight/program files; `vitality_score` (opaque composite);
`mood` (revisit later as a rec signal). `step_daily_trend` not used — superseded by
`pedometer_day_summary`.

### Parser quirks (apply in 3.2.0 shared reader)
- **Metadata line 1**, real header on line 2; encoding `utf-8-sig`.
- **Timestamps:** `start_time` is *local* text + a separate `time_offset` col
  (`UTC-0500`) → combine to UTC. `day_time` is epoch-**milliseconds**.
- **Daily-step dedup:** multiple device rows per `day_time` — aggregate before insert
  or steps inflate.
- **Idempotent upsert:** telemetry on `(ts, metric, source)`; body_composition on `ts`;
  sleep on `start_ts`; exercise/training on a stable natural key (e.g. start_ts+type).

**Later:** Health Connect (Android) as a cleaner automated bridge (server/TODO.md).
