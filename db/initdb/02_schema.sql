-- Health Tracker schema.
-- Conventions: all timestamps are timestamptz stored in UTC (frontend converts).
-- type/source columns use CHECK constraints (not native enums) so values are
-- trivial to add later without an ALTER TYPE migration dance.
-- The server owns all reads/writes (SQLAlchemy); this file is just the contract.

-- ─────────────────────────────────────────────────────────────────────────────
-- Telemetry — dense time-series from Samsung Health / Galaxy Watch 4.
-- Long/narrow shape (one metric per row) so new metrics need no schema change.
-- Becomes a hypertable in 03_hypertables.sql (partitioned on ts).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE telemetry (
    ts      timestamptz       NOT NULL,
    metric  text              NOT NULL,   -- steps | heart_rate | stress | spo2 | sleep_stage | ...
    value   double precision  NOT NULL,
    unit    text,                         -- bpm | count | % | index | stage-code ...
    source  text              NOT NULL DEFAULT 'samsung_health'
);
-- One reading per (metric, source) at a given instant — lets ingest UPSERT on
-- re-sync without duplicating. Must include ts (the partition key) for Timescale.
CREATE UNIQUE INDEX telemetry_ts_metric_source_uidx
    ON telemetry (ts, metric, source);

-- ─────────────────────────────────────────────────────────────────────────────
-- Sleep sessions — one row per night (sparse). Regular table, not a hypertable.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE sleep_sessions (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    start_ts    timestamptz NOT NULL,
    end_ts      timestamptz NOT NULL,
    total_min   integer,
    deep_min    integer,
    rem_min     integer,
    light_min   integer,
    awake_min   integer,
    efficiency  numeric(5,2),             -- percent, 0–100
    UNIQUE (start_ts),
    CHECK (end_ts > start_ts)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Body composition — periodic (smart-scale) readings. Sparse; regular table.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE body_composition (
    ts                  timestamptz PRIMARY KEY,
    weight_kg           numeric(5,2),
    body_fat_pct        numeric(4,1),
    skeletal_muscle_kg  numeric(5,2),
    bmr_kcal            integer
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Training — sessions (swim AM / gym PM) and their per-set detail.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE training_sessions (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ts            timestamptz NOT NULL,
    type          text        NOT NULL CHECK (type IN ('swim', 'gym')),
    duration_min  integer,
    rpe           numeric(3,1) CHECK (rpe >= 0 AND rpe <= 10),  -- rate of perceived exertion
    load          numeric(8,2),                                 -- e.g. duration_min * rpe
    notes         text
);

CREATE TABLE training_sets (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id  bigint NOT NULL REFERENCES training_sessions (id) ON DELETE CASCADE,
    exercise    text   NOT NULL,           -- 'bench press' | 'freestyle' ...
    set_no      integer,
    reps        integer,                   -- gym
    weight_kg   numeric(6,2),              -- gym
    distance_m  numeric(8,2),              -- swim
    pace        text                       -- swim, e.g. '1:45/100m'
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Nutrition — meals and their items. Items come from the image service
-- (photo -> macros) or manual entry.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE meals (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ts          timestamptz NOT NULL,
    name        text,
    photo_path  text,
    source      text NOT NULL DEFAULT 'manual' CHECK (source IN ('image', 'manual'))
);

CREATE TABLE meal_items (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    meal_id    bigint NOT NULL REFERENCES meals (id) ON DELETE CASCADE,
    food       text   NOT NULL,
    grams      numeric(7,2),
    kcal       numeric(7,2),
    protein_g  numeric(6,2),
    carbs_g    numeric(6,2),
    fat_g      numeric(6,2)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Goals — the user's objective (lean bulk / gain weight / improve sleep / ...).
-- Records intent plus an optional measurable target; the recommendation engine
-- reads the active goal to turn descriptive signals into directional advice.
-- At most one active goal per category (body / sleep) via a partial unique index.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE goals (
    id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type                  text NOT NULL CHECK (type IN
                              ('gain_muscle','gain_weight','lose_fat','recomp','maintain','improve_sleep')),
    category              text NOT NULL CHECK (category IN ('body','sleep')),
    status                text NOT NULL DEFAULT 'active'
                              CHECK (status IN ('active','achieved','abandoned')),
    metric                text,            -- weight_kg | skeletal_muscle_kg | body_fat_pct | sleep_min | sleep_efficiency
    baseline_value        numeric(7,2),    -- metric value when the goal was created
    target_value          numeric(7,2),    -- metric value to reach
    target_rate_per_week  numeric(6,3),    -- desired weekly change, e.g. +0.25 kg/wk
    start_date            date NOT NULL DEFAULT CURRENT_DATE,
    target_date           date,
    calorie_delta         integer,         -- surplus(+)/deficit(-) vs TDEE the engine should aim for
    protein_g_per_kg      numeric(4,2),    -- protein target override (e.g. 2.0 on a cut)
    notes                 text,
    created_at            timestamptz NOT NULL DEFAULT now()
);
-- One active goal per category keeps the derived thresholds unambiguous.
CREATE UNIQUE INDEX goals_one_active_per_category ON goals (category) WHERE status = 'active';
CREATE INDEX goals_status_idx ON goals (status);

-- ─────────────────────────────────────────────────────────────────────────────
-- Recommendations — one rule-based pass per day, stored for history + feedback.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE recommendations (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date          date        NOT NULL,
    payload       jsonb       NOT NULL,    -- the generated recommendation set
    generated_at  timestamptz NOT NULL DEFAULT now(),
    feedback      text,                    -- optional user reaction, for later tuning
    UNIQUE (date)
);
