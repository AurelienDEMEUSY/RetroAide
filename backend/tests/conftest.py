"""Initialise le logging pour les tests (même format que l'API)."""

from app.logging_config import setup_logging


def pytest_configure(config) -> None:
    _ = config  # hook pytest (nom imposé)
    setup_logging()
