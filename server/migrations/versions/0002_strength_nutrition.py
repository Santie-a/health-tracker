"""strength catalog + serving-based nutrition (db/TODO.md additions)

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-07

Adds the exercise catalog + muscle taxonomy and the foods/portions catalog, plus
the per-set and per-item columns that link logged data to them. All additions are
nullable / defaulted so existing free-text logging keeps working unchanged.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- exercise catalog ----------------------------------------------------
    op.create_table(
        "exercises",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("category", sa.Text()),
        sa.Column("primary_muscle", sa.Text()),
        sa.Column("equipment", sa.Text()),
        sa.Column("is_unilateral", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_bodyweight", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("aliases", postgresql.ARRAY(sa.Text())),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("slug", name="exercises_slug_key"),
        sa.CheckConstraint(
            "category IN ('push','pull','squat','hinge','carry','core','swim','other')",
            name="exercises_category_check",
        ),
    )

    op.create_table(
        "exercise_muscles",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("exercise_id", sa.BigInteger(), nullable=False),
        sa.Column("muscle", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False, server_default="primary"),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["exercises.id"], ondelete="CASCADE",
            name="exercise_muscles_exercise_id_fkey",
        ),
        sa.UniqueConstraint("exercise_id", "muscle", name="exercise_muscles_uq"),
        sa.CheckConstraint("role IN ('primary','secondary')", name="exercise_muscles_role_check"),
    )

    # --- foods catalog -------------------------------------------------------
    op.create_table(
        "foods",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.Text())),
        sa.Column("kcal_100g", sa.Numeric(7, 2)),
        sa.Column("protein_100g", sa.Numeric(6, 2)),
        sa.Column("carbs_100g", sa.Numeric(6, 2)),
        sa.Column("fat_100g", sa.Numeric(6, 2)),
        sa.Column("default_grams", sa.Numeric(7, 2)),
        sa.Column("table_version", sa.Text()),
        sa.UniqueConstraint("slug", name="foods_slug_key"),
    )

    op.create_table(
        "food_portions",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("food_id", sa.BigInteger(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("grams", sa.Numeric(7, 2), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(
            ["food_id"], ["foods.id"], ondelete="CASCADE",
            name="food_portions_food_id_fkey",
        ),
    )

    # --- training_sets extensions -------------------------------------------
    op.add_column("training_sets", sa.Column("exercise_id", sa.BigInteger()))
    op.add_column(
        "training_sets",
        sa.Column("is_warmup", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("training_sets", sa.Column("rpe", sa.Numeric(3, 1)))
    op.add_column("training_sets", sa.Column("added_weight_kg", sa.Numeric(6, 2)))
    op.create_foreign_key(
        "training_sets_exercise_id_fkey", "training_sets", "exercises",
        ["exercise_id"], ["id"],
    )
    op.create_index("training_sets_exercise_id_idx", "training_sets", ["exercise_id"])

    # --- meal_items extensions ----------------------------------------------
    op.add_column("meal_items", sa.Column("food_id", sa.BigInteger()))
    op.add_column("meal_items", sa.Column("qty", sa.Numeric(6, 2)))
    op.add_column("meal_items", sa.Column("portion_label", sa.Text()))
    op.add_column(
        "meal_items",
        sa.Column("estimated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("meal_items", sa.Column("source", sa.Text()))
    op.create_foreign_key(
        "meal_items_food_id_fkey", "meal_items", "foods", ["food_id"], ["id"],
    )
    op.create_index("meal_items_food_id_idx", "meal_items", ["food_id"])


def downgrade() -> None:
    op.drop_index("meal_items_food_id_idx", table_name="meal_items")
    op.drop_constraint("meal_items_food_id_fkey", "meal_items", type_="foreignkey")
    op.drop_column("meal_items", "source")
    op.drop_column("meal_items", "estimated")
    op.drop_column("meal_items", "portion_label")
    op.drop_column("meal_items", "qty")
    op.drop_column("meal_items", "food_id")

    op.drop_index("training_sets_exercise_id_idx", table_name="training_sets")
    op.drop_constraint("training_sets_exercise_id_fkey", "training_sets", type_="foreignkey")
    op.drop_column("training_sets", "added_weight_kg")
    op.drop_column("training_sets", "rpe")
    op.drop_column("training_sets", "is_warmup")
    op.drop_column("training_sets", "exercise_id")

    op.drop_table("food_portions")
    op.drop_table("foods")
    op.drop_table("exercise_muscles")
    op.drop_table("exercises")
