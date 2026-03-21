"""
D2 — Client HTTP minimal pour API open data (timeouts, User-Agent identifiable).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = os.environ.get(
    "RETROAIDE_HTTP_USER_AGENT",
    "RetroAide/0.1 (hackathon; +https://github.com/hand-e-fr/OpenHosta)",
)
DEFAULT_TIMEOUT = float(os.environ.get("OPENDATA_TIMEOUT", "15"))


class OpenDataClient:
    """Client réutilisable (tests : injecter un mock transport)."""

    def __init__(
        self,
        *,
        timeout: float | None = None,
        user_agent: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=timeout or DEFAULT_TIMEOUT,
            headers={"User-Agent": user_agent or DEFAULT_USER_AGENT},
            follow_redirects=True,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OpenDataClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_cnav_records(self, dataset_id: str, *, limit: int = 3) -> dict[str, Any]:
        """GET Explore v2.1 — enregistrements d'un jeu CNAV."""
        base = "https://data.cnav.fr/api/explore/v2.1/catalog/datasets"
        url = f"{base}/{dataset_id}/records"
        logger.info("[opendata] CNAV GET %s | limit=%s", url, limit)
        response = self._client.get(url, params={"limit": limit})
        response.raise_for_status()
        data = response.json()
        logger.debug("[opendata] CNAV réponse | total_count=%s", data.get("total_count"))
        return data

    def search_data_gouv_datasets(self, query: str, *, page_size: int = 3) -> dict[str, Any]:
        """Recherche simple sur le catalogue data.gouv.fr (API v1)."""
        url = "https://www.data.gouv.fr/api/1/datasets/"
        logger.info("[opendata] data.gouv GET %s | q=%r page_size=%s", url, query, page_size)
        response = self._client.get(url, params={"q": query, "page_size": page_size})
        response.raise_for_status()
        data = response.json()
        logger.debug("[opendata] data.gouv | nb résultats=%s", len(data.get("data", [])))
        return data


def inventory_yaml_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "opendata_inventory.yaml"
