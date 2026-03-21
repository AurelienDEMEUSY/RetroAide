"""
Planification LLM des appels « outils » (équivalent MCP) avant exécution réelle.

Le modèle nomme explicitement les outils autorisés ; le backend exécute ensuite
`tool_open_data_bundle` de façon déterministe (liste blanche).
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from ai import config as _ai_config  # noqa: F401 — .env avant OpenHosta
from ai import guidance as _guidance

from OpenHosta import emulate

from tools.enrichment_handlers import TOOL_OPEN_DATA_BUNDLE

logger = logging.getLogger(__name__)

_TOOL_ORCHESTRATION_RULES = (
    "ÉTAPE : PLANIFICATION DES OUTILS (tu n’as pas encore les données brutes des API). "
    f'Outil disponible et seul autorisé : « {TOOL_OPEN_DATA_BUNDLE} » — agrège des extraits open data '
    "CNAV Explore et une recherche catalogue data.gouv.fr pour contextualiser un conseil retraite "
    "(données nationales / agrégées, pas le dossier personnel).\n"
    "Réponds UNIQUEMENT avec un objet JSON valide, sans markdown ni texte autour. Schéma exact :\n"
    '{"tool_calls":[{"name":"'
    + TOOL_OPEN_DATA_BUNDLE
    + '","rationale_for_user":"phrase courte en français clair pour une personne âgée : '
    'pourquoi on consulte ces sources publiques"}]}\n'
    "Tu peux mettre tool_calls vide [] seulement si le profil est totalement incohérent (années impossibles). "
    "Sinon, demande au moins un appel à cet outil."
)


def llm_tool_orchestration_enabled() -> bool:
    return os.environ.get("RETROAIDE_LLM_TOOL_ORCHESTRATION", "").lower() in ("1", "true", "yes")


def _strip_json_fence(text: str) -> str:
    s = text.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return s


def _parse_tool_plan(raw: Any) -> list[dict[str, str]]:
    if raw is None:
        return []
    if isinstance(raw, dict):
        payload = raw
    else:
        text = _strip_json_fence(str(raw).strip())
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("[llm_orchestrator] JSON plan invalide | aperçu=%r", text[:200])
            return []
    calls = payload.get("tool_calls")
    if not isinstance(calls, list):
        return []
    out: list[dict[str, str]] = []
    for item in calls:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        rationale = str(item.get("rationale_for_user", item.get("rationale", ""))).strip()
        if name:
            out.append({"name": name, "rationale_for_user": rationale})
    return out


def plan_retroaide_tool_calls(profile: dict[str, Any]) -> list[dict[str, str]]:
    """
    Demande au LLM quels outils nommés invoquer avant tout appel HTTP.
    Retour vide si échec parsing / exception.
    """
    logger.info("[llm_orchestrator] plan_retroaide_tool_calls | clés profil=%s", list(profile.keys()))
    _ = (
        profile,
        _guidance.SENIOR_AUDIENCE,
        _guidance.CONSEIL_RETRAITE_CADRE,
        _TOOL_ORCHESTRATION_RULES,
    )
    try:
        raw = emulate()
        parsed = _parse_tool_plan(raw)
        logger.info("[llm_orchestrator] plan parsé | %s appel(s) nommé(s)", len(parsed))
        return parsed
    except Exception:  # noqa: BLE001
        logger.exception("[llm_orchestrator] échec emulate (plan outils)")
        return []


def build_plan_preamble(calls: list[dict[str, str]]) -> str:
    """Bloc markdown préfixé au context_block pour transparence (UI / LLM aval)."""
    lines = [
        "## Choix des outils de recherche (avant appel aux sources publiques)",
        "",
        "Voici ce que l’assistant a décidé de consulter, et pourquoi (formulation simple) :",
        "",
    ]
    if not calls:
        lines.append(
            "_Aucun plan d’outil n’a pu être lu — les sources publiques sont chargées par politique produit._"
        )
    else:
        for c in calls:
            name = (c.get("name") or "").strip()
            why = (c.get("rationale_for_user") or "").strip() or "—"
            lines.append(f"- **{name}** : {why}")
    return "\n".join(lines)
