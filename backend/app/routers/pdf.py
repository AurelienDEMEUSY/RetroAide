"""Export PDF — endpoint autonome (étape 3 du pipeline chaîné)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Response

from app.schemas import AnalyzeReportResponse
from core.pdf_export import generate_pdf_bytes

logger = logging.getLogger(__name__)

router = APIRouter(tags=["pdf"])


def _make_pdf_response(report_dict: dict) -> Response:
    """Génère le PDF à partir d'un dict rapport et renvoie la réponse HTTP."""
    try:
        pdf_bytes = generate_pdf_bytes(report_dict)
    except Exception:
        logger.exception("[pdf] génération PDF échouée")
        raise HTTPException(status_code=500, detail="Échec de la génération du PDF") from None
    if not pdf_bytes:
        raise HTTPException(status_code=500, detail="PDF vide")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="retroaide-rapport.pdf"',
        },
    )


@router.post(
    "/report/pdf",
    summary="Générer un PDF à partir du rapport JSON",
    description=(
        "Accepte un `AnalyzeReportResponse` JSON (sortie de `POST /ai/analyze`) "
        "et génère le PDF — aucun calcul ni appel LLM."
    ),
    response_class=Response,
    responses={
        200: {
            "description": "Fichier PDF (téléchargement)",
            "content": {"application/pdf": {}},
        },
        500: {"description": "Échec de génération du PDF"},
    },
)
def post_report_pdf(body: AnalyzeReportResponse) -> Response:
    """Étape 3 : génération PDF depuis un rapport JSON pré-calculé."""
    logger.info("[pdf] POST /report/pdf — PDF depuis JSON")
    payload = body.model_dump(mode="json")
    return _make_pdf_response(payload)


