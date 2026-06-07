"""Shared test fixtures."""

from __future__ import annotations

import io

import pytest
from PIL import Image


def make_png(color: tuple[int, int, int] = (120, 60, 30), size: int = 32) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (size, size), color).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def png_bytes() -> bytes:
    return make_png()
