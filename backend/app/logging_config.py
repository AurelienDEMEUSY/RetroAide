"""Configuration logging : sortie stdout pour Docker (`docker compose logs`)."""

from __future__ import annotations

import logging
import os
import sys


def setup_logging() -> None:
    """
    Niveau par défaut DEBUG pour un suivi verbeux (variable LOG_LEVEL=INFO|WARNING|DEBUG).
    """
    level_name = os.environ.get("LOG_LEVEL", "DEBUG").upper()
    level = getattr(logging, level_name, logging.DEBUG)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt, datefmt))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Moins de bruit réseau (sauf si LOG_LEVEL=DEBUG sur ces loggers)
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).setLevel(level)

    logging.getLogger(__name__).debug(
        "Logging initialisé | niveau racine=%s | LOG_LEVEL env=%r",
        logging.getLevelName(level),
        os.environ.get("LOG_LEVEL", "(défaut DEBUG)"),
    )
