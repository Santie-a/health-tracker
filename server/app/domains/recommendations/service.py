"""Recommendation orchestration: build context -> run engine -> store -> return.

The daily pass (``run_for_date``) is guarded so a failure is logged and never
propagates — a bad pass must not take the API down (ARCHITECTURE.md "Resilience").
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import date as date_cls

from sqlalchemy.ext.asyncio import AsyncSession

from . import repository, rules
from .schemas import RecommendationItem, RecommendationsOut

log = logging.getLogger("server.recommendations")


def _to_out(day: date_cls, payload: dict, generated_at=None) -> RecommendationsOut:
    return RecommendationsOut(
        date=day,
        generated_at=generated_at,
        recommendations=[RecommendationItem(**r) for r in payload.get("recommendations", [])],
        context=payload.get("context"),
    )


async def generate_for_date(
    session: AsyncSession, day: date_cls, store: bool = True
) -> RecommendationsOut:
    ctx = await repository.build_context(session, day)
    recs = rules.generate(ctx)
    payload = {
        "recommendations": [asdict(r) for r in recs],
        "context": asdict(ctx) | {"date": ctx.date.isoformat()},
    }
    if store:
        await repository.upsert(session, day, payload)
        row = await repository.get(session, day)  # re-read to surface generated_at
        if row is not None:
            return _to_out(day, row.payload, row.generated_at)
    return _to_out(day, payload)


async def get_for_date(session: AsyncSession, day: date_cls) -> RecommendationsOut:
    """Return the stored pass for the day, generating + storing it lazily if absent."""
    row = await repository.get(session, day)
    if row is not None:
        return _to_out(day, row.payload, row.generated_at)
    return await generate_for_date(session, day, store=True)


async def run_for_date(session: AsyncSession, day: date_cls) -> RecommendationsOut | None:
    """Guarded entrypoint for the scheduled daily pass: regenerate + store, but
    swallow+log any failure so the worker/loop continues."""
    try:
        return await generate_for_date(session, day, store=True)
    except Exception:
        log.exception("Daily recommendation pass failed for %s", day)
        return None


async def set_feedback(session: AsyncSession, day: date_cls, feedback: str) -> bool:
    return await repository.set_feedback(session, day, feedback)
