"""Aggregator that imports every ORM model so they register on ``Base.metadata``.

Import this (not the individual domain modules) wherever the full schema is needed
— notably Alembic's ``env.py`` target_metadata.
"""

from __future__ import annotations

from app.core.db import Base
from app.domains.nutrition import models as nutrition  # noqa: F401
from app.domains.recommendations import models as recommendations  # noqa: F401
from app.domains.telemetry import models as telemetry  # noqa: F401
from app.domains.training import models as training  # noqa: F401

metadata = Base.metadata
