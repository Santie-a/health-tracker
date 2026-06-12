"""goals: user objectives (lean bulk / gain weight / sleep) that steer recommendations

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-11

Adds the `goals` table. A goal records the user's *intent* (gain muscle, gain
weight, lose fat, recomp, maintain, improve sleep) plus an optional measurable
target (a body-composition or sleep metric, a target value/date, and/or a weekly
rate). This is the keystone the recommendation engine was missing — until now
`rule_calorie_balance` could only *describe* the energy balance because "the
user's cut/bulk intent is unknown" (rules.py). With an active goal the same
signals become directional.

A partial unique index enforces at most one active goal per `category` (body /
sleep), so the engine derives a single, unambiguous set of thresholds.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


GOAL_TYPES = ("gain_muscle", "gain_weight", "lose_fat", "recomp", "maintain", "improve_sleep")
GOAL_STATUS = ("active", "achieved", "abandoned")
GOAL_CATEGORIES = ("body", "sleep")


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        # measurable target (all optional — a goal can be qualitative intent only)
        sa.Column("metric", sa.Text(), nullable=True),  # weight_kg | skeletal_muscle_kg | body_fat_pct | sleep_min | sleep_efficiency
        sa.Column("baseline_value", sa.Numeric(7, 2), nullable=True),
        sa.Column("target_value", sa.Numeric(7, 2), nullable=True),
        sa.Column("target_rate_per_week", sa.Numeric(6, 3), nullable=True),  # e.g. +0.25 kg/wk
        sa.Column("start_date", sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column("target_date", sa.Date(), nullable=True),
        # nutrition knobs the engine reads (override the defaults in thresholds.py)
        sa.Column("calorie_delta", sa.Integer(), nullable=True),  # surplus(+)/deficit(-) vs TDEE
        sa.Column("protein_g_per_kg", sa.Numeric(4, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "type IN ('gain_muscle','gain_weight','lose_fat','recomp','maintain','improve_sleep')",
            name="goals_type_check",
        ),
        sa.CheckConstraint("category IN ('body','sleep')", name="goals_category_check"),
        sa.CheckConstraint(
            "status IN ('active','achieved','abandoned')", name="goals_status_check"
        ),
    )
    # At most one active goal per category, so the engine derives unambiguous thresholds.
    op.create_index(
        "goals_one_active_per_category",
        "goals",
        ["category"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index("goals_status_idx", "goals", ["status"])


def downgrade() -> None:
    op.drop_index("goals_status_idx", table_name="goals")
    op.drop_index("goals_one_active_per_category", table_name="goals")
    op.drop_table("goals")
