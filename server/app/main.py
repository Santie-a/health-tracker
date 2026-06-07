"""FastAPI entrypoint: app factory, lifespan, router registration, health checks.

This module wires cross-cutting concerns only — no domain logic. Domain routers
register themselves here as they land (telemetry, training, nutrition, ...).

Resilience: fail fast at startup on misconfiguration, survive at runtime. The
engine is created here but is lazy (no connection at boot), so liveness (/health)
never depends on the database; /health/ready does.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import __version__
from .core.config import get_settings
from .core.db import create_engine, create_sessionmaker, ping
from .core.errors import install_request_id_middleware, register_exception_handlers
from .core.logging_config import configure_logging
from .domains.ingest.router import router as ingest_router
from .domains.telemetry.router import router as telemetry_router

log = logging.getLogger("server")


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


class ReadyResponse(BaseModel):
    status: str  # "ok" | "degraded"
    database: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    engine = create_engine(settings.database_url)
    app.state.engine = engine
    app.state.sessionmaker = create_sessionmaker(engine)
    log.info("gateway started: version=%s log_level=%s", __version__, settings.log_level)

    try:
        yield
    finally:
        await engine.dispose()
        log.info("gateway stopped: engine disposed")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Health Tracker — API Gateway",
        version=__version__,
        lifespan=lifespan,
    )

    install_request_id_middleware(app)
    register_exception_handlers(app)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        """Liveness: process is up. Dependency-light (no DB) on purpose."""
        return HealthResponse(status="ok", version=__version__)

    @app.get("/health/ready", tags=["health"])
    async def ready() -> JSONResponse:
        """Readiness: checks the DB so orchestration can gate traffic without
        coupling liveness to it. 200 when ready, 503 when degraded."""
        db_ok = await ping(app.state.engine)
        body = ReadyResponse(status="ok" if db_ok else "degraded", database=db_ok)
        code = 200 if db_ok else 503
        return JSONResponse(status_code=code, content=body.model_dump())

    # Domain routers (all under /api/v1).
    app.include_router(telemetry_router, prefix="/api/v1")
    app.include_router(ingest_router, prefix="/api/v1")

    return app


app = create_app()
