# db — TimescaleDB (Postgres) for Health Tracker

Containerized Postgres + TimescaleDB. Developed on the PC (Docker Desktop), runs
in production on the Raspberry Pi 5 (arm64). The image is multi-arch, so the only
difference between the two is `.env` (notably `DB_BIND_ADDR`).

This folder is **infra + schema only**. The server owns all reads/writes via
SQLAlchemy. See [../ARCHITECTURE.md](../ARCHITECTURE.md).

## Layout
```
db/
  docker-compose.yml          TimescaleDB service, named volume, healthcheck
  .env.example                copy to .env (gitignored) and fill in
  initdb/                     runs ONCE on first init of an empty volume, in order:
    01_extensions.sql           CREATE EXTENSION timescaledb
    02_schema.sql               all tables + constraints
    03_hypertables_indexes.sql  telemetry -> hypertable, indexes
  apply-later/                run by hand once data is flowing (NOT auto-run):
    10_continuous_aggregates.sql  daily telemetry rollup
    11_retention.sql              drop raw samples > 6 months
```

## First run
```sh
cp .env.example .env          # then edit POSTGRES_PASSWORD
docker compose up -d
docker compose logs -f db     # watch for "database system is ready to accept connections"
```
The `initdb/` scripts run **only** on an empty data volume. After changing them,
re-initialize with `docker compose down -v` (⚠ destroys data) then `up -d`, or
apply the change as a migration against the running DB.

## Verify
```sh
# from the DB host
docker compose exec db psql -U health -d health_tracker -c "\dt"
docker compose exec db psql -U health -d health_tracker \
  -c "SELECT hypertable_name FROM timescaledb_information.hypertables;"

# insert + read a telemetry sample
docker compose exec db psql -U health -d health_tracker -c \
  "INSERT INTO telemetry (ts, metric, value, unit) VALUES (now(), 'steps', 1234, 'count');"
docker compose exec db psql -U health -d health_tracker -c \
  "SELECT * FROM telemetry ORDER BY ts DESC LIMIT 1;"

# from the server box over the LAN (after setting DB_BIND_ADDR on the Pi5)
psql "postgresql://health@<pi5-ip>:5432/health_tracker" -c "SELECT 1;"
```

## Apply the time-series policies (after data flows)
```sh
docker compose exec -T db psql -U health -d health_tracker < apply-later/10_continuous_aggregates.sql
docker compose exec -T db psql -U health -d health_tracker < apply-later/11_retention.sql
```

## Connection string for the server's `.env`
```
postgresql+psycopg://health:<password>@<db-host>:5432/health_tracker
```
`<db-host>` is `localhost` when the server runs on the same box as the DB (Pi5
production), or the Pi5 LAN/VPN IP during PC development.

## Backups (Pi5)
```sh
# nightly cron: dump to the Pi, then copy off-device
docker compose exec -T db pg_dump -U health -Fc health_tracker > backup-$(date +%F).dump
```

## Notes
- `restart: unless-stopped` + a `pg_isready` healthcheck are configured.
- 5432 is bound to `DB_BIND_ADDR` (default `127.0.0.1`). Never expose it to the
  internet — keep the Pi5 on the LAN/VPN.
- Fallback if the Timescale arm64 image misbehaves on the Pi5: switch the image
  to `postgres:16` and drop `01_extensions.sql` + `apply-later/` (plain Postgres;
  `create_hypertable` in `03` would then need removing too).
