"""Charge les variables d'environnement (OpenHosta lit aussi la hiérarchie des dossiers)."""

from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_ROOT / ".env", override=False)
