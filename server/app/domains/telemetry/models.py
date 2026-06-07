"""SQLAlchemy ORM models for telemetry, sleep, and body composition.

Mirrors db/initdb/02_schema.sql exactly (the DB contract). The base schema is
created by db/initdb (and stamped as Alembic baseline 0001); these models exist
so the server can read/write it and so Alembic has metadata to diff against.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Float,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Telemetry(Base):
    """Long/narrow time-series — one metric reading per row. Timescale hypertable
    (partitioned on ts via initdb/03). New metrics need no schema change.

    No surrogate PK in the DB; the unique (ts, metric, source) index is the
    identity and the ON CONFLICT target for idempotent ingest. Declared here as a
    composite primary key so the ORM has an identity to map.
    """

    __tablename__ = "telemetry"

    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    metric: Mapped[str] = mapped_column(Text, primary_key=True)
    source: Mapped[str] = mapped_column(Text, primary_key=True, server_default="samsung_health")
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(Text)


class SleepSession(Base):
    """One row per night (sparse). Regular table, not a hypertable."""

    __tablename__ = "sleep_sessions"
    __table_args__ = (
        UniqueConstraint("start_ts", name="sleep_sessions_start_ts_key"),
        CheckConstraint("end_ts > start_ts", name="sleep_sessions_check"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_min: Mapped[int | None] = mapped_column(Integer)
    deep_min: Mapped[int | None] = mapped_column(Integer)
    rem_min: Mapped[int | None] = mapped_column(Integer)
    light_min: Mapped[int | None] = mapped_column(Integer)
    awake_min: Mapped[int | None] = mapped_column(Integer)
    efficiency: Mapped[float | None] = mapped_column(Numeric(5, 2))


class BodyComposition(Base):
    """Periodic smart-scale readings. Sparse; regular table keyed by ts."""

    __tablename__ = "body_composition"

    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    body_fat_pct: Mapped[float | None] = mapped_column(Numeric(4, 1))
    skeletal_muscle_kg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    bmr_kcal: Mapped[int | None] = mapped_column(Integer)
