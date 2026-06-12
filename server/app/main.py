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

from nutrition_core import MacroTable, default_macro_csv

from . import __version__
from .core.config import get_settings
from .core.db import create_engine, create_sessionmaker, ping
from .core.errors import install_request_id_middleware, register_exception_handlers
from .core.logging_config import configure_logging
from .domains.dashboard.router import router as dashboard_router
from .domains.goals.router import router as goals_router
from .domains.ingest.router import router as ingest_router
from .domains.nutrition.foods_seed import seed_foods
from .domains.nutrition.router import foods_router
from .domains.nutrition.router import router as nutrition_router
from .domains.recommendations.router import router as recommendations_router
from .domains.telemetry.router import body_router as body_composition_router
from .domains.telemetry.router import router as telemetry_router
from .domains.training.router import exercises_router
from .domains.training.router import router as training_router
from .domains.training.seed import seed_exercises

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

    # Fail fast at startup if the shared macro table is missing/unreadable — a fixed
    # config + restart recovers it. Used for manual-entry macro resolution.
    try:
        app.state.macro_table = MacroTable.from_csv(default_macro_csv())
    except Exception:
        log.exception("Startup failed: could not load macro table from nutrition_core")
        raise

    # Seed the starter exercise catalog (idempotent by slug). Guarded — a seeding
    # failure (e.g. DB momentarily down) is logged but must not block startup.
    try:
        async with app.state.sessionmaker() as seed_session:
            ex_added = await seed_exercises(seed_session)
            food_added = await seed_foods(seed_session)
            await seed_session.commit()
        if ex_added or food_added:
            log.info("seeded catalog: exercises=%d foods=%d", ex_added, food_added)
    except Exception:
        log.exception("Catalog seeding failed (continuing without it)")

    log.info(
        "gateway started: version=%s log_level=%s foods=%d",
        __version__, settings.log_level, len(app.state.macro_table),
    )

    try:
        yield
    finally:
        await engine.dispose()
        log.info("gateway stopped: engine disposed")


def _use_binary_file_uploads(app: FastAPI) -> None:
    """Make Swagger UI render file-upload buttons for upload fields.

    FastAPI emits OpenAPI 3.1, which encodes uploads as ``contentMediaType``;
    Swagger UI's file widget only recognizes the 3.0-style ``format: binary`` and
    otherwise shows a plain text box (notably for ``list[UploadFile]`` arrays).
    This rewrites binary string schemas to advertise ``format: binary`` so the docs
    show real upload buttons. Documentation-only — request parsing is unaffected.
    """
    from fastapi.openapi.utils import get_openapi

    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title, version=app.version, routes=app.routes,
            description=app.description or None,
        )

        def walk(node) -> None:
            if isinstance(node, dict):
                if (
                    node.get("type") == "string"
                    and node.get("contentMediaType") == "application/octet-stream"
                    and "format" not in node
                ):
                    node["format"] = "binary"
                    node.pop("contentMediaType", None)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(schema)
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi


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
    app.include_router(body_composition_router, prefix="/api/v1")
    app.include_router(training_router, prefix="/api/v1")
    app.include_router(exercises_router, prefix="/api/v1")
    app.include_router(nutrition_router, prefix="/api/v1")
    app.include_router(foods_router, prefix="/api/v1")
    app.include_router(recommendations_router, prefix="/api/v1")
    app.include_router(goals_router, prefix="/api/v1")
    app.include_router(dashboard_router, prefix="/api/v1")
    app.include_router(ingest_router, prefix="/api/v1")

    _use_binary_file_uploads(app)
    return app


app = create_app()
