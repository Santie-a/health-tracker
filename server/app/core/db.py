"""Async database engine, session factory, and the per-request session dependency.

The engine + sessionmaker are created once in the app lifespan and stored on
``app.state``; ``get_session`` hands out one session per request, committing on
success and rolling back on any error (one transaction per request).

``pool_pre_ping=True`` makes the pool validate a connection before handing it
out, so a dropped/stale connection (Pi5 box sleeping, db restart) is transparently
replaced instead of surfacing a hard error to the user.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(database_url: str) -> AsyncEngine:
    """Build the async engine. Lazy — does not connect until first use."""
    return create_async_engine(database_url, pool_pre_ping=True, future=True)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False so response serialization after commit doesn't
    # trigger surprise lazy-loads on detached attributes.
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Per-request session: commit on success, roll back on error."""
    sessionmaker: async_sessionmaker[AsyncSession] = request.app.state.sessionmaker
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def ping(engine: AsyncEngine) -> bool:
    """Best-effort connectivity check for /health/ready. Never raises."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
