# Frontend (Next.js standalone) — multi-arch: the SAME Dockerfile builds for arm64 (Pi5)
# and amd64 (PC dev). Build context is THIS folder, unlike the server (which builds from
# the repo root for nutrition_core). The frontend has no cross-repo dependency.
#
#   docker build -t health-tracker-frontend ./frontend
#   # or, with the compose alongside it:
#   docker compose -f frontend/docker-compose.yml up -d --build
#
# Secrets stay OUT of the image: GATEWAY_URL / GATEWAY_TOKEN are read server-side at
# request time (see src/lib/env.ts), so they are RUNTIME env (frontend/.env), not build
# args. The build never needs the gateway.
#
# Base is glibc (bookworm-slim), not alpine: the native napi deps (unrs-resolver) ship
# glibc prebuilds, so we sidestep the musl-variant footguns on arm64. pnpm pinned to a
# major that reads lockfileVersion 9.0.

FROM node:22-bookworm-slim AS base
RUN npm install -g pnpm@11
WORKDIR /app

# ---- deps: install from the lockfile only (best layer cache) ----
# --ignore-scripts: sharp + unrs-resolver ship prebuilt binaries (they're in
# pnpm-workspace.yaml's ignoredBuiltDependencies), so their postinstall builds are skipped
# anyway; passing the flag also avoids pnpm 10/11's now-fatal ERR_PNPM_IGNORED_BUILDS.
FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile --ignore-scripts

# ---- builder: compile the standalone server bundle ----
# Invoke next directly (not `pnpm build`) so pnpm's verify-deps-before-run doesn't trigger
# an implicit re-install (which would re-raise the ignored-builds error).
FROM base AS builder
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN node_modules/.bin/next build

# ---- runner: minimal runtime, non-root, no node_modules (standalone carries its own) ----
FROM node:22-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

# `node` (uid 1000) ships with the base image — run unprivileged.
COPY --from=builder /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

USER node
EXPOSE 3000
CMD ["node", "server.js"]
