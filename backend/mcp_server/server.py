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


@mcp.tool()
def retroaide_scrape_webpage(url: str) -> dict:
    """
    Extrait le texte brut d'une page Web spécifiée.
    Utile pour récupérer des informations dynamiques de sources externes de manière adhoc.
    Retour : dict contenant l'URL, le texte extrait et le statut.
    """
    import httpx
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return {"url": url, "error": "BeautifulSoup non installé (bs4).", "status": "error"}

    logger.info(f"[mcp] tool retroaide_scrape_webpage | url={url}")
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Retrait des balises non-pertinentes au texte
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = " ".join(soup.stripped_strings)
            
            return {
                "url": url,
                "content": text[:10000],  # Limite pour éviter les surcharges de contexte texte trop larges
                "status": "success"
            }
    except Exception as e:
        logger.exception("[mcp] erreur récupération webpage %s", url)
        return {"url": url, "error": str(e), "status": "error"}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
