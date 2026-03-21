"""POST /api/v1/compute — calculs déterministes + enrichissement (pas de LLM)."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from tools.mcp_pipeline import EnrichmentResult, EnrichmentToolTrace

client = TestClient(app)

_ENRICHMENT_MOCK = EnrichmentResult(
    context_block="[contexte enrichissement]",
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


@patch("app.routers.compute.run_enrichment", return_value=_ENRICHMENT_MOCK)
def test_post_compute_returns_expected_shape(_mock_enrich) -> None:
    """Le compute ne fait pas d'appel LLM et retourne les chiffres + enrichissement."""
    response = client.post("/api/v1/compute", json=_MINIMAL_BODY)
    assert response.status_code == 200
    data = response.json()

    assert data["departure_age"] == 63
    assert data["age_taux_plein_auto"] == 67
    assert data["quarters_worked"] == 172
    assert data["quarters_remaining"] == 0
    assert data["enrichment"]["context_block"] == "[contexte enrichissement]"
    assert data["enrichment"]["tools"][0]["tool"] == "retroaide_open_data_bundle"
    # Le profil est inclus pour chaînage
    assert data["profile"]["birth_year"] == 1963
    assert data["profile"]["career_start_age"] == "avant_20"


@patch("app.routers.compute.run_enrichment", return_value=_ENRICHMENT_MOCK)
def test_post_compute_validation_error_on_bad_body(_mock_enrich) -> None:
    bad = {**_MINIMAL_BODY, "professional_statuses": ["invalide"]}
    response = client.post("/api/v1/compute", json=bad)
    assert response.status_code == 422
