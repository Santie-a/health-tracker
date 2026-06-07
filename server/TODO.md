# Server — Python API Gateway (FastAPI)

The single backend the frontend talks to. Owns DB access, recommendation logic, Samsung
Health ingestion, and proxies meal photos to the GPU image service.

## Structure (decided — see ARCHITECTURE.md "Code structure & conventions")
- [ ] Layered **by domain**: `app/domains/{telemetry,training,nutrition,recommendations}/`
      each with `router.py` (thin HTTP) · `service.py` (business logic) · `repository.py`
      (DB access) · `models.py` (SQLAlchemy) · `schemas.py` (Pydantic). Routers hold no
      SQL/rules; services depend on repositories, not raw sessions.
- [ ] `app/core/` for cross-cutting: `config.py` (pydantic-settings, mirror image-svc's),
      `db.py` (async engine/session dependency), `auth.py` (bearer dep, reuse the
      `secrets.compare_digest` pattern from image-svc), shared deps.
- [ ] `app/main.py` = app factory + router registration + lifespan only.
- [ ] Install the shared `nutrition_core` package (editable) for manual-entry macro
      resolution instead of duplicating image-svc's matcher.

## Stack
- [ ] FastAPI + Uvicorn. Pydantic v2 models for request/response.
- [ ] SQLAlchemy 2.x + asyncpg for Postgres/Timescale. Alembic for migrations.
- [ ] `.env` for DB URL, single API bearer token, image-svc URL. Provide `.env.example`.
- [ ] Develop on the PC (fast iteration), then containerize for the Pi5.
- [ ] Dockerfile on a multi-arch base (`python:3.x-slim`) so the SAME image builds for
      arm64. Verify `asyncpg`/SQLAlchemy/FastAPI wheels resolve on arm64 (they do).
- [ ] In production, run this container in the Pi5 `docker-compose.yml` next to Postgres
      so gateway->DB is localhost. Keep the image-svc URL pointing at the PC over LAN/VPN.

## Auth
- [ ] Single static bearer token (header `Authorization: Bearer ...`) checked by a dependency. Single user — keep it simple. Don't expose the server publicly without TLS + VPN.

## Core API (REST, `/api/v1`)
- [ ] `GET  /health`
- [ ] `POST /ingest/samsung` — accept exported Samsung Health data (CSV/JSON), normalize, upsert into telemetry/sleep/body_composition. Idempotent on (ts, metric).
- [ ] `GET  /telemetry?metric=&from=&to=` — query rollups/raw.
- [ ] `POST /training` / `GET /training` — log + list swim/gym sessions and sets.
- [ ] `POST /meals` — accepts a photo (multipart); forwards to image-svc; stores returned macro estimate; allows manual override.
- [ ] `GET  /meals?date=` — daily nutrition + totals.
- [ ] `GET  /dashboard?date=` — aggregated day view (one call powering the frontend home).
- [ ] `GET  /recommendations?date=` — today's recommendations.

## Samsung Health ingestion
- [ ] Start with the manual export flow (Samsung Health -> data export -> CSV/JSON), since there is no clean public live API. Write a parser per file type.
- [ ] Map units, dedupe, store source tag. Document the export steps in this folder.
- [ ] Later: explore Health Connect on Android as a more automated bridge.

## Recommendation engine (rule-based v1)
- [ ] Pure functions: input = today's aggregated metrics, output = list of recommendations.
- [ ] Heuristics to start:
      - Low sleep (<6h) or high stress -> reduce gym intensity / suggest deload.
      - High training load + low protein intake -> flag protein gap (target g/kg bodyweight).
      - Calorie balance vs goal (intake - estimated expenditure) -> over/under message.
      - Two-a-day (swim AM + gym PM) -> hydration + carb timing reminder.
- [ ] Store generated recs in `recommendations` with a feedback field for later ML.
- [ ] Keep thresholds in a config module so they're easy to tune.
- [ ] Later: replace/augment with an optimizer (e.g. macro split under constraints) once history exists.

## Image service bridge
- [ ] HTTP client to image-svc with timeout + graceful fallback (if GPU box is off, return "manual entry" path, don't 500).
- [ ] Feature-flag/stub the image-svc so the server works before it exists.

## Strength tracking & exercise catalog (planned feature)
Per-set logging already exists in the schema; this layer adds the catalog, the
muscle taxonomy, and the analytics that turn logged sets into "what am I focusing
on / what's imbalanced". See db/TODO.md for the `exercises`/`exercise_muscles`
tables and `training_sets` extensions.
- [ ] `GET  /exercises?q=&muscle=&category=` — search/autocomplete the catalog
      (name + aliases) for the frontend exercise picker.
- [ ] `POST /exercises` — add a custom exercise (single user; keep it open).
- [ ] `POST /training/{id}/sets` (or accept `sets[]` in `POST /training`) — log sets
      against a session: exercise_id, set_no, reps, weight_kg/added_weight, rpe,
      is_warmup. Resolve a free-text exercise name -> catalog where possible.
- [ ] `GET  /training/stats?from=&to=` — strength analytics:
      - working sets per muscle group per week (the 10–20 sets/muscle heuristic),
        crediting secondary muscles fractionally via `exercise_muscles`.
      - volume load (Σ reps×weight) per muscle group + trend over time.
      - push:pull and upper:lower ratios -> imbalance flags.
      - per-exercise top set, estimated 1RM (Epley: w×(1+reps/30)), PR history.
      - exclude warmup sets from working-set counts.
- [ ] Seed script: starter exercise catalog (your common lifts) with muscle/category
      mappings. Fold into the general seed task below.
- [ ] Recommendation hooks: feed weekly per-muscle set counts + imbalance ratios into
      the engine ("posterior chain lagging", "you've skipped pull this week").

## Manual nutrition & serving-based estimation (planned feature)
Goal: log food without weighing grams daily — type "rice", pick "1 cup", get an
estimate. The image model stays complementary; both paths resolve to the same
`foods` table and sum into one total. See db/TODO.md for `foods`/`food_portions`
and the `meal_items` extensions.
- [ ] Seed `foods` + `food_portions` from image-svc's macro CSV at migration/startup
      — one loader both components agree on; record the `table_version`.
- [ ] `GET  /foods?q=` — search foods (name + aliases) for manual-entry autocomplete;
      return per-100g macros + portion presets + default serving.
- [ ] `GET  /foods/resolve?name=` — best-match + confidence for a typed name, reusing
      image-svc's token matcher so "rice" resolves identically on both paths (share/
      port `image-svc/app/nutrition/usda.py` rather than re-implementing).
- [ ] `POST /meals/{id}/items` (and manual `POST /meals`) — add an item by
      food_id + (portion_label × qty) OR explicit grams; server resolves -> macros and
      marks `estimated=true` when from a serving preset.
- [ ] Quick-add helpers (the real daily-use win): recent foods, frequent foods/
      favorites, repeat-yesterday, and a raw kcal-only quick entry.
- [ ] Totals in `GET /meals?date=` and `GET /dashboard` sum image + manual + estimate
      items uniformly.

## Resilience & error handling (Pi5 always-on — see ARCHITECTURE.md "Resilience")
The gateway is the long-running process users hit; it must log failures, not crash.
- [ ] Configure stdlib `logging` once in `core/` at startup (level from env, structured
      key=value/JSON to stdout so Docker/systemd capture it on the Pi5). No `print`.
- [ ] Register global handlers on the app:
      - [ ] catch-all `Exception` handler -> log with context (method, path, request id)
            + return a clean JSON 500 (no stack trace to the client).
      - [ ] handler for `RequestValidationError`/`HTTPException` with consistent error shape.
      - [ ] add a request-id middleware so a logged error maps to a specific request.
- [ ] DB resilience: pooled async engine with `pool_pre_ping=true`; wrap repository
      calls so a transient connection error is retried/surfaced as a clean 503, never a
      crash. Services use one transaction per request and roll back on error.
- [ ] image-svc bridge: timeout + retry, and on ANY failure (GPU box off, timeout, 5xx)
      return the manual-entry fallback path — never propagate a 500. Log the cause.
- [ ] Ingestion parser is row-resilient: a malformed row is skipped + logged with line
      number; the import reports counts (ok/skipped) instead of aborting the whole file.
- [ ] Guard everything outside a request (lifespan, the daily recommendation pass, any
      scheduled ingestion): wrap the body so an exception is logged and the loop/worker
      continues. A failed daily pass must not take the API down.
- [ ] `GET /health` stays dependency-light (process up) ; add `/health/ready` that checks
      DB (and optionally image-svc) for orchestration without coupling liveness to them.
- [ ] Catch narrow (expected errors only); let unexpected ones reach the global handler.
      No `except Exception: pass` — a swallowed error returning wrong macros is worse
      than a crash.

## Verification
- [ ] pytest: recommendation rules (table-driven), ingestion parser, API contract.
- [ ] pytest: error paths — image-svc offline -> fallback (not 500), bad ingest row
      skipped + logged, DB error -> clean 503, global handler shape.
- [ ] pytest: strength stats (sets/muscle/week, 1RM, push:pull) and serving->macro
      resolution (table-driven), incl. the shared name matcher.
- [ ] Seed script with fake data for frontend development (telemetry + training sets
      across muscle groups + a few days of meals via manual/serving entry).
- [ ] OpenAPI docs reviewed (`/docs`) — this is the contract the frontend builds against.
