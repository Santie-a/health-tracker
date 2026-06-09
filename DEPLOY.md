# Health Tracker — Deployment

How the pieces get onto hardware, in what order, and how secrets (`.env`) are
handled per machine. See [ARCHITECTURE.md](./ARCHITECTURE.md) for the why.

> **Read this first if you're the Claude Code agent.** The Pi5 is not a blank box.
> It already runs a small homelab (Docker on an SSD, a Dockge manager, a shared Caddy
> reverse proxy, Tailscale, and Pi-hole). The conventions below are not suggestions —
> they are how this host is wired. Place things where this document says, and plug into
> the existing proxy/DNS instead of standing up new ones. See
> [Notes for the Claude Code agent](#notes-for-the-claude-code-agent).

---

## Pi5 host environment (already provisioned)

The Pi5 host is set up and these facts are stable. Treat them as the deployment target.

**Hardware / OS**
- Raspberry Pi 5 (8 GB), **arm64**. All images must be arm64 (build on the Pi or pull
  multi-arch tags).
- Root filesystem is on the microSD; **all container data lives on a USB SSD** mounted
  at `/mnt/ssd` (ext4, mounted by UUID in `/etc/fstab` with `nofail`).
- Networking is managed by **NetworkManager + netplan** (not `dhcpcd`). `eth0` has a
  **static IP `192.168.20.51/24`**, gateway `192.168.20.1`. Wired, not Wi-Fi.

**Storage layout — put things here**
```
/mnt/ssd/
├── docker/                     # Docker data-root (images, named volumes). Docker-managed; do not touch by hand.
├── stacks/                     # one folder per stack = its compose.yaml (+ .env, Dockerfile, source). Managed by Dockge.
│   ├── dockge/
│   ├── caddy/                  # the shared reverse proxy + its Caddyfile
│   ├── pihole/
│   └── health-tracker/         # THIS project goes here
└── appdata/                    # persistent bind-mount data per service (configs, DB files)
    └── health-tracker/
        └── db/                 # Postgres/Timescale data dir
```
Convention: **definitions in `stacks/<name>/`, persistent data in `appdata/<name>/`.**
Prefer bind mounts into `appdata/` over anonymous named volumes so data is visible and
easy to back up.

**Container management**
- **Docker Engine + Compose plugin**, data-root relocated to `/mnt/ssd/docker`
  (`/etc/docker/daemon.json`).
- **Dockge** is the web UI for stacks (`http://dockge.homeserver.internal`, or
  `:5001`). Each stack is a real `compose.yaml` on disk under `/mnt/ssd/stacks/`, so you
  can edit by hand over SSH *or* via Dockge — they stay in sync.
- Kernel cgroup memory accounting is enabled (`cgroup_enable=memory cgroup_memory=1` in
  `/boot/firmware/cmdline.txt`), so per-container `mem_limit` works. Set sane limits on
  an 8 GB box.

**Reverse proxy + shared network**
- A single **Caddy** instance fronts everything on ports 80/443. Stack:
  `/mnt/ssd/stacks/caddy/`, config: `/mnt/ssd/stacks/caddy/Caddyfile`.
- There is an external Docker network named **`proxy`**. Any web-facing container joins
  it; Caddy reaches backends by **container name : internal port** over that network, so
  **fronted services do not publish ports to the host** (only Caddy does).
- Caddy uses plain-HTTP `http://name.homeserver.internal { … }` blocks (no public certs
  for a private `.internal` domain). Internal TLS via Caddy's local CA can be added later.

**DNS & access**
- **Tailscale** runs on the host (and on the PC and phone). The Pi's MagicDNS name is
  `raspberrypi-homeserver`; its Tailscale IP is `100.x.y.z` (call it `<PI_TS_IP>`).
- The private naming domain is **`homeserver.internal`** (ICANN-reserved for private use).
- **Pi-hole** holds the local DNS records: `*.homeserver.internal → <PI_TS_IP>`. Tailscale
  is configured with **Split DNS** so the tailnet sends `homeserver.internal` queries to
  Pi-hole. Net effect: any device on Tailscale (phone, PC) resolves the service names and
  reaches Caddy over the VPN — at home or remote — with no router/DHCP changes (the ISP
  gateway's DHCP is locked, so we do not rely on it).
- SSH is **key-only** (password auth disabled); alias `homeserver` in `~/.ssh/config`.

**Quick reference**
| Thing                         | Value |
|-------------------------------|-------|
| Stack dir for this project    | `/mnt/ssd/stacks/health-tracker/` |
| Persistent data               | `/mnt/ssd/appdata/health-tracker/db/` |
| Shared proxy network          | `proxy` (external) |
| Caddyfile                     | `/mnt/ssd/stacks/caddy/Caddyfile` |
| Naming domain                 | `homeserver.internal` |
| Pi static LAN IP              | `192.168.20.51` |
| Pi Tailscale name / IP        | `raspberrypi-homeserver` / `<PI_TS_IP>` |
| PC (image-svc) address        | `<PC_TS_NAME>` (Tailscale name) |

---

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

On the Pi5, the three always-on components share one internal Docker network. Only the
**frontend** additionally joins the external `proxy` network so Caddy can serve it by
name; `db` and `server` stay internal and are never published beyond the Pi.

---

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
  IMAGE_SVC_URL=http://localhost:8001            # image-svc is local during dev

  # server/.env on the Pi5 (prod)
  DATABASE_URL=postgresql+asyncpg://health:<pw>@localhost:5432/health_tracker  # db = same host
  IMAGE_SVC_URL=http://<PC_TS_NAME>:8001         # image-svc lives on the PC, reached over Tailscale
  ```

- **One value must match across machines:** `API_TOKEN`. The PC's `image-svc/.env`
  and the Pi5's `server/.env` must carry the *same* token — it's the shared secret the
  gateway sends to the image service.

### Getting the values onto the Pi5
Pick either (single-user homelab, both fine):
- **Recreate (recommended):** on the Pi5, `cp <component>/.env.example <component>/.env`
  and fill it in by hand. Nothing sensitive leaves your SSH session.
- **Copy then edit:** `scp server/.env homeserver:/mnt/ssd/stacks/health-tracker/server/.env`,
  then edit the host-specific values (`IMAGE_SVC_URL`, etc.). You rarely copy verbatim.
  (`homeserver` is the SSH alias; it resolves over Tailscale, so this works remotely too.)

Never `git add` a `.env`. The root `.gitignore` already blocks it; the verification
step below double-checks.

---

## Networking

- Everything is reached over the **LAN or Tailscale**. **Do not port-forward any service
  to the internet.** The ISP gateway's admin (and its DHCP) is locked, so Tailscale is the
  access path, not router config.
- The Pi5 reaches the PC's `image-svc` by a **stable Tailscale name** (`<PC_TS_NAME>`),
  not a LAN IP. The PC is on-demand; its Tailscale name is stable across reboots and
  networks, where a DHCP LAN address is not. Put that name in the Pi5's `server/.env`
  `IMAGE_SVC_URL`.
- `DB_BIND_ADDR=127.0.0.1` on the Pi5 is correct and safest: db, gateway, and frontend
  are all on the Pi5, so nothing needs Postgres exposed beyond localhost. (If you later
  unify everything into one compose, addressing the db by service name `db:5432` on the
  project's internal network is an equally valid alternative — pick one and be consistent.)
- The **frontend** is the only component exposed publicly-by-name, through the shared
  Caddy at `http://health.homeserver.internal`. The browser only ever talks to the
  frontend; the frontend talks to the gateway server-side over localhost, so the gateway
  token never reaches the browser and the gateway needs no Caddy route of its own.

---

## Deployment order

> Status: all three components (db, server, frontend) are built and wired into one stack
> (the root `docker-compose.yml`). image-svc runs separately on the PC.

### 0. Pi5 prep — already done
The host is provisioned: arm64 OS, SSD at `/mnt/ssd`, Docker with data-root on the SSD,
Dockge, the `proxy` network, Caddy, Tailscale, and Pi-hole are all up. So for this
project you only need to:
- `git clone` the repo into `/mnt/ssd/stacks/health-tracker/`. (No `.env` files come
  with it — expected.)
- Confirm the `proxy` network exists: `docker network ls | grep proxy` (it does).

### 1. Fill in the three `.env` files
One per component, each from its `.env.example`. In the unified stack, **cross-service URLs
use the docker service name, never `localhost`** (inside a container `localhost` is that
container):
```bash
cd /mnt/ssd/stacks/health-tracker
cp db/.env.example       db/.env        # POSTGRES_USER=health, a strong POSTGRES_PASSWORD, DB_BIND_ADDR=127.0.0.1
cp server/.env.example   server/.env    # DATABASE_URL=...@db:5432/...  IMAGE_SVC_URL=http://<PC_TS_NAME>:8001  API_TOKEN=<shared>
cp frontend/.env.example frontend/.env  # GATEWAY_URL=http://server:8000  GATEWAY_TOKEN=<same as server API_TOKEN>
```
`API_TOKEN` (server) and `GATEWAY_TOKEN` (frontend) must match; that same token is what the
PC's `image-svc/.env` expects too.

### 2. Bring up the whole stack
```bash
cd /mnt/ssd/stacks/health-tracker
docker compose up -d --build      # builds arm64 images on the Pi, starts db → server → frontend
```
Order is handled for you: the server waits for the db healthcheck, then its entrypoint runs
`alembic upgrade head` (idempotent) before uvicorn; the frontend starts after the server.
The `initdb/*.sql` runs once on the first boot of an empty volume (extensions, schema,
hypertables) — then apply the deferred Timescale features in `db/apply-later/` and verify
per [db/README.md](./db/README.md). Only the frontend is on the `proxy` network; db and
server are internal (db also publishes `127.0.0.1:5432` for host-side backups only).

### 3. Expose the frontend through the shared Caddy
The `frontend` container is already on the `proxy` network with no published port. Wire it
to the proxy + DNS (see [Exposing a service through the shared Caddy](#exposing-a-service-through-the-shared-caddy)):
1. Add to the shared Caddyfile:
   ```
   http://health.homeserver.internal {
       reverse_proxy frontend:3000
   }
   ```
2. `caddy validate` + `caddy reload` (don't restart the container).
3. Add the Pi-hole record `health.homeserver.internal → <PI_TS_IP>`.

Your phone/PC then hits `http://health.homeserver.internal` over Tailscale. The browser only
ever talks to the frontend; the frontend reaches the gateway server-side as `server:8000`,
so the token never leaves the Pi.

### 4. image-svc — on the PC, on demand
Already runs bare-metal on the PC (Python 3.12 venv, `IMAGE_SVC_BACKEND=vlm`):
```powershell
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```
Make sure the Pi5's `server/.env` `IMAGE_SVC_URL` points at the PC's Tailscale name
(`http://<PC_TS_NAME>:8001`) and the `API_TOKEN` matches. Leave the PC off whenever you
don't need photo estimation.

### 5. Reverse proxy + TLS — already handled by the shared Caddy
You do **not** stand up a per-project proxy. The Pi5's existing Caddy is the single entry
point; the frontend plugs into it as in step 3. If you later want HTTPS for `.internal`
names, enable Caddy's internal CA (`tls internal`) and trust its root on your devices —
do it once in the shared Caddy, not per project.

---

## Exposing a service through the shared Caddy

Reference for adding any new fronted service (replace `miapp` / port `8000`):

1. **Join the `proxy` network** in the service's compose, and don't publish its port:
   ```yaml
   services:
     miapp:
       image: ...
       container_name: miapp
       restart: unless-stopped
       networks:
         - proxy
   networks:
     proxy:
       external: true
   ```
2. **Add a Caddy block** (the Caddyfile is root-owned; edit over SSH):
   ```bash
   sudo nano /mnt/ssd/stacks/caddy/Caddyfile
   ```
   ```
   http://miapp.homeserver.internal {
       reverse_proxy miapp:8000
   }
   ```
   Target is **container-name : internal-port**, reachable over the `proxy` network.
3. **Validate and hot-reload Caddy** (no downtime; bad config is rejected and the old one
   keeps running):
   ```bash
   docker exec caddy caddy validate --config /etc/caddy/Caddyfile
   docker exec caddy caddy reload   --config /etc/caddy/Caddyfile
   ```
4. **Add the Pi-hole record** `miapp.homeserver.internal → <PI_TS_IP>` under
   *Local DNS Records*. (A wildcard `*.homeserver.internal` can replace this step later;
   not set up yet.)

---

## Editing files on the Pi (sudo nano + shortcuts)

Most config under `/mnt/ssd/stacks/**` and system files are root-owned, so use `sudo`.

**nano keys** (`^` = Ctrl):
- `^O` then `Enter` — save (write Out)
- `^X` — exit
- `^W` — search; `^\` — search & replace
- `^K` cut line · `^U` paste · `Alt+U` undo · `Alt+E` redo
- `^_` — go to line:column · `^G` — help
- Tip: nano can silently break single-line files (like `cmdline.txt`). For those, prefer
  the non-interactive overwrite below.

**Back up before editing anything important:**
```bash
sudo cp /path/file /path/file.bak
```

**Overwrite a whole file non-interactively** (what we use for compose/Caddyfile; safe for
the agent because it's deterministic):
```bash
sudo tee /mnt/ssd/stacks/caddy/Caddyfile > /dev/null <<'EOF'
http://health.homeserver.internal {
    reverse_proxy frontend:3000
}
EOF
```
The quoted `'EOF'` prevents shell expansion inside the heredoc — important when content
contains `$`.

**Append a single line** (e.g., a kernel flag, idempotent-check first):
```bash
echo 'SOMELINE' | sudo tee -a /path/file
```

**Common paths**
| File | Path |
|------|------|
| Caddy config | `/mnt/ssd/stacks/caddy/Caddyfile` |
| A stack's compose | `/mnt/ssd/stacks/<name>/compose.yaml` |
| A stack's secrets | `/mnt/ssd/stacks/<name>/.env` |
| Docker daemon | `/etc/docker/daemon.json` |
| Mounts | `/etc/fstab` |
| Kernel cmdline | `/boot/firmware/cmdline.txt` (must stay one line) |

---

## Notes for the Claude Code agent

Hard rules for this host — follow them, don't re-derive:

- **Data lives on the SSD.** New persistent data goes under `/mnt/ssd/appdata/<name>/`,
  stacks under `/mnt/ssd/stacks/<name>/`. Never write container data to the microSD or
  to `/var/lib/docker` (the data-root is `/mnt/ssd/docker`).
- **Don't publish ports for fronted services.** Join the `proxy` network and let Caddy
  reach them by `container-name:port`. Only Caddy binds 80/443.
- **One reverse proxy.** Add a block to the existing Caddyfile + a Pi-hole record; never
  spin up a second proxy.
- **After editing the Caddyfile**, always `caddy validate` then `caddy reload` via
  `docker exec caddy …` — don't restart the container unless reload fails.
- **arm64 only.** Build on the Pi or use multi-arch images.
- **Pin image versions** (e.g. `postgres:16-alpine`, `caddy:2`) — avoid `:latest` so a
  recreate can't pull a breaking major version.
- **Networking is netplan + NetworkManager.** Do not suggest `dhcpcd`/`/etc/dhcpcd.conf`.
  The static IP lives in the NM connection; `eth0` is `192.168.20.51`.
- **Secrets:** never commit a `.env`; create it per host from `.env.example`. The
  `API_TOKEN` must match between the PC's `image-svc/.env` and the Pi5's `server/.env`.
- **DB stays local:** `DB_BIND_ADDR=127.0.0.1`; the gateway is internal; only the
  frontend is exposed by name.
- **Reach the PC's image-svc by Tailscale name** (`<PC_TS_NAME>`), not a LAN IP, and
  treat it as optionally-offline (graceful degradation to manual meal entry).

---

## The always-on stack

The root `docker-compose.yml` (a Dockge stack at `/mnt/ssd/stacks/health-tracker/`) brings
up **db + server + frontend** on a shared internal `backend` network (frontend also on the
`proxy` network) with `restart: unless-stopped`, so a power blip or reboot restores the
whole site unattended. Services address each other by name (`db:5432`, `server:8000`);
startup is ordered via the db healthcheck + `depends_on`. The per-component compose files
(`db/`, `server/`, `frontend/`) remain for running a single piece in isolation during dev —
use those **or** the root stack, not both at once (they share the `health-tracker-pgdata`
volume and container names).

---

## Backups

Cron `pg_dump` on the Pi5 + copy off-device (the dump and any off-device copy should land
on `/mnt/ssd` or an external target, not the microSD). It must **fail loudly** (log +
non-zero exit) so a silent/0-byte backup is noticeable — see [db/TODO.md](./db/TODO.md).

---

## Updating
```bash
ssh homeserver
cd /mnt/ssd/stacks/health-tracker
git pull                      # secrets untouched: .env is gitignored
docker compose build          # rebuild changed images (arm64, on the Pi)
docker compose up -d
```
Or redeploy the stack from Dockge. `.env` files are gitignored, so `git pull` never
touches your secrets or config. Re-run DB migrations if the server shipped new ones.
After any Caddyfile change, `caddy validate` + `caddy reload` as above.