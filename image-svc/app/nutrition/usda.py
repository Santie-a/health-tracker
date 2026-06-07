"""Local macro lookup so estimates never need the network.

Loads a bundled USDA FoodData Central subset (per-100g macros) and maps a
detected ``(food, grams)`` pair to absolute macros.

Matching is tolerant of the loose, free-form names a vision-LLM emits
("grilled chicken breast with herbs", "zucchini flowers", "tomatoes"):

1. exact match on the normalized name or any alias;
2. exact match after singularizing each word (plurals);
3. token-set matching — drop cooking/filler words ("grilled", "with", ...),
   singularize, then prefer the most specific phrase whose words are all
   present, falling back to the largest word overlap.

Token matching replaces naive substring matching, which false-matched short
names inside longer ones (e.g. "egg" inside "eggplant", "rice" inside "licorice").
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

_WORD = re.compile(r"[^a-z0-9]+")

# Cooking methods and filler dropped before token matching so they never drive a
# match. Deliberately excludes words that distinguish foods ("whole", "sweet",
# "white", "brown", "green", "mixed").
_STOPWORDS = frozenset(
    {
        "grilled", "fried", "deep", "pan", "baked", "roasted", "roast", "steamed",
        "boiled", "poached", "sauteed", "seared", "smoked", "raw", "cooked",
        "fresh", "ripe", "plain", "hot", "cold", "warm", "with", "without", "and",
        "or", "of", "a", "an", "the", "in", "on", "some", "served", "serving",
        "side", "piece", "pieces", "chopped", "sliced", "diced", "minced",
        "plate", "dish", "bowl", "cup", "homemade", "style",
    }
)


def _normalize(name: str) -> str:
    return _WORD.sub(" ", name.strip().lower()).strip()


def _singularize(word: str) -> str:
    """Cheap, domain-appropriate plural -> singular."""
    if len(word) <= 3 or word.endswith("ss"):
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"  # berries -> berry
    if word.endswith("oes"):
        return word[:-2]  # tomatoes -> tomato
    if word.endswith("ves"):
        return word[:-3] + "f"  # loaves -> loaf
    if word.endswith("s"):
        return word[:-1]  # eggs -> egg, flowers -> flower
    return word


def _content_tokens(norm: str) -> frozenset[str]:
    """Significant words: stopwords dropped, each singularized."""
    return frozenset(
        _singularize(w) for w in norm.split() if w and w not in _STOPWORDS
    )


@dataclass(frozen=True)
class MacroRow:
    """Per-100g macros for one food."""

    name: str
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float

    def scale(self, grams: float) -> tuple[float, float, float, float]:
        f = grams / 100.0
        return (
            round(self.kcal * f, 1),
            round(self.protein_g * f, 1),
            round(self.carbs_g * f, 1),
            round(self.fat_g * f, 1),
        )


class MacroTable:
    """Name -> per-100g macros, tolerant of loose model output."""

    def __init__(
        self,
        rows: dict[str, MacroRow],
        index: dict[str, str],
        phrases: list[tuple[frozenset[str], str]],
    ):
        self._rows = rows  # canonical name -> MacroRow
        self._index = index  # normalized name/alias -> canonical name
        self._phrases = phrases  # (token set, canonical) for every name + alias

    @classmethod
    def from_csv(cls, path: str | Path) -> "MacroTable":
        path = Path(path)
        rows: dict[str, MacroRow] = {}
        index: dict[str, str] = {}
        phrases: list[tuple[frozenset[str], str]] = []
        with path.open(newline="", encoding="utf-8") as fh:
            for raw in csv.DictReader(fh):
                row = MacroRow(
                    name=raw["name"].strip(),
                    kcal=float(raw["kcal"]),
                    protein_g=float(raw["protein_g"]),
                    carbs_g=float(raw["carbs_g"]),
                    fat_g=float(raw["fat_g"]),
                )
                rows[row.name] = row
                surfaces = [row.name, *(raw.get("aliases") or "").split(";")]
                for surface in surfaces:
                    surface = surface.strip()
                    if not surface:
                        continue
                    norm = _normalize(surface)
                    index.setdefault(norm, row.name)
                    tokens = _content_tokens(norm)
                    if tokens:
                        phrases.append((tokens, row.name))
        if not rows:
            raise ValueError(f"Macro table at {path} is empty")
        # Longest phrases first so the most specific subset match wins ties.
        phrases.sort(key=lambda p: len(p[0]), reverse=True)
        return cls(rows, index, phrases)

    def __len__(self) -> int:
        return len(self._rows)

    @property
    def names(self) -> list[str]:
        return list(self._rows)

    def lookup(self, name: str) -> MacroRow | None:
        """Resolve a (possibly loose) food name to a macro row, or None."""
        norm = _normalize(name)
        if not norm:
            return None
        if norm in self._index:
            return self._rows[self._index[norm]]

        singular = " ".join(_singularize(w) for w in norm.split())
        if singular in self._index:
            return self._rows[self._index[singular]]

        query = _content_tokens(norm)
        if not query:
            return None

        # (kind, size): subset matches (2) beat overlap (1); within each, the
        # bigger phrase / overlap wins. Phrases are pre-sorted longest-first, so
        # equal scores keep the most specific phrase.
        best_canonical: str | None = None
        best_score = (0, 0)
        for tokens, canonical in self._phrases:
            if tokens <= query:
                score = (2, len(tokens))
            else:
                overlap = len(tokens & query)
                if overlap == 0:
                    continue
                score = (1, overlap)
            if score > best_score:
                best_score = score
                best_canonical = canonical
        return self._rows[best_canonical] if best_canonical else None
