"""
Orchestrateur enrichissement : mêmes handlers que le serveur MCP, appelés en process par FastAPI.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from tools.enrichment_handlers import (
    TOOL_OPEN_DATA_BUNDLE,
    OpenDataBundleResult,
    tool_open_data_bundle,
)
from tools.opendata_client import OpenDataClient

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentToolTrace:
    """Une entrée de trace (outil MCP équivalent)."""

    tool: str
    ok: bool
    sources: list[str] = field(default_factory=list)
    error: str | None = None
    sub_steps: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "ok": self.ok,
            "sources": list(self.sources),
            "error": self.error,
            "sub_steps": list(self.sub_steps),
        }


@dataclass
class EnrichmentResult:
    """Résultat agrégé pour injection LLM + réponse API."""

    context_block: str
    sources_touched: list[str]
    tools: list[EnrichmentToolTrace]

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_block": self.context_block,
            "sources_touched": list(self.sources_touched),
            "tools": [t.to_dict() for t in self.tools],
        }


def _bundle_trace_ok(bundle: OpenDataBundleResult) -> tuple[bool, str | None]:
    """False seulement si inventaire YAML introuvable (bloc vide et erreur explicite)."""
    for s in bundle.sub_steps:
        if s.source == "inventory_yaml" and not s.ok:
            return False, s.error
    return True, None


def run_enrichment(
    profile: dict[str, Any],
    *,
    client: OpenDataClient | None = None,
) -> EnrichmentResult:
    """
    Enchaîne les outils d’enrichissement (aujourd’hui : bundle open data uniquement).
    """
    logger.info("[mcp_pipeline] run_enrichment | démarrage")
    bundle = tool_open_data_bundle(profile, client=client)
    ok, err = _bundle_trace_ok(bundle)
    trace = EnrichmentToolTrace(
        tool=TOOL_OPEN_DATA_BUNDLE,
        ok=ok,
        sources=list(bundle.sources_touched),
        error=err,
        sub_steps=[s.to_dict() for s in bundle.sub_steps],
    )
    logger.info(
        "[mcp_pipeline] run_enrichment | tool=%s ok=%s sources=%s",
        trace.tool,
        trace.ok,
        trace.sources,
    )
    return EnrichmentResult(
        context_block=bundle.context_block,
        sources_touched=list(bundle.sources_touched),
        tools=[trace],
    )
