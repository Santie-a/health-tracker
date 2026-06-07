# Health Tracker — Deployment

How the pieces get onto hardware, in what order, and how secrets (`.env`) are
handled per machine. See [ARCHITECTURE.md](./ARCHITECTURE.md) for the why.

## What runs where

Two machines, two very different roles:

| Component        | Raspberry Pi 5 (always on) | PC + RTX 5070 (on-demand) |
|------------------|:--------------------------:|:-------------------------:|
| `db` (Postgres/Timescale) | ✅ production home        | dev/testing only          |
| `server` (gateway)        | ✅ production home        | dev only                  |
| `frontend` (Next.js)      | ✅ **served here 24/7**   | dev only                  |
| `image-svc` (GPU)         | ❌ never (needs CUDA)     | ✅ **only home**          |

**The website lives entirely on the Pi5.** You reach the frontend from your phone/
browser over the LAN/VPN, and it stays up whether or not the PC is on.

**The PC is just a GPU accelerator for one feature.** Turn it on only when you want
photo→macro estimation. When it's off, the gateway can't reach `image-svc`, so meal
logging falls back to **manual entry** — everything else (dashboard, training,
telemetry, recommendations, manual/serving food logging) is unaffected. This is the
designed graceful-degradation path, not an outage.

## Secrets: `.env` is per-host and never travels in git

This is the key thing to internalize:

- **Only `.env.example` is committed.** It's the documented template. The real `.env`
  is gitignored, so when you `git clone`/`pull` onto the Pi5, **no `.env` arrives** —
  that's expected. You create it on each machine.
- **Values differ per host.** The template is shared; the filled-in values are not.
  The clearest example is the gateway's `.env`:

  ```bash
  # server/.env on the PC (dev)
  DATABASE_URL=postgresql+asyncpg://health:<pw>@localhost:5432/health_tracker
  IMAGE_SVC_URL=http://localhost:8001          # image-svc is local during dev

  # server/.env on the Pi5 (prod)
  DATABASE_URL=postgresql+asyncpg://health:<pw>@localhost:5432/health_tracker  # db = same host
  IMAGE_SVC_URL=http://<PC-LAN-or-VPN-IP>:8001 # image-svc lives on the PC
  ```

- **One value must match across machines:** `API_TOKEN`. The PC's `image-svc/.env`
  and the Pi5's `server/.env` must carry the *same* token — it's the shared secret the
  gateway sends to the image service.

### Getting the values onto the Pi5
Pick either (single-user homelab, both fine):
- **Recreate (recommended):** on the Pi5, `cp <component>/.env.example <component>/.env`
  and fill it in by hand. Nothing sensitive leaves your SSH session.
- **Copy then edit:** `scp server/.env pi@pi5:~/health-tracker/server/.env`, then edit
  the host-specific values (`IMAGE_SVC_URL`, etc.). You rarely copy verbatim.

Never `git add` a `.env`. The root `.gitignore` already blocks it; the verification
step below double-checks.

## Networking
- Keep everything on the **LAN or a VPN** (WireGuard/Tailscale). Do **not** port-forward
  any service to the internet without TLS in front.
- The Pi5 must reach the PC's `image-svc` by a **stable address** — give the PC a static
  LAN IP or a VPN hostname (e.g. a Tailscale name), and put that in the Pi5's
  `server/.env` `IMAGE_SVC_URL`. A DHCP address that changes will break the bridge.
- `DB_BIND_ADDR=127.0.0.1` on the Pi5 is correct and safest: db, gateway, and frontend
  are all on the Pi5, so nothing needs Postgres exposed beyond localhost.

## Deployment order

> Status: `db` is ready today. `server` and `frontend` steps describe the intended flow
> and apply once those components are built (they are currently TODO-only).

### 0. Pi5 prep (once)
- Install **64-bit** Raspberry Pi OS (required for the arm64 Docker images).
- Install Docker Engine + the Compose plugin.
- `git clone` the repo to the Pi5. (No `.env` files come with it — expected.)

### 1. Database — ready now
```bash
cd db
cp .env.example .env          # set POSTGRES_PASSWORD; keep DB_BIND_ADDR=127.0.0.1
docker compose up -d
```
The `initdb/*.sql` runs automatically on the first boot of an empty volume (extensions,
schema, hypertables). Then apply the deferred Timescale features in `apply-later/` and
verify with the steps in [db/README.md](./db/README.md).

### 2. Server gateway — when built
```bash
cd server
cp .env.example .env          # DATABASE_URL=localhost, IMAGE_SVC_URL=<PC IP>, API_TOKEN=<shared>
```
Build the arm64 image and run it. Target: add it to a Pi5 `docker-compose.yml` next to
Postgres (so gateway→DB is localhost and it restarts with the box). Run DB migrations
(Alembic) on deploy.

### 3. Frontend — when built (served from the Pi5)
Build the Next.js app for arm64 and run it on the Pi5 (container or `next start`). It
holds the gateway token **server-side** (route handlers / server actions); the browser
never sees it. frontend→gateway is localhost on the Pi5. Your phone/browser hits the
Pi5's address.

### 4. image-svc — on the PC, on demand
Already runs bare-metal on the PC (Python 3.12 venv, `IMAGE_SVC_BACKEND=vlm`):
```powershell
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```
Make sure the Pi5's `server/.env` `IMAGE_SVC_URL` points at it and the `API_TOKEN`
matches. Leave the PC off whenever you don't need photo estimation.

### 5. (Optional) Reverse proxy + TLS on the Pi5
For one clean HTTPS entry point over the VPN, put Caddy/nginx on the Pi5: terminate TLS,
route `/` → frontend and `/api` → gateway. Optional for a plain trusted LAN; recommended
if you expose it over a VPN.

## The always-on stack (target shape)
Eventually a single `docker-compose.yml` on the Pi5 brings up **db + server + frontend**
(+ optional proxy) with `restart: unless-stopped`, so a power blip or reboot restores the
whole site unattended. Today only `db` has a compose file; the server/frontend compose
entries land with those components.

## Backups
Cron `pg_dump` on the Pi5 + copy off-device. It must **fail loudly** (log + non-zero
exit) so a silent/0-byte backup is noticeable — see [db/TODO.md](./db/TODO.md).

## Updating
```bash
git pull                      # on the Pi5
docker compose build          # rebuild changed images
docker compose up -d
```
`.env` files are gitignored, so `git pull` never touches your secrets or config.
Re-run DB migrations if the server shipped new ones.
