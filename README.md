# Health Tracker

Personal health app: Samsung Health / Galaxy Watch 4 telemetry + training (swim AM,
gym PM) + nutrition (with photo-based macro estimation) -> daily recommendations.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the topology and decisions, and
[DEPLOY.md](./DEPLOY.md) for how it deploys (Pi5 hosts the site 24/7; the PC is an
on-demand GPU box) and how `.env` is handled per machine.

## Components
- `db/` — Postgres + TimescaleDB in Docker on a Raspberry Pi 5.
- `server/` — Python (FastAPI) API gateway: DB access, recommendation engine, image proxy, ingest.
- `image-svc/` — GPU (RTX 5070) FastAPI service: food photo -> macro estimate.
- `frontend/` — Next.js dashboard and logging UI.

Each folder has a `TODO.md`. Start with `db/`, then `server/`, then `image-svc/`, then `frontend/`.

## Conventions
- Frontend talks only to `server/`. Never call the DB or image service from the browser.
- Single-user auth: one bearer token (env var) on the gateway. Keep the Pi5 and GPU box on the LAN/VPN only.
- All timestamps stored UTC; convert in the frontend.
