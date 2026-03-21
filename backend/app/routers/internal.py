"""
D4 — Endpoint interne pour prévisualiser le contexte open data (protégé par token).
"""

from __future__ import annotations

import logging
import os
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException

from app.schemas import RetirementContextResponse, UserProfile
from tools.mcp_pipeline import run_enrichment

router = APIRouter(tags=["internal"])
log = logging.getLogger(__name__)


def _require_internal_bearer(authorization: str | None) -> None:
    expected = os.environ.get("INTERNAL_API_TOKEN", "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Endpoint interne désactivé : définir INTERNAL_API_TOKEN dans l'environnement.",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization Bearer requis.")
    token = authorization.removeprefix("Bearer ").strip()
    if token != expected:
        raise HTTPException(status_code=403, detail="Token interne invalide.")


@router.post("/context", response_model=RetirementContextResponse)
def post_retirement_context_preview(
    body: UserProfile,
    authorization: Annotated[str | None, Header()] = None,
) -> RetirementContextResponse:
    """
    Construit le même bloc texte que pour `/analyze` (open data), sans appeler le LLM.
    Utile pour debug, MCP, ou orchestrateurs externes.
    """
    _require_internal_bearer(authorization)
    log.info("[internal] POST /internal/context — prévisualisation contexte open data")
    profile_dict = body.model_dump()
    er = run_enrichment(profile_dict)
    return RetirementContextResponse.model_validate(er.to_dict())
