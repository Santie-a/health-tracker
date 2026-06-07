-- Apply-later (NOT in initdb): run after the daily continuous aggregate exists.
--   docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
--     < apply-later/11_retention.sql
--
-- Drop raw per-sample telemetry older than 6 months. The telemetry_daily
-- continuous aggregate is a separate hypertable and is NOT affected, so the
-- daily rollups are kept forever while raw samples age out.
SELECT add_retention_policy('telemetry', INTERVAL '6 months');
