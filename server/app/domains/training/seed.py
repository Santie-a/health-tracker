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
    # --- push (expanded) ------------------------------------------------------
    ("Dumbbell Bench Press", "push", "chest", False, ["db bench", "dumbbell press"], ["triceps", "front_delt"]),
    ("Decline Bench Press", "push", "chest", False, ["decline bench"], ["triceps"]),
    ("Push-up", "push", "chest", True, ["pushup", "push ups", "press up"], ["triceps", "front_delt"]),
    ("Chest Fly", "push", "chest", False, ["cable fly", "pec fly", "pec deck", "dumbbell fly"], ["front_delt"]),
    ("Arnold Press", "push", "front_delt", False, [], ["side_delt", "triceps"]),
    ("Front Raise", "push", "front_delt", False, ["db front raise"], []),
    ("Skull Crusher", "push", "triceps", False, ["skullcrusher", "lying triceps extension"], []),
    ("Overhead Triceps Extension", "push", "triceps", False, ["triceps extension", "overhead extension"], []),
    ("Close Grip Bench Press", "push", "triceps", False, ["close grip bench", "cgbp"], ["chest"]),
    # --- pull (expanded) ------------------------------------------------------
    ("T-Bar Row", "pull", "back", False, ["t bar row", "tbar row"], ["lats", "biceps"]),
    ("Dumbbell Row", "pull", "back", False, ["db row", "one arm row", "single arm row"], ["lats", "biceps"]),
    ("Pendlay Row", "pull", "back", False, [], ["lats", "biceps"]),
    ("Hammer Curl", "pull", "biceps", False, ["hammer curls"], ["forearms"]),
    ("Preacher Curl", "pull", "biceps", False, [], ["forearms"]),
    ("Cable Curl", "pull", "biceps", False, [], ["forearms"]),
    ("Shrug", "pull", "traps", False, ["shrugs", "barbell shrug", "dumbbell shrug"], []),
    ("Rear Delt Fly", "pull", "rear_delt", False, ["reverse fly", "rear delt raise"], ["traps"]),
    ("Straight Arm Pulldown", "pull", "lats", False, ["straight arm pushdown"], ["back"]),
    # --- squat (expanded) -----------------------------------------------------
    ("Goblet Squat", "squat", "quads", False, [], ["glutes"]),
    ("Bulgarian Split Squat", "squat", "quads", False, ["split squat", "bss"], ["glutes", "hamstrings"]),
    ("Hack Squat", "squat", "quads", False, [], ["glutes"]),
    ("Leg Extension", "squat", "quads", False, ["leg extensions"], []),
    ("Step-up", "squat", "quads", True, ["step up", "step ups"], ["glutes"]),
    # --- hinge (expanded) -----------------------------------------------------
    ("Sumo Deadlift", "hinge", "hamstrings", False, ["sumo dl"], ["glutes", "quads"]),
    ("Good Morning", "hinge", "hamstrings", False, [], ["glutes", "back"]),
    ("Leg Curl", "hinge", "hamstrings", False, ["hamstring curl", "lying leg curl", "seated leg curl"], []),
    ("Glute Bridge", "hinge", "glutes", False, [], ["hamstrings"]),
    ("Back Extension", "hinge", "back", False, ["hyperextension", "45 degree back extension"], ["glutes", "hamstrings"]),
    ("Kettlebell Swing", "hinge", "glutes", False, ["kb swing"], ["hamstrings", "back"]),
    # --- core (expanded) ------------------------------------------------------
    ("Crunch", "core", "abs", True, ["crunches", "sit-up", "situp", "sit ups"], ["obliques"]),
    ("Russian Twist", "core", "obliques", True, [], ["abs"]),
    ("Cable Crunch", "core", "abs", False, [], []),
    ("Ab Wheel Rollout", "core", "abs", False, ["ab wheel", "ab rollout"], ["obliques"]),
    ("Mountain Climber", "core", "abs", True, ["mountain climbers"], ["obliques"]),
    ("Side Plank", "core", "obliques", True, [], ["abs"]),
    # --- carry / accessory / cardio (other) -----------------------------------
    ("Farmers Carry", "carry", "forearms", False, ["farmers walk", "farmer's walk", "farmer carry"], ["traps"]),
    ("Seated Calf Raise", "other", "calves", False, [], []),
    ("Wrist Curl", "other", "forearms", False, ["wrist curls"], []),
    ("Running", "other", "quads", False, ["run", "jog", "jogging", "treadmill"], ["hamstrings", "calves"]),
    ("Cycling", "other", "quads", False, ["bike", "stationary bike", "spinning"], ["hamstrings", "calves"]),
    ("Rowing Machine", "other", "back", False, ["row erg", "erg", "rowing machine"], ["lats", "quads"]),
    ("Elliptical", "other", "quads", False, [], ["hamstrings"]),
    ("Jump Rope", "other", "calves", True, ["skipping", "skip rope"], []),
    ("Burpee", "other", "quads", True, ["burpees"], ["chest", "abs"]),
    # --- swim strokes ---------------------------------------------------------
    ("Freestyle", "swim", "lats", False, ["front crawl", "crawl"], ["back", "triceps"]),
    ("Breaststroke", "swim", "chest", False, [], ["quads", "glutes"]),
    ("Backstroke", "swim", "lats", False, [], ["rear_delt", "back"]),
    ("Butterfly", "swim", "chest", False, ["fly stroke"], ["lats", "front_delt"]),
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
