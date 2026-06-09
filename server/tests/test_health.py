"""Phase 0: liveness/readiness, request-id, and the consistent error shape."""

from __future__ import annotations

from app import __version__
from app.core.errors import REQUEST_ID_HEADER


def test_health_is_ok_and_dependency_light(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__


def test_every_response_carries_a_request_id(client):
    resp = client.get("/health")
    assert resp.headers.get(REQUEST_ID_HEADER)


def test_inbound_request_id_is_echoed(client):
    resp = client.get("/health", headers={REQUEST_ID_HEADER: "test-rid-123"})
    assert resp.headers.get(REQUEST_ID_HEADER) == "test-rid-123"


def test_404_uses_consistent_error_shape(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert "detail" in body
    assert "request_id" in body


def test_ready_reports_db_status(client):
    resp = client.get("/health/ready")
    body = resp.json()
    assert set(body) == {"status", "database"}
    # Status code and the database flag must agree, whether or not a db is up.
    assert (resp.status_code == 200) == (body["database"] is True)
    assert body["status"] == ("ok" if body["database"] else "degraded")
