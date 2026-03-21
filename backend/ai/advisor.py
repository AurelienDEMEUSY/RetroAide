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
    logger.debug(
        "[advisor] _normalize_missing_quarters | type=%s | aperçu=%r",
        type(raw).__name__,
        (raw[:2] if isinstance(raw, list) and len(raw) > 2 else raw),
    )
    if not isinstance(raw, list):
        logger.warning("[advisor] missing_quarters: attendu une list, reçu %s", type(raw).__name__)
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
    logger.debug("[advisor] _normalize_missing_quarters → %s entrée(s) valide(s)", len(out))
    return out


def _normalize_checklist(raw: Any) -> list[dict[str, str]]:
    logger.debug(
        "[advisor] _normalize_checklist | type=%s | len=%s",
        type(raw).__name__,
        len(raw) if isinstance(raw, list) else "n/a",
    )
    if not isinstance(raw, list):
        logger.warning("[advisor] checklist: attendu une list, reçu %s", type(raw).__name__)
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
    logger.debug("[advisor] _normalize_checklist → %s entrée(s)", len(out))
    return out


def detect_missing_quarters(profile: dict, retrieval_context: str = "") -> list[dict[str, str]]:
    """
    Analyse le profil carrière (France, régime général simplifié) et identifie des périodes
    pouvant générer des trimestres souvent oubliés ou mal déclarés (enfants, chômage, arrêts longs, etc.).

    Si retrieval_context est non vide, il contient des extraits open data (CNAV / data.gouv) : t'en
    servir uniquement comme contexte statistique national, pas comme dossier individuel.

    Retour : liste de dicts avec clés period, reason, action — français simple.
    """
    logger.info(
        "[advisor] detect_missing_quarters | clés profil=%s | contexte_open_data=%s caractères",
        list(profile.keys()),
        len(retrieval_context or ""),
    )
    _ = (profile, retrieval_context)  # fourni au modèle via inspection OpenHosta
    try:
        logger.debug("[advisor] detect_missing_quarters → appel emulate()")
        raw = emulate()
        logger.debug("[advisor] detect_missing_quarters ← emulate() type=%s", type(raw).__name__)
        normalized = _normalize_missing_quarters(raw)
        logger.info("[advisor] detect_missing_quarters | résultat final: %s item(s)", len(normalized))
        return normalized
    except Exception as exc:  # noqa: BLE001 — fallback hackathon
        logger.exception("[advisor] detect_missing_quarters | échec emulate → liste vide")
        return []


def generate_checklist(
    profile: dict,
    missing_quarters: list[dict[str, str]],
    retrieval_context: str = "",
) -> list[dict[str, str]]:
    """
    Produit 5 à 10 étapes concrètes, ordonnées, en français simple, avec liens d’administration
    quand ils sont connus.

    retrieval_context : statistiques officielles agrégées (open data) — citer avec prudence,
    ne pas en déduire un montant de pension personnel.
    """
    logger.info(
        "[advisor] generate_checklist | missing_quarters en entrée=%s | clés profil=%s | "
        "contexte_open_data=%s caractères",
        len(missing_quarters),
        list(profile.keys()),
        len(retrieval_context or ""),
    )
    _ = (profile, missing_quarters, retrieval_context)
    try:
        logger.debug("[advisor] generate_checklist → appel emulate()")
        raw = emulate()
        logger.debug("[advisor] generate_checklist ← emulate() type=%s", type(raw).__name__)
        normalized = _normalize_checklist(raw)
        if not normalized:
            logger.warning(
                "[advisor] generate_checklist | normalisation vide → FALLBACK_CHECKLIST (%s étapes)",
                len(FALLBACK_CHECKLIST),
            )
            return list(FALLBACK_CHECKLIST)
        logger.info("[advisor] generate_checklist | résultat final: %s étape(s)", len(normalized))
        return normalized
    except Exception:  # noqa: BLE001
        logger.exception("[advisor] generate_checklist | échec emulate → FALLBACK")
        return list(FALLBACK_CHECKLIST)


def synthesize_report_markdown(
    document_seed_markdown: str,
    retrieval_context: str = "",
) -> str:
    """
    À partir du bloc « données factuelles » (markdown), rédige un document markdown complet
    (titres ##, listes, ton pédagogique, français simple). Ne pas inventer de montants ni de dates
    qui ne figurent pas dans le bloc ni dans retrieval_context.

    retrieval_context : statistiques agrégées open data — contexte national uniquement.
    """
    logger.info(
        "[advisor] synthesize_report_markdown | seed=%s caractères | open_data=%s caractères",
        len(document_seed_markdown or ""),
        len(retrieval_context or ""),
    )
    _ = (document_seed_markdown, retrieval_context)
    try:
        logger.debug("[advisor] synthesize_report_markdown → appel emulate()")
        raw = emulate()
        text = str(raw).strip() if raw is not None else ""
        if not text:
            logger.warning("[advisor] synthesize_report_markdown | réponse vide")
            return ""
        logger.info("[advisor] synthesize_report_markdown | OK | longueur=%s", len(text))
        return text
    except Exception:  # noqa: BLE001
        logger.exception("[advisor] synthesize_report_markdown | échec emulate → chaîne vide")
        return ""


def explain_term(term: str) -> str:
    """
    Explique un terme de retraite en français très simple, max 3 phrases, sans jargon,
    pour une personne de 65 ans sans formation juridique.
    """
    logger.info("[advisor] explain_term | terme=%r", term)
    _ = term
    try:
        logger.debug("[advisor] explain_term → appel emulate()")
        raw = emulate()
        logger.debug("[advisor] explain_term ← emulate() type=%s", type(raw).__name__)
        text = str(raw).strip() if raw is not None else ""
        if not text:
            logger.warning("[advisor] explain_term | réponse vide → fallback générique")
            return _glossary_fallback(term)
        logger.info("[advisor] explain_term | OK | longueur=%s", len(text))
        return text
    except Exception as exc:  # noqa: BLE001
        logger.exception("[advisor] explain_term | échec emulate → fallback")
        return _glossary_fallback(term)
