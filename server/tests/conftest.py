"""Shared test fixtures.

Tests run against the app factory with a TestClient; the engine is lazy so no
real database is needed for Phase 0 (liveness, error-shape, auth) tests.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    # `with` triggers lifespan (engine + sessionmaker setup/teardown).
    with TestClient(create_app()) as c:
        yield c
