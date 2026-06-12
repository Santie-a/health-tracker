"""SQLAlchemy ORM model for goals. Mirrors db/initdb/02_schema.sql (the DB
contract) and migration 0004."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Identity,
    Index,
    Integer,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Goal(Base):
    """One user objective. `category` (body / sleep) partitions goals so the
    recommendation engine can hold one active goal per family; the partial unique
    index enforces it at the DB level."""

    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint(
            "type IN ('gain_muscle','gain_weight','lose_fat','recomp','maintain','improve_sleep')",
            name="goals_type_check",
        ),
        CheckConstraint("category IN ('body','sleep')", name="goals_category_check"),
        CheckConstraint("status IN ('active','achieved','abandoned')", name="goals_status_check"),
        Index(
            "goals_one_active_per_category",
            "category",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
        Index("goals_status_idx", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active")

    metric: Mapped[str | None] = mapped_column(Text)
    baseline_value: Mapped[float | None] = mapped_column(Numeric(7, 2))
    target_value: Mapped[float | None] = mapped_column(Numeric(7, 2))
    target_rate_per_week: Mapped[float | None] = mapped_column(Numeric(6, 3))
    start_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    target_date: Mapped[date | None] = mapped_column(Date)

    calorie_delta: Mapped[int | None] = mapped_column(Integer)
    protein_g_per_kg: Mapped[float | None] = mapped_column(Numeric(4, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
