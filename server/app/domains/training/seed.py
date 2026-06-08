"""Starter exercise catalog (common lifts) with muscle/category mappings.

Seeded idempotently at startup (by slug). Free-text logging still works for
anything not in the catalog; this just powers the balance/volume statistics.
Tuple shape: (name, category, primary_muscle, is_bodyweight, aliases, secondaries).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Exercise, ExerciseMuscle

# (name, category, primary_muscle, is_bodyweight, aliases, [secondary muscles])
SEED: list[tuple[str, str, str, bool, list[str], list[str]]] = [
    ("Bench Press", "push", "chest", False, ["barbell bench", "flat bench", "bench"], ["triceps", "front_delt"]),
    ("Incline Bench Press", "push", "chest", False, ["incline bench"], ["front_delt", "triceps"]),
    ("Overhead Press", "push", "front_delt", False, ["ohp", "shoulder press", "military press"], ["triceps", "side_delt"]),
    ("Lateral Raise", "push", "side_delt", False, ["side raise", "db lateral raise"], []),
    ("Triceps Pushdown", "push", "triceps", False, ["pushdown", "cable pushdown"], []),
    ("Dip", "push", "chest", True, ["dips"], ["triceps", "front_delt"]),
    ("Pull-up", "pull", "lats", True, ["pullup", "pull up", "chin-up", "chinup"], ["biceps", "back"]),
    ("Lat Pulldown", "pull", "lats", False, ["pulldown"], ["biceps"]),
    ("Barbell Row", "pull", "back", False, ["bent over row", "bb row", "row"], ["lats", "biceps", "rear_delt"]),
    ("Seated Cable Row", "pull", "back", False, ["cable row"], ["lats", "biceps"]),
    ("Biceps Curl", "pull", "biceps", False, ["curl", "dumbbell curl", "barbell curl"], ["forearms"]),
    ("Face Pull", "pull", "rear_delt", False, ["facepull"], ["traps"]),
    ("Back Squat", "squat", "quads", False, ["squat", "barbell squat"], ["glutes", "hamstrings"]),
    ("Front Squat", "squat", "quads", False, [], ["glutes"]),
    ("Leg Press", "squat", "quads", False, [], ["glutes"]),
    ("Lunge", "squat", "quads", False, ["walking lunge"], ["glutes", "hamstrings"]),
    ("Deadlift", "hinge", "hamstrings", False, ["conventional deadlift"], ["glutes", "back", "traps"]),
    ("Romanian Deadlift", "hinge", "hamstrings", False, ["rdl"], ["glutes"]),
    ("Hip Thrust", "hinge", "glutes", False, [], ["hamstrings"]),
    ("Calf Raise", "other", "calves", False, ["standing calf raise"], []),
    ("Plank", "core", "abs", True, [], ["obliques"]),
    ("Hanging Leg Raise", "core", "abs", True, ["leg raise"], ["obliques"]),
]


def _slug(name: str) -> str:
    return name.lower().replace("-", " ").replace("'", "").strip().replace(" ", "_")


async def seed_exercises(session: AsyncSession) -> int:
    """Insert any catalog entries missing by slug. Returns how many were added."""
    existing = set(
        (await session.execute(select(Exercise.slug))).scalars().all()
    )
    added = 0
    for name, category, primary, is_bw, aliases, secondaries in SEED:
        slug = _slug(name)
        if slug in existing:
            continue
        ex = Exercise(
            name=name,
            slug=slug,
            category=category,
            primary_muscle=primary,
            is_bodyweight=is_bw,
            aliases=aliases or None,
            muscles=[
                ExerciseMuscle(muscle=primary, role="primary"),
                *[ExerciseMuscle(muscle=m, role="secondary") for m in secondaries],
            ],
        )
        session.add(ex)
        added += 1
    if added:
        await session.flush()
    return added
