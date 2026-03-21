"""Calculs déterministes retraite (estimation hackathon, PRD RetroAide §7.4)."""


def calculate_departure_age(birth_year: int) -> int:
    """Âge légal de départ (simplification réforme 2023, profil général)."""
    if birth_year >= 1968:
        return 64
    if birth_year >= 1961:
        return 63
    return 62


def estimate_quarters_worked(start_work_year: int, *, reference_year: int = 2026) -> int:
    """
    Estimation brute : 4 trimestres par an entre début de carrière et année de référence, plafonnée à 172.
    `reference_year` permet de figer les tests (PRD utilise 2026).
    """
    years = reference_year - start_work_year
    if years < 0:
        return 0
    return min(years * 4, 172)


def quarters_remaining(quarters_worked: int) -> int:
    """Trimestres manquants pour atteindre le plafond de cotisation retenu (172)."""
    return max(0, 172 - quarters_worked)
