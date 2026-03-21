"""
Couche LLM unique RetroAide : droits oubliés, checklist, glossaire (OpenHosta emulate).
"""

from __future__ import annotations

import logging
from typing import Any

from ai import config as _ai_env  # noqa: F401 — charge .env avant OpenHosta

from OpenHosta import emulate

logger = logging.getLogger(__name__)

FALLBACK_CHECKLIST: list[dict[str, str]] = [
    {
        "title": "Contrôler votre relevé de carrière",
        "detail": "Demandez vos relevés à la CNAV et à l’Agirc-Arrco (ou caisse équivalente) pour vérifier vos trimestres.",
        "url": "https://www.lassuranceretraite.fr",
    },
    {
        "title": "Simuler ou estimer votre départ",
        "detail": "Utilisez les outils officiels pour affiner les dates et montants avant toute décision.",
        "url": "https://www.info-retraite.fr",
    },
    {
        "title": "Prendre rendez-vous avec votre caisse",
        "detail": "Un conseiller peut valider votre situation personnelle et les pièces à fournir.",
        "url": "https://www.lassuranceretraite.fr",
    },
]


def _glossary_fallback(term: str) -> str:
    return (
        f"« {term} » est un mot employé par l’assurance retraite. "
        "Pour une explication précise adaptée à votre dossier, contactez votre caisse de retraite "
        "ou consultez les fiches sur info-retraite.fr."
    )


def _normalize_missing_quarters(raw: Any) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        row = {
            "period": str(item.get("period", "")).strip(),
            "reason": str(item.get("reason", "")).strip(),
            "action": str(item.get("action", "")).strip(),
        }
        if not row["period"] and not row["reason"] and not row["action"]:
            continue
        out.append(row)
    return out


def _normalize_checklist(raw: Any) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for item in raw:
        if isinstance(item, str):
            t = item.strip()
            if t:
                out.append({"title": t, "detail": "", "url": ""})
        elif isinstance(item, dict):
            title = str(item.get("title", item.get("step", ""))).strip()
            if not title:
                continue
            out.append(
                {
                    "title": title,
                    "detail": str(item.get("detail", item.get("description", ""))).strip(),
                    "url": str(item.get("url", item.get("link", ""))).strip(),
                }
            )
    return out


def detect_missing_quarters(profile: dict) -> list[dict[str, str]]:
    """
    Analyse le profil carrière (France, régime général simplifié) et identifie des périodes
    pouvant générer des trimestres souvent oubliés ou mal déclarés (enfants, chômage, arrêts longs, etc.).

    Retour : liste de dicts avec clés period, reason, action — français simple.
    """
    _ = profile  # fourni au modèle via inspection OpenHosta
    try:
        raw = emulate()
        return _normalize_missing_quarters(raw)
    except Exception as exc:  # noqa: BLE001 — fallback hackathon
        logger.warning("detect_missing_quarters: %s", exc)
        return []


def generate_checklist(
    profile: dict,
    missing_quarters: list[dict[str, str]],
) -> list[dict[str, str]]:
    """
    Produit 5 à 10 étapes concrètes, ordonnées, en français simple, avec liens d’administration
    quand ils sont connus.
    """
    _ = (profile, missing_quarters)
    try:
        raw = emulate()
        normalized = _normalize_checklist(raw)
        if not normalized:
            return list(FALLBACK_CHECKLIST)
        return normalized
    except Exception as exc:  # noqa: BLE001
        logger.warning("generate_checklist: %s", exc)
        return list(FALLBACK_CHECKLIST)


def explain_term(term: str) -> str:
    """
    Explique un terme de retraite en français très simple, max 3 phrases, sans jargon,
    pour une personne de 65 ans sans formation juridique.
    """
    _ = term
    try:
        raw = emulate()
        text = str(raw).strip() if raw is not None else ""
        if not text:
            return _glossary_fallback(term)
        return text
    except Exception as exc:  # noqa: BLE001
        logger.warning("explain_term: %s", exc)
        return _glossary_fallback(term)
