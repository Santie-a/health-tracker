from __future__ import annotations

import pytest

from app.config import get_settings
from nutrition_core import MacroTable


@pytest.fixture(scope="module")
def table() -> MacroTable:
    return MacroTable.from_csv(get_settings().macro_table_path)


def test_loads_rows(table: MacroTable):
    assert len(table) > 100
    assert "chicken breast" in table.names


def test_canonical_lookup(table: MacroTable):
    row = table.lookup("chicken breast")
    assert row is not None
    assert row.kcal == 165
    assert row.protein_g == 31.0


def test_alias_lookup(table: MacroTable):
    # "grilled chicken" is an alias of "chicken breast".
    row = table.lookup("Grilled Chicken")
    assert row is not None and row.name == "chicken breast"


def test_token_match_prefers_most_specific(table: MacroTable):
    # Loose model output should map to the most specific row, dropping cooking
    # words ("grilled", "with") rather than matching the bare "chicken" alias.
    row = table.lookup("some grilled chicken breast with herbs")
    assert row is not None and row.name == "chicken breast"


def test_plurals_resolve(table: MacroTable):
    assert table.lookup("tomatoes").name == "tomato"
    assert table.lookup("eggs").name == "egg"
    assert table.lookup("zucchini flowers").name == "zucchini flowers"


def test_no_false_substring_match(table: MacroTable):
    # "eggplant" must not resolve to "egg" the way naive substring did.
    assert table.lookup("eggplant").name == "eggplant"
    assert table.lookup("egg").name == "egg"


def test_alias_synonyms(table: MacroTable):
    assert table.lookup("courgette").name == "zucchini"
    assert table.lookup("aubergine").name == "eggplant"
    assert table.lookup("fries").name == "french fries"


def test_unknown_returns_none(table: MacroTable):
    # Truly absent foods (no shared significant token) resolve to nothing.
    assert table.lookup("dragonfruit") is None
    assert table.lookup("tiramisu") is None
    assert table.lookup("") is None


def test_scale_math(table: MacroTable):
    row = table.lookup("white rice")
    assert row is not None
    kcal, protein, carbs, fat = row.scale(200)
    assert kcal == pytest.approx(260.0)  # 130 * 2
    assert carbs == pytest.approx(56.0)  # 28 * 2
