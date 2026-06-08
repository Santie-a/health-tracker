#!/bin/sh
# Run DB migrations on boot, then start the gateway (DEPLOY.md: "run migrations on
# deploy"). Baseline 0001 is an empty marker, so `upgrade head` is safe on an
# initdb-created DB (it just applies the extension migrations).
set -e

echo "[entrypoint] applying database migrations..."
alembic upgrade head

echo "[entrypoint] starting gateway..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
