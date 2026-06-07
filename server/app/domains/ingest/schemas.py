"""Response models for the ingest API — a per-file report + totals."""

from __future__ import annotations

from pydantic import BaseModel


class FileReport(BaseModel):
    filename: str
    data_type: str | None = None
    target: str | None = None  # table or note
    parsed: int = 0   # rows successfully parsed
    written: int = 0  # rows upserted/inserted
    skipped: int = 0  # malformed rows skipped
    errors: list[str] = []


class IngestResponse(BaseModel):
    files: list[FileReport]
    parsed: int
    written: int
    skipped: int
