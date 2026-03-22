"""Étape 1 du pipeline : calculs déterministes + enrichissement open data."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from app.converters import enrichment_to_section
from app.schemas import ComputeResponse, UserProfile
from core.calculator import (
    TRIMESTRES_REQUIS_TAUX_PLEIN,
    calculate_departure_age,
    estimate_quarters_worked,
    quarters_remaining,
    statutory_full_rate_age,
)
from tools.mcp_pipeline import run_enrichment

router = APIRouter(tags=["compute"])
log = logging.getLogger(__name__)


def run_compute(body: UserProfile) -> ComputeResponse:
    """Exécute les calculs déterministes + enrichissement — réutilisable en interne."""
    profile_dict = body.model_dump()

    departure_age = calculate_departure_age(body.birth_year)
    age_taux = statutory_full_rate_age(body.birth_year)
    # On utilise la valeur saisie si elle est renseignée (> 0), sinon on estime.
    q_worked = body.validated_quarters if body.validated_quarters > 0 else estimate_quarters_worked(body.career_start_age, body.birth_year)
    q_remaining = quarters_remaining(q_worked, trimestres_requis=TRIMESTRES_REQUIS_TAUX_PLEIN)

    enrichment = run_enrichment(profile_dict)

    return ComputeResponse(
        departure_age=departure_age,
        age_taux_plein_auto=age_taux,
        quarters_worked=q_worked,
        quarters_remaining=q_remaining,
        enrichment=enrichment_to_section(enrichment),
        profile=profile_dict,
    )


@router.post("/compute", response_model=ComputeResponse)
def post_compute(body: UserProfile) -> ComputeResponse:
    """Étape 1 : calculs réglementaires + enrichissement open data (pas de LLM)."""
    log.info("[compute] POST /compute — calculs + enrichissement")
    return run_compute(body)
