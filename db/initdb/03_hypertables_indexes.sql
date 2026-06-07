-- Promote telemetry to a hypertable (time-partitioned on ts) and add the
-- access-pattern indexes. Runs after 02_schema.sql created the tables.

-- 7-day chunks: small dataset, single user, ~per-minute samples -> keeps chunks
-- light while still bounding how many a typical day/week query touches.
SELECT create_hypertable('telemetry', 'ts', chunk_time_interval => INTERVAL '7 days');

-- Most reads are "this metric over a time range" -> (metric, ts DESC).
CREATE INDEX telemetry_metric_ts_idx ON telemetry (metric, ts DESC);

-- FK + time indexes on the relational tables (Timescale only auto-indexes ts on
-- the hypertable; everything else is explicit).
CREATE INDEX training_sessions_ts_idx     ON training_sessions (ts DESC);
CREATE INDEX training_sets_session_id_idx ON training_sets (session_id);
CREATE INDEX meals_ts_idx                 ON meals (ts DESC);
CREATE INDEX meal_items_meal_id_idx       ON meal_items (meal_id);
CREATE INDEX sleep_sessions_start_ts_idx  ON sleep_sessions (start_ts DESC);
CREATE INDEX recommendations_date_idx     ON recommendations (date DESC);
