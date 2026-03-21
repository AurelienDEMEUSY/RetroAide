"""Pipeline enrichissement (équivalent MCP in-process)."""

from __future__ import annotations

import httpx
import pytest

from tools.mcp_pipeline import run_enrichment
from tools.opendata_client import OpenDataClient


def test_run_enrichment_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_OPENDATA_CONTEXT", "false")
    r = run_enrichment({"birth_year": 1960})
    assert r.context_block == ""
    assert r.sources_touched == []
    assert r.tools[0].tool == "retroaide_open_data_bundle"


def test_run_enrichment_with_mock_http(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_OPENDATA_CONTEXT", "true")

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if "data.cnav.fr" in u:
            return httpx.Response(200, json={"results": [{"annee": 2019}], "total_count": 1})
        if "data.gouv.fr" in u:
            return httpx.Response(
                200,
                json={"data": [{"title": "T", "organization": {"name": "O"}, "slug": "s"}]},
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport, timeout=5.0)
    client = OpenDataClient(client=http)
    try:
        r = run_enrichment({}, client=client)
    finally:
        client.close()

    assert "Open data CNAV" in r.context_block
    assert r.tools[0].ok is True
    assert len(r.tools[0].sub_steps) >= 2
