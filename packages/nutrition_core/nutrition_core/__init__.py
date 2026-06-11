"""Shared nutrition core: one food-name matcher + per-100g macro table.

Single source of truth for BOTH photo estimation (image-svc) and the gateway's
manual / serving-based entry (server), so "rice" resolves identically on both
paths and the macro data carries one ``TABLE_VERSION``.

Installed editable into each service's venv (``pip install -e``), so the bundled
``data/macros.csv`` is always on local disk — no network dependency at runtime.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from .matcher import MacroRow, MacroTable

__all__ = ["MacroRow", "MacroTable", "TABLE_VERSION", "default_macro_csv"]

# Bump when the bundled macros.csv changes; both services record it on output.
TABLE_VERSION = "usda-subset-0.3-co"


def default_macro_csv() -> Path:
    """Filesystem path to the bundled macro table (real path under editable install)."""
    return Path(str(files("nutrition_core").joinpath("data", "macros.csv")))
