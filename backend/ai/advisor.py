"""
Couche LLM unique RetroAide : droits oubliés, checklist, glossaire (OpenHosta emulate).

Chaque fonction publique délègue à ``_safe_emulate`` qui centralise le try/except,
la normalisation et le fallback — évite la duplication de blocs identiques.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar

from ai import config as _ai_env  # noqa: F401 — charge .env avant OpenHosta
from ai import guidance as _guidance

from OpenHosta import emulate

logger = logging.getLogger(__name__)

T = TypeVar("T")

FALLBACK_CHECKLIST: list[dict[str, str]] = [
    {
        "title": "Contrôler votre relevé de carrière",
        "detail": "Demandez vos relevés à la CNAV et à l'Agirc-Arrco (ou caisse équivalente) pour vérifier vos trimestres.",
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


# ---------------------------------------------------------------------------
# Helpers internes
# ---------------------------------------------------------------------------

def _s(d: dict, key: str) -> str:
    """Extraction sûre d'une valeur texte depuis un dict (strip + coerce str)."""
    return str(d.get(key) or "").strip()


def _safe_emulate(
    *,
    label: str,
    guidance_args: tuple,
    normalizer: Callable[[Any], T],
    fallback: T | Callable[[], T],
    allow_empty: bool = False,
) -> T:
    """Appelle ``emulate()``, normalise le résultat et retourne un fallback en cas d'échec.

    Centralise le pattern try/except + normalisation + fallback utilisé
    par toutes les fonctions LLM de ce module.

    Parameters
    ----------
    label:
        Nom court pour les logs (ex. ``"detect_missing_quarters"``).
    guidance_args:
        Tuple de variables référencées dans le corps de la fonction appelante
        (profil, guidance, etc.) — passé ici uniquement pour que ``emulate()``
        les voie dans le scope d'appel.
    normalizer:
        Fonction de post-traitement du résultat brut.
    fallback:
        Valeur ou callable à utiliser si normalisation vide ou exception.
    allow_empty:
        Si ``True``, un résultat vide après normalisation est accepté
        (utilisé pour la synthèse markdown qui peut légitimement être vide).
    """
    _ = guidance_args  # noqa: F841 — référencé pour emulate()
    try:
        raw = emulate()
        result = normalizer(raw)
        if not result and not allow_empty:
            fb = fallback() if callable(fallback) else fallback
            logger.warning("[advisor] %s | résultat vide → fallback", label)
            return fb
        logger.info("[advisor] %s | OK", label)
        return result
    except Exception:  # noqa: BLE001
        logger.exception("[advisor] %s | échec emulate → fallback", label)
        return fallback() if callable(fallback) else fallback


def _glossary_fallback(term: str) -> str:
    return (
        f"« {term} » est un mot employé par l'assurance retraite. "
        "Pour une explication précise adaptée à votre dossier, contactez votre caisse de retraite "
        "ou consultez les fiches sur info-retraite.fr."
    )


# ---------------------------------------------------------------------------
# Normalisation des réponses LLM
# ---------------------------------------------------------------------------

def _normalize_missing_quarters(raw: Any) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        logger.warning("[advisor] missing_quarters: attendu list, reçu %s", type(raw).__name__)
        return []
    out: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        row = {k: _s(item, k) for k in ("period", "reason", "action")}
        if not any(row.values()):
            continue
        out.append(row)
    return out


def _normalize_checklist(raw: Any) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        logger.warning("[advisor] checklist: attendu list, reçu %s", type(raw).__name__)
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
            out.append({
                "title": title,
                "detail": str(item.get("detail", item.get("description", ""))).strip(),
                "url": str(item.get("url", item.get("link", ""))).strip(),
            })
    return out


def _normalize_guided_journey(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        logger.warning("[advisor] guided_journey: attendu list, reçu %s", type(raw).__name__)
        return []
    phases_ok = frozenset({"recap", "point_a_clarifier", "prochaine_etape"})
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            step_n = int(item.get("step", 0))
        except (TypeError, ValueError):
            continue
        if step_n < 1 or step_n > 15:
            continue
        phase = _s(item, "phase")
        if phase not in phases_ok:
            continue
        title = _s(item, "title")
        content = _s(item, "content")
        if not title and not content:
            continue
        out.append({
            "step": step_n,
            "phase": phase,
            "title": title,
            "content": content,
            "optional_prompt": _s(item, "optional_prompt"),
        })
    out.sort(key=lambda x: x["step"])
    return out


def _normalize_text(raw: Any) -> str:
    """Normalisation simple pour les fonctions qui retournent du texte brut."""
    return str(raw).strip() if raw is not None else ""


def _fallback_guided_journey(
    profile: dict,
    missing_quarters: list[dict[str, str]],
    checklist: list[dict[str, str]],
) -> list[dict[str, Any]]:
    by = profile.get("birth_year", "?")
    cs = profile.get("career_start_year", "?")
    steps: list[dict[str, Any]] = [
        {
            "step": 1,
            "phase": "recap",
            "title": "Ce que nous avons retenu de votre formulaire",
            "content": (
                f"Vous avez indiqué être né(e) en {by} et avoir commencé à travailler en {cs}. "
                "Ces repères servent à orienter la suite : ils devront être vérifiés sur vos relevés officiels."
            ),
            "optional_prompt": "Y a-t-il une période de votre carrière que vous souhaitez mentionner en premier ?",
        },
        {
            "step": 2,
            "phase": "point_a_clarifier",
            "title": "Points à confirmer avec votre caisse",
            "content": (
                "Les trimestres et montants ne peuvent être figés qu'après consultation de votre relevé de carrière "
                "et des simulateurs agréés (info-retraite, Assurance Retraite)."
            ),
            "optional_prompt": "",
        },
    ]
    n = 3
    if missing_quarters:
        first = (_s(missing_quarters[0], "period") or "certaines périodes")
        steps.append({
            "step": n,
            "phase": "prochaine_etape",
            "title": "Creuser une période à risque",
            "content": (
                f"L'analyse signale notamment : {first}. "
                "Vous pouvez rassembler bulletins de paie ou attestations pour en discuter avec un conseiller."
            ),
            "optional_prompt": "Souhaitez-vous de l'aide pour préparer cette démarche ?",
        })
        n += 1
    for c in checklist[:3]:
        t = _s(c, "title")
        if not t:
            continue
        steps.append({
            "step": n,
            "phase": "prochaine_etape",
            "title": t,
            "content": (_s(c, "detail") or "Voir le détail dans la checklist ci-dessous."),
            "optional_prompt": "",
        })
        n += 1
        if n > 8:
            break
    return steps


# ---------------------------------------------------------------------------
# Fonctions publiques (API LLM)
# ---------------------------------------------------------------------------

def detect_missing_quarters(profile: dict, retrieval_context: str = "") -> list[dict[str, str]]:
    """
    Identifie des périodes où des trimestres sont souvent oubliés ou mal déclarés.

    Retour : liste de dicts ``{period, reason, action}`` en français simple.
    """
    logger.info("[advisor] detect_missing_quarters | profil=%s clés | ctx=%s car.",
                len(profile), len(retrieval_context or ""))
    return _safe_emulate(
        label="detect_missing_quarters",
        guidance_args=(
            profile, retrieval_context,
            _guidance.SENIOR_AUDIENCE, _guidance.CONSEIL_RETRAITE_CADRE,
            _guidance.OPEN_DATA_ET_APIS, _guidance.FORMAT_SORTIE_MANQUANTS,
        ),
        normalizer=_normalize_missing_quarters,
        fallback=[],
    )


def generate_checklist(
    profile: dict,
    missing_quarters: list[dict[str, str]],
    retrieval_context: str = "",
) -> list[dict[str, str]]:
    """
    Checklist de 5 à 10 étapes pour sécuriser le parcours retraite.

    Retour : liste de ``{title, detail, url}``.
    """
    logger.info("[advisor] generate_checklist | missing=%s | profil=%s clés | ctx=%s car.",
                len(missing_quarters), len(profile), len(retrieval_context or ""))
    return _safe_emulate(
        label="generate_checklist",
        guidance_args=(
            profile, missing_quarters, retrieval_context,
            _guidance.SENIOR_AUDIENCE, _guidance.CONSEIL_RETRAITE_CADRE,
            _guidance.OPEN_DATA_ET_APIS, _guidance.FORMAT_SORTIE_CHECKLIST,
        ),
        normalizer=_normalize_checklist,
        fallback=lambda: list(FALLBACK_CHECKLIST),
    )


def generate_guided_journey(
    profile: dict,
    missing_quarters: list[dict[str, str]],
    checklist: list[dict[str, str]],
    retrieval_context: str = "",
    tools_summary: str = "",
) -> list[dict[str, Any]]:
    """
    Parcours étape par étape : récap → points à clarifier → démarches concrètes.
    """
    logger.info("[advisor] generate_guided_journey | missing=%s | checklist=%s | ctx=%s car.",
                len(missing_quarters), len(checklist), len(retrieval_context or ""))
    return _safe_emulate(
        label="generate_guided_journey",
        guidance_args=(
            profile, missing_quarters, checklist, retrieval_context, tools_summary,
            _guidance.SENIOR_AUDIENCE, _guidance.CONSEIL_RETRAITE_CADRE,
            _guidance.OPEN_DATA_ET_APIS, _guidance.FORMAT_PARCOURS_GUIDE,
        ),
        normalizer=_normalize_guided_journey,
        fallback=lambda: _fallback_guided_journey(profile, missing_quarters, checklist),
    )


def synthesize_report_markdown(
    document_seed_markdown: str,
    retrieval_context: str = "",
) -> str:
    """
    Synthèse markdown lisible pour un senior, à partir du seed et du retrieval_context.
    """
    logger.info("[advisor] synthesize_report_markdown | seed=%s car. | ctx=%s car.",
                len(document_seed_markdown or ""), len(retrieval_context or ""))
    return _safe_emulate(
        label="synthesize_report_markdown",
        guidance_args=(
            document_seed_markdown, retrieval_context,
            _guidance.SENIOR_AUDIENCE, _guidance.CONSEIL_RETRAITE_CADRE,
            _guidance.OPEN_DATA_ET_APIS, _guidance.FORMAT_SYNTHESE_MARKDOWN,
        ),
        normalizer=_normalize_text,
        fallback="",
        allow_empty=True,
    )


def explain_term(term: str) -> str:
    """
    Explication d'un terme retraite comme à un proche de 70 ans (max 3 phrases).
    """
    logger.info("[advisor] explain_term | terme=%r", term)
    return _safe_emulate(
        label="explain_term",
        guidance_args=(
            term,
            _guidance.SENIOR_AUDIENCE, _guidance.FORMAT_GLOSSAIRE,
        ),
        normalizer=_normalize_text,
        fallback=lambda: _glossary_fallback(term),
    )
