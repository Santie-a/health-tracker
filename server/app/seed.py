"""Dev seed script: populate the gateway with a realistic dataset for the frontend.

By default it generates self-contained data (so it works anywhere — fresh clone,
CI, the Pi5): catalog, telemetry, manual training (with sets), meals, and a daily
recommendation pass. Pass --samsung <dir> to ingest a REAL Samsung export for the
telemetry instead of generating it (your local /temp/data) — manual data is always
generated since there's no real source for it.

Usage:
    python -m app.seed --days 21
    python -m app.seed --days 21 --samsung temp/data --reset
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import random
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from nutrition_core import MacroTable, default_macro_csv
from sqlalchemy import delete

from app.core.config import get_settings
from app.core.db import create_engine, create_sessionmaker
from app.core.logging_config import configure_logging
from app.domains.ingest import service as ingest_service
from app.domains.nutrition.foods_seed import seed_foods
from app.domains.nutrition.models import Meal, MealItem
from app.domains.recommendations import service as rec_service
from app.domains.recommendations.models import Recommendation
from app.domains.telemetry.models import BodyComposition, SleepSession, Telemetry
from app.domains.training.models import TrainingSession, TrainingSet
from app.domains.training.seed import seed_exercises

log = logging.getLogger("server.seed")
random.seed(42)

# Rotating gym templates (catalog names so stats resolve) + a swim.
_GYM_DAYS = [
    [("Bench Press", 5, 80), ("Overhead Press", 6, 45), ("Triceps Pushdown", 12, 25)],
    [("Barbell Row", 6, 70), ("Lat Pulldown", 10, 55), ("Biceps Curl", 12, 18)],
    [("Back Squat", 5, 110), ("Romanian Deadlift", 8, 90), ("Calf Raise", 15, 60)],
]
_MEALS = [
    ("breakfast", [("oats", 80), ("banana", 118), ("egg", 100)]),
    ("lunch", [("chicken breast", 200), ("rice", 180), ("olive oil", 10)]),
    ("dinner", [("salmon", 180), ("potato", 200), ("broccoli", 150)]),
]


def _utc(d: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(d, time(hour, minute), tzinfo=timezone.utc)


def _meal_items(table: MacroTable, items: list[tuple[str, float]]) -> list[MealItem]:
    out = []
    for food, grams in items:
        row = table.lookup(food)
        kcal = p = c = f = None
        estimated = False
        if row is not None:
            kcal, p, c, f = row.scale(grams)
            estimated = True
        out.append(MealItem(food=food, grams=grams, kcal=kcal, protein_g=p, carbs_g=c,
                            fat_g=f, estimated=estimated, source="manual"))
    return out


def _generate_telemetry(d: date) -> list:
    rows = []
    midnight = _utc(d, 0)
    rows.append(Telemetry(ts=midnight, metric="steps", value=random.randint(5000, 13000),
                          unit="count", source="seed"))
    rows.append(Telemetry(ts=midnight, metric="energy_expenditure",
                          value=random.randint(2000, 2700), unit="kcal", source="seed"))
    for hour in (9, 14, 20):
        rows.append(Telemetry(ts=_utc(d, hour), metric="stress",
                              value=random.randint(25, 85), unit="index", source="seed"))
        rows.append(Telemetry(ts=_utc(d, hour), metric="heart_rate",
                              value=random.randint(55, 95), unit="bpm", source="seed"))
    rows.append(Telemetry(ts=_utc(d, 7), metric="spo2", value=random.randint(95, 99),
                          unit="%", source="seed"))
    return rows


def _sleep_session(d: date) -> SleepSession:
    start = _utc(d, 0) - timedelta(hours=1)  # ~23:00 previous night
    total = random.randint(330, 480)
    deep = int(total * 0.18)
    rem = int(total * 0.22)
    awake = random.randint(10, 40)
    light = total - deep - rem
    return SleepSession(start_ts=start, end_ts=start + timedelta(minutes=total + awake),
                        total_min=total, deep_min=deep, rem_min=rem, light_min=light,
                        awake_min=awake, efficiency=round(total / (total + awake) * 100, 1))


async def _reset(session) -> None:
    for model in (Recommendation, MealItem, Meal, TrainingSet, TrainingSession,
                  Telemetry, SleepSession, BodyComposition):
        await session.execute(delete(model))
    log.info("reset: cleared transactional tables (catalog kept)")


async def run(days: int, samsung: str | None, reset: bool) -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    engine = create_engine(settings.database_url)
    sm = create_sessionmaker(engine)
    table = MacroTable.from_csv(default_macro_csv())
    today = datetime.now(timezone.utc).date()

    async with sm() as session:
        if reset:
            await _reset(session)
        await seed_exercises(session)
        await seed_foods(session)

        # Telemetry: real export if given, else generated.
        if samsung:
            files = [(p.name, p.read_bytes()) for p in sorted(Path(samsung).glob("com.samsung*.csv"))]
            report = await ingest_service.ingest_files(session, files)
            log.info("ingested Samsung export: %d rows from %d files", report.written, len(files))
        else:
            for i in range(days):
                d = today - timedelta(days=i)
                session.add_all(_generate_telemetry(d))
                session.add(_sleep_session(d))
            session.add(BodyComposition(ts=_utc(today - timedelta(days=days), 8),
                                        weight_kg=80, body_fat_pct=15, skeletal_muscle_kg=38, bmr_kcal=1750))

        # Manual data (always generated).
        for i in range(days):
            d = today - timedelta(days=i)
            if i % 4 == 3:  # swim every 4th day
                session.add(TrainingSession(ts=_utc(d, 7), type="swim", duration_min=45, rpe=6,
                                            load=270, source="manual", distance_m=1500,
                                            sets=[TrainingSet(exercise="freestyle", distance_m=1500, pace="1:50/100m")]))
            else:
                tmpl = _GYM_DAYS[i % len(_GYM_DAYS)]
                sets = []
                for name, reps, weight in tmpl:
                    for n in range(1, 4):
                        sets.append(TrainingSet(exercise=name, set_no=n, reps=reps, weight_kg=weight))
                session.add(TrainingSession(ts=_utc(d, 18), type="gym", duration_min=60, rpe=8,
                                            load=480, source="manual", sets=sets))
            for hour, (name, items) in zip((8, 13, 20), _MEALS):
                session.add(Meal(ts=_utc(d, hour), name=name, source="manual",
                                 items=_meal_items(table, items)))
        await session.commit()
        log.info("seeded %d days of manual training + meals", days)

    # Recommendation pass per day (separate sessions, guarded).
    async with sm() as session:
        for i in range(days):
            await rec_service.run_for_date(session, today - timedelta(days=i))
        await session.commit()
    log.info("generated recommendations for %d days", days)
    await engine.dispose()


def main() -> None:
    ap = argparse.ArgumentParser(description="Seed the gateway with dev data.")
    ap.add_argument("--days", type=int, default=21, help="How many days back to seed.")
    ap.add_argument("--samsung", help="Dir of Samsung CSVs to ingest instead of generated telemetry.")
    ap.add_argument("--reset", action="store_true", help="Clear transactional tables first.")
    args = ap.parse_args()
    asyncio.run(run(args.days, args.samsung, args.reset))


if __name__ == "__main__":
    main()
