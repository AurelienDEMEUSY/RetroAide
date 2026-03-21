"""
Orchestrateur enrichissement : mêmes handlers que le serveur MCP, appelés en process par FastAPI.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from tools.enrichment_handlers import (
    TOOL_OPEN_DATA_BUNDLE,
    EnrichmentSubStep,
    OpenDataBundleResult,
    tool_open_data_bundle,
)
from tools.llm_research_orchestrator import (
    build_plan_preamble,
    llm_tool_orchestration_enabled,
    plan_retroaide_tool_calls,
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

    Si ``RETROAIDE_LLM_TOOL_ORCHESTRATION=true``, un premier appel LLM nomme explicitement
    l’outil ``retroaide_open_data_bundle`` avant l’exécution HTTP ; le préambule est préfixé
    au ``context_block``.
    """
    logger.info("[mcp_pipeline] run_enrichment | démarrage")
    use_llm_tools = llm_tool_orchestration_enabled()
    plan_calls: list[dict[str, str]] = []
    if use_llm_tools:
        plan_calls = plan_retroaide_tool_calls(profile)

    bundle = tool_open_data_bundle(profile, client=client)

    context_block = bundle.context_block
    merged_sub_steps: list[EnrichmentSubStep] = list(bundle.sub_steps)

    if use_llm_tools:
        preamble = build_plan_preamble(plan_calls)
        requested = {c.get("name", "").strip() for c in plan_calls}
        if requested and TOOL_OPEN_DATA_BUNDLE not in requested:
            preamble += (
                "\n\n> _Les outils demandés ne sont pas tous reconnus par le serveur ; "
                "le jeu de sources publiques standard a tout de même été chargé pour le conseil._"
            )
        context_block = f"{preamble}\n\n---\n\n{bundle.context_block}"
        plan_step = EnrichmentSubStep(
            source="llm_tool_plan",
            ok=True,
            detail=json.dumps(plan_calls, ensure_ascii=False),
        )
        merged_sub_steps = [plan_step, *bundle.sub_steps]

    ok, err = _bundle_trace_ok(bundle)
    trace = EnrichmentToolTrace(
        tool=TOOL_OPEN_DATA_BUNDLE,
        ok=ok,
        sources=list(bundle.sources_touched),
        error=err,
        sub_steps=[s.to_dict() for s in merged_sub_steps],
    )
    logger.info(
        "[mcp_pipeline] run_enrichment | tool=%s ok=%s sources=%s",
        trace.tool,
        trace.ok,
        trace.sources,
    )
    return EnrichmentResult(
        context_block=context_block,
        sources_touched=list(bundle.sources_touched),
        tools=[trace],
    )
