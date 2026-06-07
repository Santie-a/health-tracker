"""DB-free tests for ingest routing and batch dedupe (the ON CONFLICT fix)."""

from __future__ import annotations

from app.domains.ingest import dispatch
from app.domains.ingest.samsung import codes
from app.domains.ingest.service import _dedupe


def _csv(data_type: str) -> bytes:
    # minimal: metadata line + a header line, no data rows
    return (f"{data_type},6320001,1\r\ncol\r\n").encode("utf-8-sig")


def test_dispatch_routes_known_types():
    assert dispatch.parse(codes.DT_WEIGHT, _csv(codes.DT_WEIGHT), {}).kind == "body_composition"
    assert dispatch.parse(codes.DT_STRESS, _csv(codes.DT_STRESS), {}).kind == "telemetry"
    assert dispatch.parse(codes.DT_EXERCISE, _csv(codes.DT_EXERCISE), {}).kind == "training_swim"


def test_dispatch_returns_none_for_stage_and_unknown():
    # sleep_stage is handled separately (enrichment), not via dispatch
    assert dispatch.parse(codes.DT_SLEEP_STAGE, _csv(codes.DT_SLEEP_STAGE), {}) is None
    assert dispatch.parse("com.samsung.shealth.something_else", _csv("x"), {}) is None


def test_dedupe_keeps_last_per_key():
    rows = [
        {"ts": 1, "metric": "stress", "source": "s", "value": 10},
        {"ts": 1, "metric": "stress", "source": "s", "value": 20},  # same key -> wins
        {"ts": 2, "metric": "stress", "source": "s", "value": 30},
    ]
    out = _dedupe(rows, lambda r: (r["ts"], r["metric"], r["source"]))
    assert len(out) == 2
    by_ts = {r["ts"]: r["value"] for r in out}
    assert by_ts == {1: 20, 2: 30}
