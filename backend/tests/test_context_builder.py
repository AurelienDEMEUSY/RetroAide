"""D3/D5 — Bloc contexte open data (inventaire YAML + résumés)."""

from __future__ import annotations

import os

import httpx
import pytest

from tools.context_builder import build_retirement_context_block
from tools.opendata_client import OpenDataClient


def test_build_context_disabled_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_OPENDATA_CONTEXT", "false")
    block, sources = build_retirement_context_block({"birth_year": 1960})
    assert block == ""
    assert sources == []


def test_build_context_with_mock_http(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_OPENDATA_CONTEXT", "true")

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if "data.cnav.fr" in u:
            return httpx.Response(
                200,
                json={"results": [{"annee": 2019, "montant": 1200}], "total_count": 1},
            )
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
        block, sources = build_retirement_context_block({}, client=client)
    finally:
        client.close()

    assert "Open data CNAV" in block
    assert "data.gouv.fr" in block
    assert any(s.startswith("cnav:") for s in sources)
    assert "data.gouv:search" in sources


def test_summarize_handles_flat_cnav_rows() -> None:
    from tools import context_builder as cb

    text = cb._summarize_cnav_records(  # noqa: SLF001
        {"results": [{"annee": 2020, "x": 1}, "not-a-dict"]},
        max_items=2,
    )
    assert "annee" in text
    assert "not-a-dict" in text
