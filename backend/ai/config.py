"""Charge les variables d'environnement (OpenHosta lit aussi la hiérarchie des dossiers)."""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_env_path = _BACKEND_ROOT / ".env"
_loaded = load_dotenv(_env_path, override=False)
logger.info("[ai.config] chargement .env | path=%s | chargé=%s", _env_path, _loaded)
