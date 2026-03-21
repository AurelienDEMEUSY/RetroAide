"""D4/D5 — Endpoint interne /internal/context."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tools.mcp_pipeline import EnrichmentResult, EnrichmentToolTrace

client = TestClient(app)

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


def test_internal_context_503_when_token_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("INTERNAL_API_TOKEN", raising=False)
    r = client.post(
        "/internal/context",
        json=_MINIMAL_BODY,
        headers={"Authorization": "Bearer x"},
    )
    assert r.status_code == 503


def test_internal_context_401_without_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERNAL_API_TOKEN", "secret-token")
    r = client.post("/internal/context", json=_MINIMAL_BODY)
    assert r.status_code == 401


def test_internal_context_403_wrong_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERNAL_API_TOKEN", "secret-token")
    r = client.post(
        "/internal/context",
        json=_MINIMAL_BODY,
        headers={"Authorization": "Bearer wrong"},
    )
    assert r.status_code == 403


@patch("app.routers.internal.run_enrichment")
def test_internal_context_200(
    mock_run: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_run.return_value = EnrichmentResult(
        context_block="bloc\nctx",
        sources_touched=["cnav:test"],
        tools=[
            EnrichmentToolTrace(
                tool="retroaide_open_data_bundle",
                ok=True,
                sources=["cnav:test"],
                error=None,
                sub_steps=[],
            )
        ],
    )
    monkeypatch.setenv("INTERNAL_API_TOKEN", "secret-token")
    r = client.post(
        "/internal/context",
        json=_MINIMAL_BODY,
        headers={"Authorization": "Bearer secret-token"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["context_block"] == "bloc\nctx"
    assert data["sources_touched"] == ["cnav:test"]
    assert data["tools"][0]["tool"] == "retroaide_open_data_bundle"
