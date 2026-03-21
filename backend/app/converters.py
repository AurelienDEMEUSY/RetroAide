"""Convertisseurs partagés entre routeurs (enrichment → schema, tools summary)."""

from __future__ import annotations

from app.schemas import EnrichmentSection, EnrichmentTraceItem
from tools.mcp_pipeline import EnrichmentResult


def enrichment_to_section(er: EnrichmentResult) -> EnrichmentSection:
    """Convertit un ``EnrichmentResult`` (dataclass interne) en ``EnrichmentSection`` (schéma API)."""
    return EnrichmentSection(
        context_block=er.context_block,
        sources_touched=list(er.sources_touched),
        tools=[
            EnrichmentTraceItem(
                tool=t.tool,
                ok=t.ok,
                sources=list(t.sources),
                error=t.error,
                sub_steps=list(t.sub_steps),
            )
            for t in er.tools
        ],
    )


def tools_summary_text(enrichment: EnrichmentSection) -> str:
    """Résumé compact des outils (pour injecter dans le parcours guidé LLM)."""
    parts: list[str] = []
    for t in enrichment.tools:
        label = "ok" if t.ok else "erreur ou partiel"
        parts.append(f"{t.tool} ({label})")
    return " ; ".join(parts) if parts else ""
