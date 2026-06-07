"""Logging setup — configured once at startup, written to stdout.

Stdout (not a file) so Docker / systemd capture it on the Pi5. Format is a
readable key=value line with timestamp, level, and logger name so a caught
error is always traceable. Call ``configure_logging`` from the app lifespan.
"""

from __future__ import annotations

import logging
import sys

_CONFIGURED = False


def configure_logging(level: str = "INFO") -> None:
    """Idempotent: safe to call on every lifespan enter (e.g. under TestClient)."""
    global _CONFIGURED

    root = logging.getLogger()
    root.setLevel(level.upper())

    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s level=%(levelname)s logger=%(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    root.handlers.clear()
    root.addHandler(handler)
    _CONFIGURED = True
