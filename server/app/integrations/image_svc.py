"""HTTP bridge to the GPU image service (food photo -> macro estimate).

Resilience contract (ARCHITECTURE.md): the GPU box is on-demand. On ANY failure
— not configured, connection refused, timeout, 5xx, bad body — this returns a
result with ``ok=False`` and the caller degrades to manual entry. It NEVER raises
to the request handler, so meal logging never 500s because the PC is off.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import httpx

from app.core.config import Settings

log = logging.getLogger("server.image_svc")

_RETRIES = 1  # one retry, but ONLY when the connection never landed (see estimate)


@dataclass
class EstimateResult:
    ok: bool
    items: list[dict] = field(default_factory=list)  # food, grams, kcal, protein_g, carbs_g, fat_g
    model_version: str | None = None
    table_version: str | None = None
    error: str | None = None


def map_items(data: dict) -> list[dict]:
    """Map image-svc's EstimateResponse items to our meal_item shape (grams_est->grams)."""
    items = []
    for it in data.get("items", []):
        items.append(
            {
                "food": it["food"],
                "grams": it.get("grams_est"),
                "kcal": it.get("kcal"),
                "protein_g": it.get("protein_g"),
                "carbs_g": it.get("carbs_g"),
                "fat_g": it.get("fat_g"),
            }
        )
    return items


async def estimate(
    settings: Settings, image: bytes, filename: str, content_type: str | None
) -> EstimateResult:
    if not settings.image_svc_url:
        return EstimateResult(ok=False, error="image-svc not configured")

    url = settings.image_svc_url.rstrip("/") + "/estimate"
    headers = {}
    if settings.api_token:
        headers["Authorization"] = f"Bearer {settings.api_token}"
    files = {"image": (filename, image, content_type or "application/octet-stream")}

    last_error = "unknown error"
    for attempt in range(_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.image_svc_timeout) as client:
                resp = await client.post(url, files=files, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return EstimateResult(
                    ok=True,
                    items=map_items(data),
                    model_version=data.get("model_version"),
                    table_version=data.get("table_version"),
                )
            # Any non-200 means image-svc already received and processed the request, so a
            # retry would re-run the (expensive, non-idempotent) GPU inference. 5xx (e.g.
            # model OOM) is the documented "degraded" signal — fall back, don't retry.
            last_error = f"image-svc returned {resp.status_code}"
            break
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            # Couldn't establish the connection — the request never reached image-svc, so
            # retrying is safe (e.g. the on-demand GPU box just came online).
            last_error = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            # Read timeout (inference still in flight), malformed body, or anything else:
            # the request may already be processing, so DON'T retry — degrade, never raise.
            last_error = f"{type(exc).__name__}: {exc}"
            break

    log.warning("image-svc unavailable (%s) — falling back to manual entry", last_error)
    return EstimateResult(ok=False, error=last_error)
