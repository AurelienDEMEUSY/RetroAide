"""Endpoint glossaire : explication d’un terme via OpenHosta (advisor)."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from ai.advisor import explain_term
from app.schemas import GlossaryRequest, GlossaryResponse

router = APIRouter(tags=["glossary"])
log = logging.getLogger(__name__)


@router.post("/glossary", response_model=GlossaryResponse)
def post_glossary(body: GlossaryRequest) -> GlossaryResponse:
    term = body.term.strip()
    log.info("[glossary] début | terme=%r (longueur=%s)", term, len(term))
    text = explain_term(term)
    log.info("[glossary] fin | explication longueur=%s caractères", len(text))
    log.debug("[glossary] extrait: %s...", text[:120] if len(text) > 120 else text)
    return GlossaryResponse(explanation=text)
