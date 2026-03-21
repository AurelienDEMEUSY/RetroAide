"""
D3 — Facade : assemble le bloc open data pour OpenHosta (implémentation dans enrichment_handlers).
"""

from __future__ import annotations

from typing import Any

from tools.enrichment_handlers import (
    summarize_cnav_records,
    summarize_data_gouv,
    tool_open_data_bundle,
)
from tools.opendata_client import OpenDataClient, inventory_yaml_path

# Compat tests / imports historiques
_summarize_cnav_records = summarize_cnav_records
_summarize_data_gouv = summarize_data_gouv


def build_retirement_context_block(
    profile: dict[str, Any],
    *,
    client: OpenDataClient | None = None,
) -> tuple[str, list[str]]:
    """
    Récupère des extraits open data et les formate pour le LLM.
    Retourne (bloc_texte, liste des identifiants de sources touchées).
    """
    out = tool_open_data_bundle(profile, client=client)
    return out.context_block, out.sources_touched


__all__ = [
    "build_retirement_context_block",
    "inventory_yaml_path",
    "summarize_cnav_records",
    "summarize_data_gouv",
]
