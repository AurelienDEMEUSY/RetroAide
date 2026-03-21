"""Endpoint analyse : métriques déterministes + OpenHosta (advisor)."""

from __future__ import annotations

from fastapi import APIRouter

from ai.advisor import detect_missing_quarters, generate_checklist
from app.schemas import AnalyzeResponse, ChecklistItem, MissingQuarterItem, UserProfile
from core.calculator import (
    calculate_departure_age,
    estimate_quarters_worked,
    quarters_remaining,
)

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
def post_analyze(body: UserProfile) -> AnalyzeResponse:
    profile_dict = body.model_dump()

    departure_age = calculate_departure_age(body.birth_year)
    quarters_worked = estimate_quarters_worked(body.career_start_year)
    q_remaining = quarters_remaining(quarters_worked)

    missing_raw = detect_missing_quarters(profile_dict)
    checklist_raw = generate_checklist(profile_dict, missing_raw)

    return AnalyzeResponse(
        departure_age=departure_age,
        quarters_worked=quarters_worked,
        quarters_remaining=q_remaining,
        missing_quarters=[MissingQuarterItem(**m) for m in missing_raw],
        checklist=[ChecklistItem(**c) for c in checklist_raw],
    )
