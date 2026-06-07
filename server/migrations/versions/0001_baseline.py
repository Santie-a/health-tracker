"""baseline — represents the db/initdb base schema

Revision ID: 0001
Revises:
Create Date: 2026-06-07

This is an intentionally EMPTY marker. The base relational schema (telemetry,
sleep_sessions, body_composition, training_sessions, training_sets, meals,
meal_items, recommendations) is created by db/initdb/*.sql — together with the
Timescale hypertable, continuous aggregate, and retention policy, which Alembic
does not manage.

Usage:
  - Existing DB (initdb already ran): `alembic stamp 0001` to mark it at baseline
    WITHOUT re-creating anything, then `alembic upgrade head` for the extensions.
  - The base DDL deliberately lives in ONE place (initdb) to avoid drift. A pure
    Alembic-only bring-up (no initdb) is not supported; the project standardizes
    on the db container.
"""
from __future__ import annotations

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
