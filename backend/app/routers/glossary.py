"""Endpoint glossaire : explication d’un terme via OpenHosta (advisor)."""

from __future__ import annotations

from fastapi import APIRouter

from ai.advisor import explain_term
from app.schemas import GlossaryRequest, GlossaryResponse

router = APIRouter(tags=["glossary"])


@router.post("/glossary", response_model=GlossaryResponse)
def post_glossary(body: GlossaryRequest) -> GlossaryResponse:
    text = explain_term(body.term.strip())
    return GlossaryResponse(explanation=text)
