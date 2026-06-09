"""Muscle taxonomy used by the strength-stats aggregations.

Groupings drive the push:pull and upper:lower balance ratios. Secondary muscles
are credited fractionally (the bench credits chest fully + triceps/front-delt
partially) — the honest way to count "sets per muscle".
"""

from __future__ import annotations

PUSH = {"chest", "front_delt", "side_delt", "triceps"}
PULL = {"back", "lats", "traps", "rear_delt", "biceps", "forearms"}
LOWER = {"quads", "hamstrings", "glutes", "calves"}
CORE = {"abs", "obliques"}
UPPER = PUSH | PULL

# Fraction of a set credited to a secondary muscle (primary = 1.0).
SECONDARY_CREDIT = 0.5


def muscle_group(muscle: str) -> str | None:
    if muscle in UPPER:
        return "upper"
    if muscle in LOWER:
        return "lower"
    if muscle in CORE:
        return "core"
    return None
