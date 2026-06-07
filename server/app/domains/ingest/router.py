"""Thin HTTP layer for ingest. Accepts one or more Samsung export CSVs."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_token
from app.core.db import get_session

from . import service
from .schemas import IngestResponse

log = logging.getLogger("server.ingest")

router = APIRouter(prefix="/ingest", tags=["ingest"], dependencies=[Depends(require_token)])


@router.post("/samsung", response_model=IngestResponse)
async def ingest_samsung(
    files: list[UploadFile] = File(..., description="One or more Samsung Health export CSVs."),
    session: AsyncSession = Depends(get_session),
) -> IngestResponse:
    """Import complementary telemetry from a Samsung Health export.

    Routes each file by its metadata line-1 data type; unknown types are reported
    as skipped, not errors. Upload the sleep_stage file alongside sleep to enrich
    deep/awake stage minutes. Idempotent: re-uploading the same export is safe.
    """
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded.")
    payloads = [(f.filename or "upload.csv", await f.read()) for f in files]
    return await service.ingest_files(session, payloads)
