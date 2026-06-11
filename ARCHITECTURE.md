# Health Tracker — Architecture

Personal health-tracking app. Single user (you). Tracks training (swim AM, gym PM), nutrition, and Samsung Health telemetry (Galaxy Watch 4 Classic: sleep, steps, stress, body composition), and produces daily recommendations.

## Decisions

- **Topology: single gateway.** The Next frontend talks ONLY to the Python server.
  The server is the API gateway + the bridge to the database and the GPU image service.
  Rationale: single user, one auth surface, one API contract, no CORS sprawl. The GPU
  box and Pi5 are never exposed to the frontend directly.
- **Image/macro detection: separate GPU service** on the desktop with the RTX 5070,
  exposing inference over HTTP (FastAPI). The gateway proxies requests to it. The GPU
  box only needs to be on when you log a meal photo; everything else keeps running.
- **Recommendations: rule-based first.** Deterministic heuristics over sleep/stress/
  training-load/nutrition. ML/optimization comes later once you have logged history.
- **Deployment: Pi5 is the always-on host; the PC is an on-demand accelerator.**
  The Pi5 runs db + gateway + **frontend**, so the website is reachable 24/7 (LAN/VPN)
  without the PC. Iterate on the PC during dev, then containerize for arm64 and run the
  whole stack on the Pi5 (gateway->DB and frontend->gateway become localhost). For a
  single user the load is negligible (CRUD + one daily rule-based pass), so the Pi5
  handles it with room to spare. The **image service is the only thing on the PC**
  (needs x86 + CUDA); turn the PC on only to log meal photos. When it's off, meal
  logging degrades to manual entry and nothing else is affected. See DEPLOY.md.

## Component map

```
  ┌───────────────────────── Raspberry Pi 5 (always on) ─────────────────────────┐
  │              ┌─────────────────────────┐                                       │
  │              │  Next frontend           │                                       │
  │              │  dashboard + logging UI  │                                       │
  │              └────────────┬─────────────┘                                       │
  │                           │ localhost (single contract)                         │
  │              ┌────────────▼─────────────┐                                       │
  │              │  Python API gateway       │   FastAPI                            │
  │              │  - auth (single token)    │                                       │
  │              │  - DB access (CRUD)       │                                       │
  │              │  - recommendation engine  │                                       │
  │              │  - proxy to image service │                                       │
  │              │  - Samsung Health ingest  │                                       │
  │              └──────┬──────────────┬─────┘                                       │
  │                     │ localhost    │                                             │
  │       ┌─────────────▼────┐         │                                            │
  │       │ Postgres          │         │                                            │
  │       │ in Docker         │         │                                            │
  │       │ + TimescaleDB ext │         │                                            │
  │       └───────────────────┘         │ LAN/VPN (only when PC is on)               │
  └─────────────────────────────────────┼──────────────────────────────────────────┘
                                         │
                          ┌──────────────▼─────────────┐
                          │ Image/macro svc (PC, 5070) │  FastAPI + CUDA
                          │ food detection -> macros    │  on-demand; off -> manual entry
                          └────────────────────────────┘
```
Browser/phone reaches the frontend on the Pi5 over the LAN/VPN. The PC hosts only the
GPU image service and can stay off; the gateway degrades to manual entry when it's down.

## Why TimescaleDB over plain Postgres
Your data is overwhelmingly time-series (per-minute/hourly telemetry). TimescaleDB is a Postgres extension — same SQL, same client, same deploy story (just a different Docker image) — but adds hypertables, automatic time partitioning, continuous aggregates (precomputed daily/weekly rollups), and retention policies. For "track telemetry over time and roll it up," it's a clear win and costs you nothing in complexity. Plain Postgres is the safe fallback if the ARM image gives you trouble on the Pi5; you can migrate the extension on later. SQLite is too limited for concurrent service access; InfluxDB would fragment your relational meal/training data away from your telemetry. Recommendation:
**TimescaleDB**, with plain Postgres as fallback.

## Data domains
- **telemetry** (time-series): sleep sessions, steps, heart rate, stress index, SpO2.
- **body_composition**: weight, body fat %, skeletal muscle, BMR — periodic, not dense.
- **training**: sessions (swim/gym), type, duration, load/RPE, per-exercise detail.
- **nutrition**: meals, items, macros (from image service or manual), kcal totals.
- **recommendations**: generated daily, stored for history/feedback.

## Repo layout
```
health-tracker/
  ARCHITECTURE.md        <- this file
  README.md
  db/        README.md            <- Pi5 Postgres/Timescale
  server/    IMPLEMENTATION_PLAN  <- Python gateway + recommendations
  image-svc/ README.md            <- GPU food->macros service
  frontend/  IMPLEMENTATION_PLAN  <- Next dashboard
```

## Build order (suggested)
1. db (schema + container) — everything depends on it.
2. server (DB bridge + ingest + stub recommendations + image proxy).
3. image-svc (can be stubbed in the server until ready).
4. frontend (last; consumes a stable gateway API).

## Code structure & conventions (decided 2026-06-07)
Locked in *before* the server is written, to keep it modular as features land.

### Server: layered by domain
The gateway is organized by **domain package**, each split into the same layers so
HTTP, business logic, and persistence never bleed together:

```
server/app/
  main.py                  # app factory, router registration, lifespan
  core/                    # config, db session, auth, shared deps (cross-cutting)
  domains/
    telemetry/   router.py · service.py · repository.py · models.py · schemas.py
    training/    router.py · service.py · repository.py · models.py · schemas.py
    nutrition/   router.py · service.py · repository.py · models.py · schemas.py
    recommendations/ router.py · service.py · repository.py · models.py · schemas.py
```
- **router** = thin HTTP (validation, status codes, calls a service). No SQL, no rules.
- **service** = business logic / orchestration. The only layer with domain rules
  (recommendation heuristics, serving→macro estimation, set→muscle stats).
- **repository** = all DB access (SQLAlchemy). Services depend on repositories, not sessions.
- **models** = SQLAlchemy ORM; **schemas** = Pydantic request/response (kept separate).
- Wiring is via FastAPI dependency injection (settings, db session, auth token).
  Rationale: each domain is independently testable and new features slot into one
  package instead of threading through a god-module.

### Shared nutrition core (one matcher, two consumers)
The macro table + name matcher (`image-svc/app/nutrition/usda.py`) is the source of
truth for **both** photo estimation and the gateway's manual/serving entry. It moves
into an in-repo package (e.g. `packages/nutrition_core/`) that both services install
(editable: `pip install -e`), so "rice" resolves identically on both paths and the
macro data has a single `table_version`. image-svc keeps bundling its own copy of the
data so it stays **network-independent**. *This extraction happens when the server is
scaffolded (the consumer) — not before, to avoid churning the working, tested image-svc.*

### Secrets & version control
- One shared bearer token (gateway ⇄ image-svc) and DB creds live only in `.env`
  files (gitignored). `.env.example` is the committed, documented template.
- Root `.gitignore` + `.gitattributes` (LF) cover all components. Never commit `.env`,
  venvs, model weights, or `node_modules`.
- The gateway reads the **same** `API_TOKEN` value image-svc expects — keep it one
  secret, document rotation. Don't expose any service publicly without TLS + VPN.

## Resilience & error handling (Pi5 is always-on, unattended)
Goal: the services stay up and *log* failures instead of crashing. "Catch blocks
everywhere" means **principled** error handling, not silent `except: pass` (a
swallowed error that returns wrong data is worse than a crash). The rules:

- **Fail fast at startup, survive at runtime.** Misconfiguration (missing macro CSV,
  bad DB URL, unreadable model) *should* stop boot with a clear logged error — the
  container's `restart: unless-stopped` + a fixed config recovers it. But once
  serving, no single request, photo, parse, or background job may take down the process.
- **Global exception handler on every FastAPI app.** Any unhandled exception →
  logged with context (path, request id) + a clean JSON 5xx. Never leak a stack trace
  to the client; always leave a trace in the logs.
- **Structured logging, not prints.** Stdlib `logging` configured once at startup
  (JSON or key=value), level via env. Docker/systemd capture stdout/stderr on the Pi5.
  Every `except` that doesn't re-raise logs at WARNING/ERROR with enough context to debug.
- **Degrade, don't crash, at integration boundaries.** image-svc offline → gateway
  returns the manual-entry path, not a 500. DB transient error → retry/return a clean
  error. One bad row in an import → skip + log, don't abort the whole file.
- **Guard everything that runs outside a request.** Lifespan hooks, the daily
  recommendation pass, scheduled ingestion: wrap the body so an exception is logged
  and the worker/loop continues, never propagating to kill the process.
- **Catch narrow, not bare.** Except the specific expected errors; let truly unexpected
  ones bubble to the global handler (which logs them). No `except Exception: pass`.
