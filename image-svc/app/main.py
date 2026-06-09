"""FastAPI entrypoint: food photo -> macro estimate.

Only the gateway calls this service; it is never exposed to the browser.
"""

from __future__ import annotations

import asyncio
import io
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from . import __version__
from .auth import require_token
from .config import Settings, get_settings
from .estimator import build_estimate, make_estimator
from .logging_config import configure_logging
from nutrition_core import MacroTable
from .schemas import EstimateResponse, HealthResponse

log = logging.getLogger("image_svc")

# Built once at startup, reused across requests.
_state: dict = {}


def _model_version(settings: Settings, backend_name: str) -> str:
    if backend_name == "vlm":
        return settings.model_version if settings.model_version != "stub-0" else settings.model_name
    return settings.model_version


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    # Startup misconfig (missing/empty macro table, unloadable model) should fail
    # fast — but with a clear, logged reason so the crash-loop is diagnosable.
    try:
        table = MacroTable.from_csv(settings.macro_table_path)
    except Exception:
        log.exception("Startup failed: could not load macro table from %s", settings.macro_table_path)
        raise

    estimator = make_estimator(settings, table)
    if settings.preload_model:
        try:
            estimator.warmup()
        except Exception:
            log.exception("Startup failed: model warmup error (backend=%s)", estimator.name)
            raise

    _state["settings"] = settings
    _state["table"] = table
    _state["estimator"] = estimator
    # Serialize access to the single GPU model: inference runs in a threadpool
    # (so it never blocks the event loop), but only one request at a time.
    _state["infer_lock"] = asyncio.Lock()
    log.info(
        "image-svc started: backend=%s preload=%s table_version=%s foods=%d",
        estimator.name, settings.preload_model, settings.table_version, len(table),
    )
    yield
    _state.clear()


app = FastAPI(title="Health Tracker — Image Service", version=__version__, lifespan=lifespan)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last line of defense: log the failure with context, return a clean 500.

    FastAPI's own handlers still serve HTTPException (415/413/400/401) with their
    intended status/detail; this only catches the genuinely unexpected so an error
    is always recorded and the process keeps serving the next request.
    """
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


def _cuda_info() -> tuple[bool, str | None]:
    """Best-effort CUDA probe; never fails if torch is absent (stub backend)."""
    try:
        import torch
    except ImportError:
        return False, None
    if not torch.cuda.is_available():
        return False, None
    return True, torch.cuda.get_device_name(0)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings: Settings = _state["settings"]
    estimator = _state["estimator"]
    cuda_available, device_name = _cuda_info()
    return HealthResponse(
        status="ok",
        backend=estimator.name,
        cuda_available=cuda_available,
        device_name=device_name,
        model=settings.model_name if estimator.name == "vlm" else "stub",
        model_loaded=estimator.loaded,
    )


@app.post("/estimate", response_model=EstimateResponse, dependencies=[Depends(require_token)])
async def estimate(image: UploadFile = File(...)) -> EstimateResponse:
    settings: Settings = _state["settings"]
    estimator = _state["estimator"]

    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Expected an image, got {image.content_type}.",
        )

    raw = await image.read()
    max_bytes = int(settings.max_image_mb * 1024 * 1024)
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Image exceeds {settings.max_image_mb} MB limit.",
        )

    from PIL import Image as PILImage, UnidentifiedImageError

    # Bound decoded pixels too (a small file can expand to gigapixels).
    PILImage.MAX_IMAGE_PIXELS = settings.max_image_pixels

    try:
        pil = PILImage.open(io.BytesIO(raw))
        pil.load()
        pil = pil.convert("RGB")
    except PILImage.DecompressionBombError:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Image exceeds the {settings.max_image_pixels}-pixel limit.",
        )
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode the uploaded image.",
        )

    # Offload the blocking GPU inference so the event loop stays responsive
    # (e.g. /health), serialized so concurrent uploads don't contend on the model.
    # Any inference failure (model load, CUDA OOM) is logged and surfaced as 503 so
    # the gateway treats it as "degraded -> manual entry" rather than a hard error.
    try:
        async with _state["infer_lock"]:
            detections = await run_in_threadpool(estimator.detect, pil)
    except Exception:
        log.exception("Inference failed (backend=%s)", estimator.name)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Estimator temporarily unavailable; fall back to manual entry.",
        )
    return build_estimate(
        detections,
        _state["table"],
        model_version=_model_version(settings, estimator.name),
        table_version=settings.table_version,
    )
