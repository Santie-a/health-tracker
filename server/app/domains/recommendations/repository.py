"""DB access for recommendations: assemble the day context (across domains) and
read/write the stored daily recommendation row."""

from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timerange import day_bounds
from app.domains.nutrition.models import Meal, MealItem
from app.domains.telemetry.models import BodyComposition, SleepSession, Telemetry
from app.domains.training import service as training_service
from app.domains.training.models import TrainingSession

from .models import Recommendation
from .rules import DayContext


def _day_range(day: date_cls) -> tuple[datetime, datetime]:
    return day_bounds(day)  # local calendar day → UTC instants (APP_TIMEZONE)


def _f(value) -> float | None:
    return float(value) if value is not None else None


async def build_context(session: AsyncSession, day: date_cls) -> DayContext:
    start, end = _day_range(day)

    # --- telemetry (complementary, optional) ---------------------------------
    sleep_min = (
        await session.execute(
            select(SleepSession.total_min)
            .where(SleepSession.end_ts >= start, SleepSession.end_ts < end)
            .order_by(SleepSession.total_min.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    avg_stress = (
        await session.execute(
            select(func.avg(Telemetry.value)).where(
                Telemetry.metric == "stress", Telemetry.ts >= start, Telemetry.ts < end
            )
        )
    ).scalar_one_or_none()

    energy = (
        await session.execute(
            select(func.sum(Telemetry.value)).where(
                Telemetry.metric == "energy_expenditure", Telemetry.ts >= start, Telemetry.ts < end
            )
        )
    ).scalar_one_or_none()

    weight = (
        await session.execute(
            select(BodyComposition.weight_kg)
            .where(BodyComposition.weight_kg.is_not(None), BodyComposition.ts < end)
            .order_by(BodyComposition.ts.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    # --- training (manual, primary) ------------------------------------------
    sessions = (
        await session.execute(
            select(TrainingSession.type, TrainingSession.load).where(
                TrainingSession.ts >= start, TrainingSession.ts < end
            )
        )
    ).all()
    did_swim = any(s.type == "swim" for s in sessions)
    did_gym = any(s.type == "gym" for s in sessions)
    loads = [float(s.load) for s in sessions if s.load is not None]
    total_load = sum(loads) if loads else None

    # --- nutrition (manual, primary) -----------------------------------------
    protein, kcal = (
        await session.execute(
            select(func.sum(MealItem.protein_g), func.sum(MealItem.kcal))
            .join(Meal, MealItem.meal_id == Meal.id)
            .where(Meal.ts >= start, Meal.ts < end)
        )
    ).one()

    # --- weekly training balance (trailing 7 days incl. today) ---------------
    stats = await training_service.get_stats(session, day - timedelta(days=6), day)

    return DayContext(
        date=day,
        sleep_min=sleep_min,
        avg_stress=_f(avg_stress),
        energy_expenditure=_f(energy),
        weight_kg=_f(weight),
        did_swim=did_swim,
        did_gym=did_gym,
        total_training_load=total_load,
        protein_g=_f(protein),
        kcal_in=_f(kcal),
        push_pull_ratio=stats.push_pull_ratio,
        upper_lower_ratio=stats.upper_lower_ratio,
    )


async def upsert(session: AsyncSession, day: date_cls, payload: dict) -> None:
    stmt = pg_insert(Recommendation).values(date=day, payload=payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["date"],
        set_={"payload": stmt.excluded.payload, "generated_at": func.now()},
    )
    await session.execute(stmt)


async def get(session: AsyncSession, day: date_cls) -> Recommendation | None:
    return (
        await session.execute(select(Recommendation).where(Recommendation.date == day))
    ).scalar_one_or_none()


async def set_feedback(session: AsyncSession, day: date_cls, feedback: str) -> bool:
    row = await get(session, day)
    if row is None:
        return False
    row.feedback = feedback
    return True
