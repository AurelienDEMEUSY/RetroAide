"""POST /api/v1/report/pdf — génération PDF depuis un rapport JSON pré-calculé."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


_REPORT_JSON = {
    "identity": {
        "nom_utilisateur": "Jean Dupont",
        "id_dossier": "00000000-0000-0000-0000-000000000000",
        "ville_signature": "Lyon",
        "date_signature": "2026-03-21",
    },
    "key_figures": {
        "age_legal": 63,
        "age_taux_plein_auto": 67,
        "trimestres_ok": 172,
        "trimestres_requis": 172,
        "trimestres_restants": 0,
        "montant_estime": 1540,
    },
    "special_cases": {
        "nb_enfants": 2,
        "nb_mois_armee": None,
        "nb_trimestres_avant_20": None,
        "pays_etranger": "",
        "liste_periodes_manquantes": "Chômage 2003",
    },
    "markdown": {
        "synthese": "# Synthèse\\n\\nParagraphe de test " + "x" * 80,
        "checklist": "## Étapes\\n\\n1. **Étape 1**",
        "cas_particuliers": "## Cas particuliers",
        "parcours_guide": "## Parcours guidé",
        "document_complet": "# Synthèse\\n\\nTexte du document " + "y" * 80,
    },
    "enrichment": {
        "context_block": "[ctx]",
        "sources_touched": ["cnav:mock"],
        "tools": [
            {
                "tool": "retroaide_open_data_bundle",
                "ok": True,
                "sources": ["cnav:mock"],
                "error": None,
                "sub_steps": [],
            }
        ],
    },
    "analyze": {
        "departure_age": 63,
        "quarters_worked": 172,
        "quarters_remaining": 0,
        "missing_quarters": [],
        "checklist": [{"title": "Étape 1", "detail": "Détail", "url": "https://www.info-retraite.fr"}],
        "guided_journey": [],
        "enrichment": {
            "context_block": "[ctx]",
            "sources_touched": ["cnav:mock"],
            "tools": [
                {
                    "tool": "retroaide_open_data_bundle",
                    "ok": True,
                    "sources": ["cnav:mock"],
                    "error": None,
                    "sub_steps": [],
                }
            ],
        },
    },
}


def test_post_report_pdf_returns_pdf_bytes() -> None:
    """Le nouvel endpoint /report/pdf génère un PDF sans appel pipeline."""
    response = client.post("/api/v1/report/pdf", json=_REPORT_JSON)
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/pdf")
    assert response.content[:4] == b"%PDF"
    assert "attachment" in response.headers.get("content-disposition", "")


def test_post_report_pdf_rejects_malformed_input() -> None:
    """Un JSON incomplet est rejeté en 422."""
    response = client.post("/api/v1/report/pdf", json={"identity": {"nom_utilisateur": "Test"}})
    assert response.status_code == 422
