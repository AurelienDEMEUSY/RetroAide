"""POST /api/v1/ai/analyze — phase LLM depuis un ComputeResponse."""

from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_COMPUTE_OUTPUT = {
    "departure_age": 63,
    "age_taux_plein_auto": 67,
    "quarters_worked": 172,
    "quarters_remaining": 0,
    "enrichment": {
        "context_block": "[ctx test]",
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
    "profile": {
        "birth_year": 1963,
        "career_start_year": 1982,
        "status": "salarie_prive",
        "currently_employed": False,
        "had_children": True,
        "had_unemployment": True,
        "had_long_sick_leave": False,
        "had_military_service": False,
        "long_part_time_years": False,
        "full_name": "",
        "ville_signature": "",
        "nb_enfants": None,
        "nb_mois_armee": None,
        "nb_trimestres_avant_20": None,
        "pays_etranger": "",
        "montant_estime_euros": None,
    },
}


@patch("app.routers.ai_analyze.synthesize_report_markdown", return_value="")
@patch("app.routers.ai_analyze.generate_guided_journey")
@patch("app.routers.ai_analyze.generate_checklist")
@patch("app.routers.ai_analyze.detect_missing_quarters")
def test_post_ai_analyze_returns_full_report(
    mock_missing: Mock,
    mock_checklist: Mock,
    mock_journey: Mock,
    _synth: Mock,
) -> None:
    mock_missing.return_value = [
        {"period": "Chômage 2003", "reason": "Trimestres possibles", "action": "Relevé Pôle emploi"},
    ]
    mock_checklist.return_value = [
        {"title": "Étape 1", "detail": "Faire X", "url": "https://www.info-retraite.fr"},
    ]
    mock_journey.return_value = [
        {
            "step": 1,
            "phase": "recap",
            "title": "Résumé",
            "content": "Texte.",
            "optional_prompt": "",
        }
    ]

    body = {
        "compute": _COMPUTE_OUTPUT,
        "full_name": "Jean Dupont",
        "ville_signature": "Lyon",
        "nb_enfants": 2,
        "montant_estime_euros": 1540,
        "pays_etranger": "Allemagne",
    }
    response = client.post("/api/v1/ai/analyze", json=body)
    assert response.status_code == 200
    data = response.json()

    # Structure du rapport
    assert data["identity"]["nom_utilisateur"] == "Jean Dupont"
    assert data["identity"]["ville_signature"] == "Lyon"
    assert data["key_figures"]["age_legal"] == 63
    assert data["key_figures"]["trimestres_ok"] == 172
    assert data["key_figures"]["montant_estime"] == 1540
    assert data["special_cases"]["nb_enfants"] == 2

    # Markdown
    assert len(data["markdown"]["document_complet"]) > 50

    # Analyze core
    assert data["analyze"]["departure_age"] == 63
    assert len(data["analyze"]["missing_quarters"]) == 1

    # Les LLM ont bien été appelés avec le bon contexte
    mock_missing.assert_called_once()
    assert mock_missing.call_args.kwargs.get("retrieval_context") == "[ctx test]"


def test_post_ai_analyze_validation_error_without_compute() -> None:
    response = client.post("/api/v1/ai/analyze", json={"full_name": "Test"})
    assert response.status_code == 422
