"""Calculs déterministes retraite (estimation hackathon, PRD RetroAide §7.4)."""

from __future__ import annotations

# Référence produit (taux plein au régime général, ordre de grandeur)
TRIMESTRES_REQUIS_TAUX_PLEIN = 172


def statutory_full_rate_age(birth_year: int) -> int:
    """
    Âge à partir duquel la décote liée à l'âge cesse en général (simplification hackathon : 67 ans).
    Ne remplace pas le calcul personnalisé (trimestres, régimes multiples).
    """
    _ = birth_year
    return 67


def calculate_departure_age(birth_year: int) -> int:
    """Âge légal de départ (simplification réforme 2023, profil général)."""
    if birth_year >= 1968:
        return 64
    elif birth_year >= 1961:
        return 63
    else:
        return 62


def estimate_quarters_worked(start_work_year: int, *, reference_year: int = 2026) -> int:
    """
    Estimation brute : 4 trimestres par an entre début de carrière et année de référence, plafonnée à 172.
    ``reference_year`` permet de figer les tests (PRD utilise 2026).
    """
    years = reference_year - start_work_year
    if years < 0:
        return 0
    return min(years * 4, TRIMESTRES_REQUIS_TAUX_PLEIN)


def quarters_remaining(quarters_worked: int, *, trimestres_requis: int = TRIMESTRES_REQUIS_TAUX_PLEIN) -> int:
    """Trimestres manquants pour atteindre le plafond de cotisation retenu (172 par défaut)."""
    return max(0, trimestres_requis - quarters_worked)
