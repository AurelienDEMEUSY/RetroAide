"""Endpoint analyse : métriques déterministes + OpenHosta (advisor)."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from ai.advisor import detect_missing_quarters, generate_checklist
from app.schemas import AnalyzeResponse, ChecklistItem, MissingQuarterItem, UserProfile
from core.calculator import (
    calculate_departure_age,
    estimate_quarters_worked,
    quarters_remaining,
)

router = APIRouter(tags=["analyze"])
log = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalyzeResponse)
def post_analyze(body: UserProfile) -> AnalyzeResponse:
    log.info("[analyze] début traitement POST /analyze")
    profile_dict = body.model_dump()
    log.debug(
        "[analyze] profil reçu (aperçu non exhaustif): birth_year=%s career_start=%s status=%s "
        "employed=%s flags={children:%s chômage:%s arrêt_long:%s militaire:%s temps_partiel:%s}",
        body.birth_year,
        body.career_start_year,
        body.status,
        body.currently_employed,
        body.had_children,
        body.had_unemployment,
        body.had_long_sick_leave,
        body.had_military_service,
        body.long_part_time_years,
    )

    log.debug("[analyze] étape calculator: calculate_departure_age(%s)", body.birth_year)
    departure_age = calculate_departure_age(body.birth_year)
    log.debug("[analyze] → departure_age=%s", departure_age)

    log.debug("[analyze] étape calculator: estimate_quarters_worked(%s)", body.career_start_year)
    quarters_worked = estimate_quarters_worked(body.career_start_year)
    log.debug("[analyze] → quarters_worked=%s", quarters_worked)

    log.debug("[analyze] étape calculator: quarters_remaining(%s)", quarters_worked)
    q_remaining = quarters_remaining(quarters_worked)
    log.debug("[analyze] → quarters_remaining=%s", q_remaining)

    log.info("[analyze] appel OpenHosta detect_missing_quarters")
    missing_raw = detect_missing_quarters(profile_dict)
    log.info("[analyze] detect_missing_quarters terminé | %s entrée(s)", len(missing_raw))

    log.info("[analyze] appel OpenHosta generate_checklist")
    checklist_raw = generate_checklist(profile_dict, missing_raw)
    log.info("[analyze] generate_checklist terminé | %s entrée(s)", len(checklist_raw))

    log.info(
        "[analyze] réponse construite | departure_age=%s quarters_worked=%s quarters_remaining=%s "
        "checklist_items=%s missing_quarters_items=%s",
        departure_age,
        quarters_worked,
        q_remaining,
        len(checklist_raw),
        len(missing_raw),
    )
    return AnalyzeResponse(
        departure_age=departure_age,
        quarters_worked=quarters_worked,
        quarters_remaining=q_remaining,
        missing_quarters=[MissingQuarterItem(**m) for m in missing_raw],
        checklist=[ChecklistItem(**c) for c in checklist_raw],
    )
