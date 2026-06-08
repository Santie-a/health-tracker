# Multi-arch image — the SAME Dockerfile builds for amd64 (PC dev) and arm64 (Pi5).
# All deps (fastapi/sqlalchemy/asyncpg/httpx) have prebuilt wheels for both, so no
# compiler/toolchain is needed on slim.
#
# Build context is the REPO ROOT (so the in-repo nutrition_core package is available):
#   docker build -f server/Dockerfile -t health-tracker-server .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app/server

# Shared package first (editable dep target), then requirements (better layer cache).
COPY packages /app/packages
COPY server/requirements.txt /app/server/requirements.txt
RUN pip install -r requirements.txt

# App code + migrations.
COPY server /app/server
RUN chmod +x /app/server/docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/server/docker-entrypoint.sh"]
