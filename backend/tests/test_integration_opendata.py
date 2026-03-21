"""D5 — Optionnel : appels réels (RUN_LIVE_OPENDATA=1)."""

from __future__ import annotations

import os

import pytest

from tools.opendata_client import OpenDataClient

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_OPENDATA", "") != "1",
    reason="Définir RUN_LIVE_OPENDATA=1 pour exécuter les appels CNAV / data.gouv en direct.",
)
def test_live_cnav_first_dataset_record() -> None:
    ds_id = "montant-mensuel-moyen-de-la-retraite-globale-"
    with OpenDataClient() as c:
        data = c.fetch_cnav_records(ds_id, limit=1)
    assert isinstance(data.get("results"), list)


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_OPENDATA", "") != "1",
    reason="Définir RUN_LIVE_OPENDATA=1 pour exécuter les appels CNAV / data.gouv en direct.",
)
def test_live_data_gouv_search() -> None:
    with OpenDataClient() as c:
        data = c.search_data_gouv_datasets("retraite", page_size=1)
    assert isinstance(data.get("data"), list)
