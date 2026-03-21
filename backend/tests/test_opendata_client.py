"""D5 — Client open data avec transport HTTP mocké."""

from __future__ import annotations

import httpx
import pytest

from tools.opendata_client import OpenDataClient


def test_fetch_cnav_records_gets_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert "data.cnav.fr" in str(request.url)
        assert request.url.params.get("limit") == "2"
        return httpx.Response(200, json={"results": [{"annee": 2020, "sexe": "2"}], "total_count": 1})

    transport = httpx.MockTransport(handler)
    c = OpenDataClient(client=httpx.Client(transport=transport, timeout=5.0))
    try:
        data = c.fetch_cnav_records("montant-mensuel-moyen-de-la-retraite-globale-", limit=2)
    finally:
        c.close()
    assert data["results"][0]["annee"] == 2020


def test_search_data_gouv_datasets_gets_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "www.data.gouv.fr" in str(request.url)
        assert request.url.params.get("q") == "retraite"
        payload = {
            "data": [
                {"title": "Jeu A", "organization": {"name": "Org"}, "slug": "jeu-a"},
            ]
        }
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    c = OpenDataClient(client=httpx.Client(transport=transport, timeout=5.0))
    try:
        data = c.search_data_gouv_datasets("retraite", page_size=3)
    finally:
        c.close()
    assert data["data"][0]["slug"] == "jeu-a"


def test_fetch_cnav_raises_on_http_error() -> None:
    transport = httpx.MockTransport(lambda _r: httpx.Response(500, json={"error": "x"}))
    c = OpenDataClient(client=httpx.Client(transport=transport, timeout=5.0))
    try:
        with pytest.raises(httpx.HTTPStatusError):
            c.fetch_cnav_records("any-id", limit=1)
    finally:
        c.close()
