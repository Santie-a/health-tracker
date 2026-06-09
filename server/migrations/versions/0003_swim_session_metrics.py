"""swim/cardio session metrics for the Samsung exercise import

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-07

`training_sessions` had no home for the Samsung `exercise` import's calorie / HR /
distance (IMPLEMENTATION_PLAN.md task 1.4 / 3.2.8). Add nullable columns + a
`source` tag distinguishing watch-imported sessions from manually logged ones.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("training_sessions", sa.Column("kcal", sa.Numeric(7, 2)))
    op.add_column("training_sessions", sa.Column("avg_hr", sa.Integer()))
    op.add_column("training_sessions", sa.Column("max_hr", sa.Integer()))
    op.add_column("training_sessions", sa.Column("distance_m", sa.Numeric(8, 2)))
    op.add_column(
        "training_sessions",
        sa.Column("source", sa.Text(), nullable=False, server_default="manual"),
    )


def downgrade() -> None:
    op.drop_column("training_sessions", "source")
    op.drop_column("training_sessions", "distance_m")
    op.drop_column("training_sessions", "max_hr")
    op.drop_column("training_sessions", "avg_hr")
    op.drop_column("training_sessions", "kcal")
