"""Calculs déterministes retraite (estimation hackathon, PRD RetroAide §7.4)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def calculate_departure_age(birth_year: int) -> int:
    """Âge légal de départ (simplification réforme 2023, profil général)."""
    logger.debug("[calculator] calculate_departure_age(birth_year=%s)", birth_year)
    if birth_year >= 1968:
        age = 64
    elif birth_year >= 1961:
        age = 63
    else:
        age = 62
    logger.debug("[calculator] → âge légal départ = %s", age)
    return age


def estimate_quarters_worked(start_work_year: int, *, reference_year: int = 2026) -> int:
    """
    Estimation brute : 4 trimestres par an entre début de carrière et année de référence, plafonnée à 172.
    `reference_year` permet de figer les tests (PRD utilise 2026).
    """
    logger.debug(
        "[calculator] estimate_quarters_worked(start=%s, reference_year=%s)",
        start_work_year,
        reference_year,
    )
    years = reference_year - start_work_year
    if years < 0:
        logger.debug("[calculator] années négatives → 0 trimestre")
        return 0
    raw_quarters = years * 4
    capped = min(raw_quarters, 172)
    logger.debug("[calculator] années=%s brut_trimestres=%s → plafonné=%s", years, raw_quarters, capped)
    return capped


def quarters_remaining(quarters_worked: int) -> int:
    """Trimestres manquants pour atteindre le plafond de cotisation retenu (172)."""
    logger.debug("[calculator] quarters_remaining(quarters_worked=%s)", quarters_worked)
    rem = max(0, 172 - quarters_worked)
    logger.debug("[calculator] → trimestres restants = %s", rem)
    return rem
