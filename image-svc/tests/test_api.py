from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings

from .conftest import make_png


@pytest.fixture
def client(monkeypatch):
    # Blank the token (an env var wins over the real .env) to test the no-auth path.
    monkeypatch.setenv("IMAGE_SVC_API_TOKEN", "")
    monkeypatch.setenv("IMAGE_SVC_BACKEND", "stub")
    get_settings.cache_clear()
    from app.main import app

    with TestClient(app) as c:
        yield c
    get_settings.cache_clear()


@pytest.fixture
def authed_client(monkeypatch):
    monkeypatch.setenv("IMAGE_SVC_API_TOKEN", "secret-token")
    monkeypatch.setenv("IMAGE_SVC_BACKEND", "stub")
    get_settings.cache_clear()
    from app.main import app

    with TestClient(app) as c:
        yield c
    get_settings.cache_clear()


def test_health(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["backend"] == "stub"
    assert "cuda_available" in body


def test_estimate_returns_valid_schema(client: TestClient):
    resp = client.post("/estimate", files={"image": ("plate.png", make_png(), "image/png")})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["items"], "expected at least one item"
    assert body["table_version"]
    for item in body["items"]:
        assert set(item) == {
            "food", "grams_est", "kcal", "protein_g", "carbs_g", "fat_g", "confidence",
        }
    # Totals are the sum of items.
    assert body["totals"]["kcal"] == pytest.approx(
        sum(i["kcal"] for i in body["items"]), abs=0.2
    )


def test_estimate_rejects_non_image(client: TestClient):
    resp = client.post("/estimate", files={"image": ("notes.txt", b"hello", "text/plain")})
    assert resp.status_code == 415


def test_estimate_rejects_undecodable_image(client: TestClient):
    resp = client.post(
        "/estimate", files={"image": ("broken.png", b"not really a png", "image/png")}
    )
    assert resp.status_code == 400


def test_estimate_rejects_decompression_bomb(client: TestClient, monkeypatch):
    # A tiny file that decodes to a huge image must be rejected (413), not OOM the box.
    from app.main import _state

    monkeypatch.setattr(_state["settings"], "max_image_pixels", 1024)  # 32x32 > 1024 px
    resp = client.post("/estimate", files={"image": ("plate.png", make_png(size=64), "image/png")})
    assert resp.status_code == 413


def test_estimate_returns_503_on_inference_failure(client: TestClient, monkeypatch):
    # A model/CUDA failure mid-request must degrade to 503 (gateway -> manual entry),
    # not an opaque 500 or a process crash.
    from app.main import _state

    def boom(_image):
        raise RuntimeError("simulated CUDA OOM")

    monkeypatch.setattr(_state["estimator"], "detect", boom)
    resp = client.post("/estimate", files={"image": ("plate.png", make_png(), "image/png")})
    assert resp.status_code == 503
    assert "manual" in resp.json()["detail"].lower()


def test_unexpected_error_returns_clean_500(monkeypatch):
    # Anything unexpected after inference hits the global handler: clean 500, no
    # stack trace leaked. raise_server_exceptions=False so the client returns the
    # handler's response instead of re-raising.
    monkeypatch.setenv("IMAGE_SVC_API_TOKEN", "")
    monkeypatch.setenv("IMAGE_SVC_BACKEND", "stub")
    get_settings.cache_clear()
    import app.main as main

    with TestClient(main.app, raise_server_exceptions=False) as c:
        monkeypatch.setattr(main, "build_estimate", lambda *a, **k: 1 / 0)
        resp = c.post("/estimate", files={"image": ("plate.png", make_png(), "image/png")})
    get_settings.cache_clear()
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error."}


def test_auth_enforced_when_token_set(authed_client: TestClient):
    files = {"image": ("plate.png", make_png(), "image/png")}
    assert authed_client.post("/estimate", files=files).status_code == 401
    ok = authed_client.post(
        "/estimate", files=files, headers={"Authorization": "Bearer secret-token"}
    )
    assert ok.status_code == 200
    # Health stays open (no auth) for liveness checks.
    assert authed_client.get("/health").status_code == 200
