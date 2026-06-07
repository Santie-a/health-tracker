-- Apply-later (NOT in initdb): run once telemetry is actually flowing.
--   docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
--     < apply-later/10_continuous_aggregates.sql
--
-- Daily rollup of telemetry. Continuous aggregates are incrementally maintained
-- materialized views — queries hit precomputed daily buckets instead of scanning
-- raw per-minute samples. Pivot specific metrics in the server/dashboard query.
CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', ts) AS day,
    metric,
    avg(value)               AS avg_value,
    min(value)               AS min_value,
    max(value)               AS max_value,
    sum(value)               AS sum_value,   -- meaningful for additive metrics (steps)
    count(*)                 AS sample_count
FROM telemetry
GROUP BY day, metric
WITH NO DATA;

-- Refresh policy: keep the last ~3 days fresh on a daily cadence; older buckets
-- are already materialized and immutable.
SELECT add_continuous_aggregate_policy('telemetry_daily',
    start_offset      => INTERVAL '3 days',
    end_offset        => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 day');
