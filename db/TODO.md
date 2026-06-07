# DB — Postgres + TimescaleDB on Raspberry Pi 5

Goal: a lightweight, containerized time-series-friendly SQL store. Primary learning goal
is deploying/operating containers on the Pi5.

> Status (2026-05-31): schema + compose built and validated locally on the PC
> (Docker Desktop, TimescaleDB pg16). Pi5 deploy + LAN/backup items remain. See
> `README.md` for run/verify steps.

## Setup
- [ ] Install Docker + Docker Compose on the Pi5 (64-bit Raspberry Pi OS required for the arm64 image).
- [x] `docker-compose.yml` using `timescale/timescaledb:latest-pg16` (arm64). Fallback: official `postgres:16` if the Timescale ARM image misbehaves.
- [x] Mount a named volume for `/var/lib/postgresql/data`. Confirm it survives `docker compose down`. *(named volume `health-tracker-pgdata`)*
- [x] Put credentials/DB name in `.env` (gitignored). Provide `.env.example`.
- [x] Bind only to the LAN interface (or keep it behind your VPN). Do NOT expose 5432 to the internet. *(`DB_BIND_ADDR`, default 127.0.0.1)*

## Schema (init SQL in `./initdb/`)
- [x] `CREATE EXTENSION IF NOT EXISTS timescaledb;`
- [x] `telemetry(ts, metric, value, unit, source)` -> make hypertable on `ts`.
      Covers steps, stress index, heart rate, SpO2, sleep stage samples.
- [x] `sleep_sessions(id, start_ts, end_ts, total_min, deep_min, rem_min, light_min, awake_min, efficiency)`.
- [x] `body_composition(ts, weight_kg, body_fat_pct, skeletal_muscle_kg, bmr_kcal)`.
- [x] `training_sessions(id, ts, type[swim|gym], duration_min, rpe, load, notes)`.
- [x] `training_sets(id, session_id FK, exercise, set_no, reps, weight_kg, distance_m, pace)`.
- [x] `meals(id, ts, name, photo_path, source[image|manual])`.
- [x] `meal_items(id, meal_id FK, food, grams, kcal, protein_g, carbs_g, fat_g)`.
- [x] `recommendations(id, date, payload jsonb, generated_at, feedback)`.
- [x] Indexes on FK columns and `ts`.

## Timescale features (after data flows)
- [x] Continuous aggregate: daily rollup (steps total, avg stress, sleep total, kcal in/out estimate). *(`apply-later/10_continuous_aggregates.sql`, smoke-tested)*
- [x] Retention policy: keep raw per-sample telemetry N months, keep daily rollups forever. *(`apply-later/11_retention.sql`, 6-month raw retention)*

## Ops / verification
- [ ] Backup script: `pg_dump` to a file on the Pi (cron) + copy off-device. *(command documented in README; not yet cron'd)*
      - [ ] Backup must fail loudly: log to a file + non-zero exit so a failed/0-byte dump
            is noticeable (a silent backup failure is the classic Pi5 footgun). Connection
            resilience itself is the server's job (pool pre-ping/retry — see server/TODO.md).
- [x] Health check in compose; auto-restart policy `unless-stopped`.
- [x] Verify: connect from the server box over LAN with `psql`, insert + read a row. *(verified locally; LAN test pending Pi5)*
- [x] Document connection string format for the server's `.env`.

## Notes
- The server owns all writes/reads via SQLAlchemy; this folder is only infra + schema + migrations.
- Consider Alembic migrations living in `server/` instead of raw initdb once past the prototype.

## Schema additions — strength tracking & manual nutrition (planned features)

### Exercise catalog & richer per-set logging (feature: training balance + stats)
Most of this already exists: `training_sets(exercise, set_no, reps, weight_kg, ...)`
captures per-set work today, but `exercise` is free text, so it can't drive balance
statistics. Add a catalog + muscle taxonomy and link to it.
- [ ] `exercises(id, name, slug UNIQUE, category, primary_muscle, equipment,
      is_unilateral bool, is_bodyweight bool, aliases text[], is_active bool DEFAULT true)`.
      - `category`: push | pull | squat | hinge | carry | core | swim | other (CHECK).
      - `primary_muscle`: chest | back | lats | traps | front_delt | side_delt |
        rear_delt | biceps | triceps | forearms | quads | hamstrings | glutes |
        calves | abs | obliques | ... (CHECK, or a small `muscles` lookup table).
      - Free-text fallback stays: an un-cataloged movement can still be logged.
- [ ] `exercise_muscles(exercise_id FK, muscle, role)` — role: primary | secondary.
      Powers honest balance stats (bench credits chest fully + triceps/front-delt
      partially). Can start primary-only; the junction lets secondary contribution
      come later without a reshape.
- [ ] Extend `training_sets`:
      - [ ] `exercise_id bigint REFERENCES exercises(id)` (nullable; keep `exercise`
            text as the as-logged label / fallback).
      - [ ] `is_warmup bool DEFAULT false` (warmups excluded from working-set counts).
      - [ ] `rpe numeric(3,1)` per set (autoregulation; session already has one).
      - [ ] `added_weight_kg numeric(6,2)` for weighted bodyweight (dips/pull-ups);
            reps-only when both weight columns are null.
      - [ ] Index `training_sets(exercise_id)`.
- [ ] Seed the catalog with your common lifts (press, lateral raise, bench, squat,
      deadlift, row, pull-up, ...) with muscle/category mappings — see server seed task.

### Foods table & serving-based estimation (feature: manual nutrition, no daily weighing)
Today macros live only in image-svc's bundled CSV. Manual entry needs a queryable
food DB on the server side + portion presets so "rice" -> a sensible estimate
without weighing grams.
- [ ] `foods(id, name, slug UNIQUE, aliases text[], kcal_100g, protein_100g,
      carbs_100g, fat_100g, default_grams, table_version)`. Per-100g macros, same
      basis as image-svc's CSV.
- [ ] `food_portions(id, food_id FK, label, grams, is_default bool)` — e.g.
      rice "1 cup cooked"=158g, bread "1 slice"=28g, banana "1 medium"=118g. Lets
      the UI offer servings instead of forcing a gram field.
- [ ] Seed `foods`/`food_portions` from image-svc's macro CSV (single source of
      truth; see server seed task) and stamp the same `table_version` so image +
      manual items stay consistent.
- [ ] Extend `meal_items`:
      - [ ] `food_id bigint REFERENCES foods(id)` (nullable; free-text `food` stays
            for un-cataloged / image `(unmatched)` items).
      - [ ] `qty numeric(6,2)` + `portion_label text` (e.g. 2 × "1 cup") so the entry
            is reconstructable; `grams` stays as the resolved amount.
      - [ ] `estimated bool DEFAULT false` — true when macros came from a serving
            preset rather than a weighed amount.
      - [ ] `source text` per item (image | manual | estimate); `meals.source` stays
            the meal-level origin.
      - [ ] Index `meal_items(food_id)`.

### Migrations
- [ ] These are post-prototype changes -> do them as Alembic migrations in `server/`
      (per the note above), not by hand-editing `initdb/`. Once stable, fold the same
      tables/columns into `initdb/` so a fresh Pi5 bring-up matches.
