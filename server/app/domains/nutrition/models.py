"""ORM models for nutrition.

Base tables (`meals`, `meal_items`) mirror initdb. Extension columns and the
catalog tables (`foods`, `food_portions`) are added by Alembic migration 0002 —
see db/TODO.md "Foods table & serving-based estimation". Models reflect the FINAL
post-migration state.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Meal(Base):
    __tablename__ = "meals"
    __table_args__ = (
        CheckConstraint("source IN ('image', 'manual')", name="meals_source_check"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    photo_path: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text, nullable=False, server_default="manual")

    items: Mapped[list[MealItem]] = relationship(
        back_populates="meal", cascade="all, delete-orphan"
    )


class MealItem(Base):
    __tablename__ = "meal_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    meal_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False
    )
    food: Mapped[str] = mapped_column(Text, nullable=False)  # as-logged / free-text fallback
    grams: Mapped[float | None] = mapped_column(Numeric(7, 2))  # resolved amount
    kcal: Mapped[float | None] = mapped_column(Numeric(7, 2))
    protein_g: Mapped[float | None] = mapped_column(Numeric(6, 2))
    carbs_g: Mapped[float | None] = mapped_column(Numeric(6, 2))
    fat_g: Mapped[float | None] = mapped_column(Numeric(6, 2))

    # --- 0002 extension: catalog link + serving-based entry --------------------
    food_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("foods.id"), index=True
    )
    qty: Mapped[float | None] = mapped_column(Numeric(6, 2))  # e.g. 2 (× portion)
    portion_label: Mapped[str | None] = mapped_column(Text)  # e.g. "1 cup"
    estimated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # per-item origin: image | manual | estimate (meals.source is meal-level).
    source: Mapped[str | None] = mapped_column(Text)

    meal: Mapped[Meal] = relationship(back_populates="items")
    food_ref: Mapped[Food | None] = relationship(back_populates="items")


class Food(Base):
    """Food catalog (0002). Per-100g macros, same basis as image-svc's CSV."""

    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    aliases: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    kcal_100g: Mapped[float | None] = mapped_column(Numeric(7, 2))
    protein_100g: Mapped[float | None] = mapped_column(Numeric(6, 2))
    carbs_100g: Mapped[float | None] = mapped_column(Numeric(6, 2))
    fat_100g: Mapped[float | None] = mapped_column(Numeric(6, 2))
    default_grams: Mapped[float | None] = mapped_column(Numeric(7, 2))
    table_version: Mapped[str | None] = mapped_column(Text)

    portions: Mapped[list[FoodPortion]] = relationship(
        back_populates="food", cascade="all, delete-orphan"
    )
    items: Mapped[list[MealItem]] = relationship(back_populates="food_ref")


class FoodPortion(Base):
    """Serving presets (0002): rice "1 cup cooked"=158g, etc."""

    __tablename__ = "food_portions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    food_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("foods.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(Text, nullable=False)
    grams: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    food: Mapped[Food] = relationship(back_populates="portions")
