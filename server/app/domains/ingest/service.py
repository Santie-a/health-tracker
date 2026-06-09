"""Ingest orchestration: dispatch each uploaded file to its parser, then upsert.

Resilience:
- Each file is processed in its own savepoint (begin_nested), so a failure in one
  file rolls back only that file and the rest still commit.
- Parsers are row-resilient; this layer reports parsed/written/skipped per file.

Idempotency:
- telemetry  -> ON CONFLICT (ts, metric, source)
- body_comp  -> ON CONFLICT (ts)
- sleep      -> ON CONFLICT (start_ts)
- swims      -> no natural unique key in the schema; dedupe by (ts) among existing
  samsung swims (re-importing the same export does not duplicate).
"""

from __future__ import annotations

import logging

from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.nutrition.models import Meal  # noqa: F401  (ensure mappers configured)
from app.domains.telemetry.models import BodyComposition, SleepSession, Telemetry
from app.domains.training.models import TrainingSession

from . import dispatch
from .samsung import codes, parsers
from .samsung.reader import peek_data_type
from .schemas import FileReport, IngestResponse

log = logging.getLogger("server.ingest")

_CHUNK = 1000


def _dedupe(rows: list[dict], key) -> list[dict]:
    """Collapse rows sharing a conflict key (last wins). Required because Postgres
    ON CONFLICT DO UPDATE cannot affect the same row twice within one statement —
    and the watch emits multiple readings at the same timestamp."""
    out: dict = {}
    for r in rows:
        out[key(r)] = r
    return list(out.values())

_TARGET = {
    "telemetry": "telemetry",
    "body_composition": "body_composition",
    "sleep": "sleep_sessions",
    "training_swim": "training_sessions",
}


# --- upsert helpers -----------------------------------------------------------

async def _chunks(rows: list[dict]):
    for i in range(0, len(rows), _CHUNK):
        yield rows[i : i + _CHUNK]


async def _upsert_telemetry(session: AsyncSession, rows: list[dict]) -> int:
    rows = _dedupe(rows, lambda r: (r["ts"], r["metric"], r["source"]))
    written = 0
    async for chunk in _chunks(rows):
        stmt = pg_insert(Telemetry).values(chunk)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ts", "metric", "source"],
            set_={"value": stmt.excluded.value, "unit": stmt.excluded.unit},
        )
        await session.execute(stmt)
        written += len(chunk)
    return written


async def _upsert_body(session: AsyncSession, rows: list[dict]) -> int:
    rows = _dedupe(rows, lambda r: r["ts"])
    written = 0
    async for chunk in _chunks(rows):
        stmt = pg_insert(BodyComposition).values(chunk)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ts"],
            set_={
                "weight_kg": stmt.excluded.weight_kg,
                "body_fat_pct": stmt.excluded.body_fat_pct,
                "skeletal_muscle_kg": stmt.excluded.skeletal_muscle_kg,
                "bmr_kcal": stmt.excluded.bmr_kcal,
            },
        )
        await session.execute(stmt)
        written += len(chunk)
    return written


async def _upsert_sleep(session: AsyncSession, rows: list[dict]) -> int:
    rows = _dedupe(rows, lambda r: r["start_ts"])
    written = 0
    async for chunk in _chunks(rows):
        stmt = pg_insert(SleepSession).values(chunk)
        stmt = stmt.on_conflict_do_update(
            index_elements=["start_ts"],
            set_={
                "end_ts": stmt.excluded.end_ts,
                "total_min": stmt.excluded.total_min,
                "deep_min": stmt.excluded.deep_min,
                "rem_min": stmt.excluded.rem_min,
                "light_min": stmt.excluded.light_min,
                "awake_min": stmt.excluded.awake_min,
                "efficiency": stmt.excluded.efficiency,
            },
        )
        await session.execute(stmt)
        written += len(chunk)
    return written


async def _insert_swims(session: AsyncSession, rows: list[dict]) -> int:
    if not rows:
        return 0
    existing = set(
        (
            await session.execute(
                select(TrainingSession.ts).where(
                    TrainingSession.source == codes.SOURCE,
                    TrainingSession.type == "swim",
                )
            )
        ).scalars()
    )
    seen: set = set()
    fresh: list[dict] = []
    for r in rows:
        if r["ts"] in existing or r["ts"] in seen:
            continue
        seen.add(r["ts"])
        fresh.append(r)
    if fresh:
        await session.execute(insert(TrainingSession).values(fresh))
    return len(fresh)


_UPSERT = {
    "telemetry": _upsert_telemetry,
    "body_composition": _upsert_body,
    "sleep": _upsert_sleep,
    "training_swim": _insert_swims,
}


# --- orchestration ------------------------------------------------------------

async def ingest_files(session: AsyncSession, files: list[tuple[str, bytes]]) -> IngestResponse:
    # Pass 1: build the sleep-stage enrichment map from any sleep_stage file(s).
    stage_map: dict[str, dict[str, int]] = {}
    for filename, data in files:
        try:
            if peek_data_type(data) == codes.DT_SLEEP_STAGE:
                stage_map.update(parsers.parse_sleep_stage(data))
        except Exception:
            log.exception("Failed reading sleep_stage file %s", filename)

    reports: list[FileReport] = []
    for filename, data in files:
        report = FileReport(filename=filename)
        try:
            data_type = peek_data_type(data)
            report.data_type = data_type
        except Exception as exc:
            report.errors = [f"could not read file: {exc}"]
            reports.append(report)
            continue

        if data_type == codes.DT_SLEEP_STAGE:
            report.target = "(sleep enrichment — applied to sleep sessions)"
            report.parsed = len(stage_map)
            reports.append(report)
            continue

        result = dispatch.parse(data_type, data, stage_map)
        if result is None:
            report.target = "(unsupported — skipped)"
            reports.append(report)
            continue

        report.parsed = result.stats.ok
        report.skipped = result.stats.skipped
        report.errors = result.stats.errors
        report.target = _TARGET[result.kind]
        try:
            async with session.begin_nested():  # savepoint: isolate per-file failure
                report.written = await _UPSERT[result.kind](session, result.rows)
        except Exception as exc:
            log.exception("Upsert failed for %s (%s)", filename, data_type)
            report.errors = [*report.errors, f"write failed: {exc}"]
        reports.append(report)

    return IngestResponse(
        files=reports,
        parsed=sum(r.parsed for r in reports),
        written=sum(r.written for r in reports),
        skipped=sum(r.skipped for r in reports),
    )
