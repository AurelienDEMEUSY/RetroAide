"""
Transport stdio (défaut FastMCP) — outils branchés sur les APIs externes CNAV / data.gouv.
Lancer depuis le répertoire backend : python -m mcp_server
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from tools.enrichment_handlers import tool_open_data_bundle
from tools.llm_research_orchestrator import plan_retroaide_tool_calls

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("retroaide-enrichment")


@mcp.tool()
def retroaide_llm_plan_open_data_tools(profile: dict) -> dict:
    """
    Demande au modèle (OpenHosta) quels outils de recherche open data invoquer, **sans** appeler CNAV/data.gouv.
    Utile pour un agent en deux temps : planifier puis exécuter `retroaide_open_data_context`.
    Retour : { "tool_calls": [ { "name", "rationale_for_user" }, ... ] }.
    """
    logger.info("[mcp] tool retroaide_llm_plan_open_data_tools | clés profil=%s", list(profile.keys()))
    return {"tool_calls": plan_retroaide_tool_calls(profile)}


@mcp.tool()
def retroaide_open_data_context(profile: dict) -> dict:
    """
    Récupère un bundle de contexte open data (CNAV + data.gouv) pour enrichir un conseil retraite.
    `profile` est le JSON du formulaire (UserProfile) ; champs optionnels pour filtrage futur.
    Retour : context_block, sources_touched, sub_steps (détail par source HTTP).
    """
    logger.info("[mcp] tool retroaide_open_data_context | clés profil=%s", list(profile.keys()))
    return tool_open_data_bundle(profile).to_dict()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
