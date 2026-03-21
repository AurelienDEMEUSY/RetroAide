"""POST /api/v1/analyze/report — JSON structuré + markdown."""

from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app
from tools.mcp_pipeline import EnrichmentResult, EnrichmentToolTrace

client = TestClient(app)

_REPORT_ENRICHMENT = EnrichmentResult(
    context_block="[ctx]",
    sources_touched=["cnav:mock"],
    tools=[
        EnrichmentToolTrace(
            tool="retroaide_open_data_bundle",
            ok=True,
            sources=["cnav:mock"],
            error=None,
            sub_steps=[{"source": "cnav:x", "ok": True, "error": None}],
        )
    ],
)

_MINIMAL_BODY = {
    "birth_year": 1963,
    "career_start_year": 1982,
    "status": "salarie_prive",
    "currently_employed": False,
    "had_children": True,
    "had_unemployment": True,
    "had_long_sick_leave": False,
    "had_military_service": False,
    "long_part_time_years": False,
}


@patch("app.routers.analyze.synthesize_report_markdown", return_value="")
@patch("app.routers.analyze.generate_guided_journey")
@patch("app.routers.analyze.generate_checklist")
@patch("app.routers.analyze.detect_missing_quarters")
@patch("app.routers.analyze.run_enrichment", return_value=_REPORT_ENRICHMENT)
def test_post_analyze_report_returns_structured_and_markdown(
    _enrich: Mock,
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
            "title": "Lecture du dossier",
            "content": "Nous reprenons vos indications.",
            "optional_prompt": "",
        }
    ]

    body = {
        **_MINIMAL_BODY,
        "full_name": "Jean Dupont",
        "ville_signature": "Lyon",
        "nb_enfants": 2,
        "montant_estime_euros": 1540,
        "pays_etranger": "Allemagne",
    }
    response = client.post("/api/v1/analyze/report", json=body)
    assert response.status_code == 200
    data = response.json()

    assert data["identity"]["nom_utilisateur"] == "Jean Dupont"
    assert data["identity"]["ville_signature"] == "Lyon"
    assert len(data["identity"]["id_dossier"]) >= 32
    assert data["identity"]["date_signature"]

    assert data["key_figures"]["age_legal"] == 63
    assert data["key_figures"]["age_taux_plein_auto"] == 67
    assert data["key_figures"]["trimestres_ok"] == 172
    assert data["key_figures"]["trimestres_requis"] == 172
    assert data["key_figures"]["trimestres_restants"] == 0
    assert data["key_figures"]["montant_estime"] == 1540

    assert data["special_cases"]["nb_enfants"] == 2
    assert "Chômage 2003" in data["special_cases"]["liste_periodes_manquantes"]
    assert data["special_cases"]["pays_etranger"] == "Allemagne"

    assert "#" in data["markdown"]["synthese"]
    assert "## Étapes" in data["markdown"]["checklist"]
    assert "Parcours guidé" in data["markdown"]["parcours_guide"]
    assert "Cas particuliers" in data["markdown"]["cas_particuliers"]
    assert len(data["markdown"]["document_complet"]) > 50

    assert data["analyze"]["departure_age"] == 63
    assert len(data["analyze"]["missing_quarters"]) == 1
    assert data["enrichment"]["context_block"] == "[ctx]"
    assert data["analyze"]["enrichment"]["context_block"] == "[ctx]"


_EMPTY_ENRICHMENT = EnrichmentResult(
    context_block="",
    sources_touched=[],
    tools=[
        EnrichmentToolTrace(
            tool="retroaide_open_data_bundle",
            ok=True,
            sources=[],
            error=None,
            sub_steps=[],
        )
    ],
)


@patch("app.routers.analyze.synthesize_report_markdown", return_value="# Synthèse LLM\n\nParagraphe détaillé " + "x" * 80)
@patch("app.routers.analyze.generate_guided_journey", return_value=[])
@patch("app.routers.analyze.generate_checklist")
@patch("app.routers.analyze.detect_missing_quarters")
@patch("app.routers.analyze.run_enrichment", return_value=_EMPTY_ENRICHMENT)
def test_post_analyze_report_uses_llm_synthese_when_long_enough(
    _enrich: Mock,
    mock_missing: Mock,
    mock_checklist: Mock,
    _journey: Mock,
    _synth: Mock,
) -> None:
    mock_missing.return_value = []
    mock_checklist.return_value = [{"title": "A", "detail": "", "url": ""}]
    r = client.post("/api/v1/analyze/report", json=_MINIMAL_BODY)
    assert r.status_code == 200
    assert r.json()["markdown"]["synthese"].startswith("# Synthèse LLM")


def test_post_analyze_report_rejects_montant_estime_zero() -> None:
    bad = {**_MINIMAL_BODY, "montant_estime_euros": 0}
    r = client.post("/api/v1/analyze/report", json=bad)
    assert r.status_code == 422
