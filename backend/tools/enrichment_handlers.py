"""
Handlers d’enrichissement (APIs externes) — même implémentation pour FastAPI et serveur MCP.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

import yaml

from tools.opendata_client import OpenDataClient, inventory_yaml_path

logger = logging.getLogger(__name__)

TOOL_OPEN_DATA_BUNDLE = "retroaide_open_data_bundle"


def _opendata_enabled() -> bool:
    return os.environ.get("ENABLE_OPENDATA_CONTEXT", "true").lower() in ("1", "true", "yes")


def summarize_cnav_records(payload: dict[str, Any], max_items: int = 2) -> str:
    """CNAV Explore v2.1 renvoie des objets plats dans `results`."""
    results = payload.get("results") or []
    lines: list[str] = []
    for row in results[:max_items]:
        if not isinstance(row, dict):
            lines.append(str(row)[:500])
            continue
        short = {k: row[k] for k in list(row)[:12]}
        lines.append(str(short))
    return "\n".join(lines) if lines else "(aucun enregistrement)"


def summarize_data_gouv(payload: dict[str, Any]) -> str:
    data = payload.get("data") or []
    lines: list[str] = []
    for item in data[:3]:
        title = item.get("title", "")
        org = (item.get("organization") or {}).get("name", "")
        rid = item.get("slug", "")
        lines.append(f"- {title} ({org}) — https://www.data.gouv.fr/datasets/{rid}/")
    return "\n".join(lines) if lines else "(aucun jeu)"


@dataclass
class EnrichmentSubStep:
    """Une requête HTTP ou étape interne au sein du bundle open data."""

    source: str
    ok: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "ok": self.ok, "error": self.error}


@dataclass
class OpenDataBundleResult:
    """Sortie de l’outil `retroaide_open_data_bundle` (MCP + pipeline API)."""

    context_block: str
    sources_touched: list[str]
    sub_steps: list[EnrichmentSubStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_block": self.context_block,
            "sources_touched": list(self.sources_touched),
            "sub_steps": [s.to_dict() for s in self.sub_steps],
        }


def tool_open_data_bundle(
    profile: dict[str, Any],
    *,
    client: OpenDataClient | None = None,
) -> OpenDataBundleResult:
    """
    Agrège CNAV + data.gouv selon l’inventaire YAML.
    `profile` est réservé au filtrage futur (régime, territoire).
    """
    _ = profile
    sub_steps: list[EnrichmentSubStep] = []
    sources: list[str] = []
    sections: list[str] = []

    if not _opendata_enabled():
        logger.info("[enrichment] ENABLE_OPENDATA_CONTEXT désactivé → bloc vide")
        return OpenDataBundleResult(context_block="", sources_touched=[], sub_steps=[])

    inv_path = inventory_yaml_path()
    if not inv_path.is_file():
        logger.warning("[enrichment] inventaire absent: %s", inv_path)
        sub_steps.append(
            EnrichmentSubStep(source="inventory_yaml", ok=False, error=f"fichier absent: {inv_path}")
        )
        return OpenDataBundleResult(context_block="", sources_touched=[], sub_steps=sub_steps)

    with open(inv_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    own_client = client is None
    http = client or OpenDataClient()
    try:
        disclaimer = inventory.get("disclaimer", "").strip()
        if disclaimer:
            sections.append(f"[Mention légale contexte]\n{disclaimer}")

        for entry in inventory.get("cnav_datasets", []):
            ds_id = entry["dataset_id"]
            limit = int(entry.get("records_limit", 3))
            label = f"cnav:{ds_id}"
            try:
                raw = http.fetch_cnav_records(ds_id, limit=limit)
                sources.append(label)
                blob = summarize_cnav_records(raw)
                sections.append(
                    f"[Open data CNAV — {entry.get('title', ds_id)}]\n"
                    f"Fiche: {entry.get('portal_page', '')}\n{blob}"
                )
                sub_steps.append(EnrichmentSubStep(source=label, ok=True, error=None))
            except Exception as exc:  # noqa: BLE001
                logger.exception("[enrichment] échec récupération %s", label)
                err = str(exc)[:500]
                sub_steps.append(EnrichmentSubStep(source=label, ok=False, error=err))

        dg = inventory.get("data_gouv", {})
        search = dg.get("search", {})
        q = search.get("query", "retraite")
        page_size = int(search.get("page_size", 3))
        dg_label = "data.gouv:search"
        try:
            raw = http.search_data_gouv_datasets(q, page_size=page_size)
            sources.append(dg_label)
            sections.append(f"[Jeux data.gouv.fr pour « {q} »]\n{summarize_data_gouv(raw)}")
            sub_steps.append(EnrichmentSubStep(source=dg_label, ok=True, error=None))
        except Exception as exc:  # noqa: BLE001
            logger.exception("[enrichment] échec recherche data.gouv")
            sub_steps.append(EnrichmentSubStep(source=dg_label, ok=False, error=str(exc)[:500]))

    finally:
        if own_client:
            http.close()

    block = "\n\n---\n\n".join(s for s in sections if s)
    logger.info("[enrichment] bundle assemblé | sources=%s | longueur=%s", sources, len(block))
    return OpenDataBundleResult(context_block=block, sources_touched=sources, sub_steps=sub_steps)
