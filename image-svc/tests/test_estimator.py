from __future__ import annotations

import io

import pytest
from PIL import Image

from app.config import get_settings
from app.estimator import build_estimate
from app.estimator.base import Detection
from app.estimator.stub import StubEstimator
from nutrition_core import MacroTable

from .conftest import make_png


@pytest.fixture(scope="module")
def table() -> MacroTable:
    return MacroTable.from_csv(get_settings().macro_table_path)


@pytest.fixture(scope="module")
def stub(table: MacroTable) -> StubEstimator:
    return StubEstimator(get_settings(), table)


def _open(png: bytes) -> Image.Image:
    return Image.open(io.BytesIO(png)).convert("RGB")


def test_stub_is_deterministic(stub: StubEstimator):
    img = _open(make_png())
    first = stub.detect(img)
    second = stub.detect(_open(make_png()))
    assert first == second
    assert 1 <= len(first) <= 3


def test_stub_returns_known_foods(stub: StubEstimator, table: MacroTable):
    for det in stub.detect(_open(make_png((10, 200, 50)))):
        assert table.lookup(det.food) is not None
        assert det.grams_est > 0
        assert 0 <= det.confidence <= 1


def test_build_estimate_totals_match_items(stub: StubEstimator, table: MacroTable):
    detections = stub.detect(_open(make_png()))
    resp = build_estimate(detections, table, model_version="t", table_version="v")
    assert resp.totals.kcal == pytest.approx(sum(i.kcal for i in resp.items), abs=0.1)
    assert resp.totals.protein_g == pytest.approx(
        sum(i.protein_g for i in resp.items), abs=0.1
    )


def test_unmatched_food_kept_with_zero_macros(table: MacroTable):
    resp = build_estimate(
        [Detection(food="dragonfruit gizmo", grams_est=100, confidence=0.9)],
        table,
        model_version="t",
        table_version="v",
    )
    assert len(resp.items) == 1
    item = resp.items[0]
    assert "(unmatched)" in item.food
    assert item.kcal == 0.0
    assert item.confidence <= 0.3
