from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app
from tools.mcp_pipeline import EnrichmentResult, EnrichmentToolTrace

client = TestClient(app)

_ENRICHMENT_MOCK = EnrichmentResult(
    context_block="[contexte test]",
    sources_touched=["cnav:mock"],
    tools=[
        EnrichmentToolTrace(
            tool="retroaide_open_data_bundle",
            ok=True,
            sources=["cnav:mock"],
            error=None,
            sub_steps=[],
        )
    ],
)

_MINIMAL_BODY = {
    "birth_month": 1,
    "birth_year": 1963,
    "marital_status": "celibataire",
    "nb_enfants": 2,
    "professional_statuses": ["salarie_prive"],
    "career_start_age": "avant_20",
    "career_breaks": [],
    "currently_employed": False,
    "current_income_annual": 35000,
    "validated_quarters": 160,
    "main_objective": "partir_tot",
    "target_departure_age": 63,
}


@patch("app.routers.analyze.generate_guided_journey")
@patch("app.routers.analyze.generate_checklist")
@patch("app.routers.analyze.detect_missing_quarters")
@patch("app.routers.analyze.run_enrichment", return_value=_ENRICHMENT_MOCK)
def test_post_analyze_returns_expected_shape(
    mock_enrichment: Mock,
    mock_missing: Mock,
    mock_checklist: Mock,
    mock_journey: Mock,
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

    response = client.post("/api/v1/analyze", json=_MINIMAL_BODY)
    assert response.status_code == 200
    data = response.json()
    assert data["departure_age"] == 63  # 1961 <= 1963 < 1968
    assert data["quarters_worked"] == 172  # plafonné (44 ans × 4 > 172)
    assert data["quarters_remaining"] == 0
    assert len(data["missing_quarters"]) == 1
    assert data["missing_quarters"][0]["period"] == "Chômage 2003"
    assert len(data["checklist"]) == 1
    assert data["checklist"][0]["title"] == "Étape 1"
    assert len(data["guided_journey"]) == 1
    assert data["guided_journey"][0]["phase"] == "recap"
    assert data["enrichment"]["context_block"] == "[contexte test]"
    assert data["enrichment"]["tools"][0]["tool"] == "retroaide_open_data_bundle"

    mock_enrichment.assert_called_once()
    mock_missing.assert_called_once()
    mock_checklist.assert_called_once()
    mock_journey.assert_called_once()
    call_profile = mock_missing.call_args[0][0]
    assert call_profile["birth_year"] == 1963
    assert mock_missing.call_args.kwargs.get("retrieval_context") == "[contexte test]"
    assert mock_checklist.call_args.kwargs.get("retrieval_context") == "[contexte test]"


def test_post_analyze_validation_error_on_bad_status() -> None:
    bad = {**_MINIMAL_BODY, "professional_statuses": ["invalide"]}
    response = client.post("/api/v1/analyze", json=bad)
    assert response.status_code == 422
