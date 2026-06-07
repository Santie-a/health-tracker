"""Shared Samsung CSV reader (task 3.2.0) + timestamp helpers.

Samsung export quirks handled here, once, so every parser is simple:
- Line 1 is metadata: ``<data_type>,<version>,<column_count>`` — skipped, but its
  first cell is returned as the data type (used for dispatch).
- Line 2 is the real header; encoding is utf-8-sig (BOM).
- ``start_time`` columns are *local* text with a separate ``time_offset`` column
  (e.g. ``UTC-0500``); ``parse_local_ts`` combines them into an aware UTC datetime.
- ``day_time`` columns are epoch milliseconds (already UTC midnight of the day).
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

_MAX_REPORTED_ERRORS = 25


@dataclass
class ParseStats:
    """Row-resilience bookkeeping for one file."""

    ok: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    def skip(self, line_no: int, reason: str) -> None:
        self.skipped += 1
        if len(self.errors) < _MAX_REPORTED_ERRORS:
            self.errors.append(f"line {line_no}: {reason}")


def peek_data_type(data: bytes) -> str:
    """Read just the metadata line 1 and return the data-type identifier."""
    text = data.decode("utf-8-sig", errors="replace")
    first = text.split("\n", 1)[0]
    return first.split(",", 1)[0].strip()


def iter_rows(data: bytes):
    """Yield ``(line_no, row_dict)`` for each data row (header on line 2).

    line_no is the 1-based file line so error reports point at the real row.
    """
    buf = io.StringIO(data.decode("utf-8-sig"))
    buf.readline()  # skip metadata line 1
    reader = csv.DictReader(buf)  # consumes line 2 as header
    for offset, row in enumerate(reader, start=3):
        yield offset, row


# --- timestamp helpers --------------------------------------------------------

def parse_offset(offset: str) -> timedelta:
    """'UTC-0500' -> timedelta(hours=-5). 'UTC+0000' -> 0."""
    offset = offset.strip()
    if not offset.upper().startswith("UTC") or len(offset) < 8:
        raise ValueError(f"bad time_offset: {offset!r}")
    sign = -1 if offset[3] == "-" else 1
    hours = int(offset[4:6])
    minutes = int(offset[6:8])
    return timedelta(hours=sign * hours, minutes=sign * minutes)


def parse_local_ts(text: str, offset: str) -> datetime:
    """Combine local text time + offset column into an aware UTC datetime."""
    text = text.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            naive = datetime.strptime(text, fmt)
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"bad timestamp: {text!r}")
    local = naive.replace(tzinfo=timezone(parse_offset(offset)))
    return local.astimezone(timezone.utc)


def parse_epoch_ms(value: str) -> datetime:
    """Epoch-milliseconds string -> aware UTC datetime."""
    return datetime.fromtimestamp(int(float(value)) / 1000, tz=timezone.utc)


# --- value helpers ------------------------------------------------------------

def to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def to_int(value: str | None) -> int | None:
    f = to_float(value)
    return int(round(f)) if f is not None else None
