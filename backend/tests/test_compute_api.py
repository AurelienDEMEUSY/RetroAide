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
    assert data["profile"]["career_start_year"] == 1982


@patch("app.routers.compute.run_enrichment", return_value=_ENRICHMENT_MOCK)
def test_post_compute_validation_error_on_bad_body(_mock_enrich) -> None:
    bad = {**_MINIMAL_BODY, "status": "invalide"}
    response = client.post("/api/v1/compute", json=bad)
    assert response.status_code == 422
