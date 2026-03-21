"""
Assemblage document : placeholders type [CLE], listes markdown, document complet.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


def new_dossier_id() -> str:
    return str(uuid4())


def today_iso() -> str:
    return date.today().isoformat()


def format_missing_periods_plain(missing_quarters: list[dict[str, str]]) -> str:
    """Forme courte pour champs de fusion type [LISTE_PERIODES_MANQUANTES]."""
    parts = [(m.get("period") or "").strip() for m in missing_quarters]
    parts = [p for p in parts if p]
    if not parts:
        return "Aucune période signalée par l’analyse automatique"
    return ", ".join(parts)


def format_missing_periods_markdown(missing_quarters: list[dict[str, str]]) -> str:
    """Liste les périodes à risque / à vérifier (issues de l’IA ou vide)."""
    if not missing_quarters:
        return "_Aucune période signalée par l’analyse automatique — vérifier tout de même le relevé de carrière._"
    lines: list[str] = []
    for m in missing_quarters:
        period = (m.get("period") or "").strip()
        reason = (m.get("reason") or "").strip()
        action = (m.get("action") or "").strip()
        chunk = period
        if reason:
            chunk += f" — _{reason}_"
        if action:
            chunk += f" → {action}"
        if chunk.strip():
            lines.append(f"- {chunk}")
    return "\n".join(lines) if lines else "_Aucune période exploitable._"


def format_checklist_summary_for_seed(checklist: list[dict[str, str]]) -> str:
    """Résumé titres seulement pour le seed LLM — évite de dupliquer tout le markdown des liens dans la synthèse."""
    if not checklist:
        return "_(Aucune étape listée par l’analyse — consulter les recommandations officielles.)_"
    lines: list[str] = []
    for i, c in enumerate(checklist, start=1):
        title = (c.get("title") or "").strip()
        if title:
            lines.append(f"{i}. {title}")
    return "\n".join(lines) if lines else "_(Titres d’étapes indisponibles.)_"


_PHASE_GUIDE_LABEL: dict[str, str] = {
    "recap": "Récapitulatif",
    "point_a_clarifier": "Point à clarifier",
    "prochaine_etape": "Prochaine étape",
}


def format_guided_journey_markdown(steps: list[dict[str, Any]]) -> str:
    """Parcours « questions → suite » pour affichage ou PDF (vide si aucune étape)."""
    if not steps:
        return ""
    lines: list[str] = ["## Parcours guidé\n", "_À suivre dans l’ordre ; chaque bloc est volontairement court._\n"]
    for s in steps:
        step_n = s.get("step", "")
        phase = str(s.get("phase", "")).strip()
        label = _PHASE_GUIDE_LABEL.get(phase, phase or "Étape")
        title = (s.get("title") or "").strip()
        content = (s.get("content") or "").strip()
        op = (s.get("optional_prompt") or "").strip()
        head = f"### Étape {step_n}"
        if title:
            head += f" — {title}"
        lines.append(head)
        lines.append(f"*{label}*\n")
        if content:
            lines.append(content + "\n")
        if op:
            lines.append(f"> _Pour la suite de l’échange : {op}_\n")
    return "\n".join(lines)


def format_checklist_markdown(checklist: list[dict[str, str]]) -> str:
    parts: list[str] = ["## Étapes recommandées\n"]
    for i, c in enumerate(checklist, start=1):
        title = (c.get("title") or "").strip()
        detail = (c.get("detail") or "").strip()
        url = (c.get("url") or "").strip()
        line = f"{i}. **{title}**"
        if detail:
            line += f"\n   - {detail}"
        if url:
            line += f"\n   - Lien : <{url}>"
        parts.append(line)
    return "\n\n".join(parts)





def build_document_seed_markdown(
    *,
    profile: dict[str, Any],
    age_legal: int,
    age_taux_plein: int,
    trimestres_ok: int,
    trimestres_requis: int,
    trimestres_restants: int,
    montant_estime: int | None,
    liste_periodes_md: str,
    checklist_summary: str,
) -> str:
    """Contenu structuré minimal passé au LLM pour générer la synthèse (pas d’invention de chiffres)."""
    lines = [
        "# Données factuelles Personnelles",
        f"- Année de naissance : {profile.get('birth_year')}",
        f"- Tranche d'âge de début de carrière : {profile.get('career_start_age')}",
        f"- Statuts professionnels : {', '.join(profile.get('professional_statuses', []))}",
        f"- Âge légal de départ (modèle simplifié) : {age_legal} ans",
        f"- Âge de taux plein sans décote liée à l’âge (modèle simplifié) : {age_taux_plein} ans",
        f"- Trimestres estimés (relevé à confirmer) : {trimestres_ok}",
        f"- Trimestres requis (référence produit) : {trimestres_requis}",
        f"- Trimestres restants à acquérir : {trimestres_restants}",
        f"- Montant estimé déclaré : {montant_estime if montant_estime is not None else 'non fourni'}",
        "",
        "# Données factuelles Projet PER (Valeurs exactes saisies par le client pour le contrat)",
        f"- Organisme gestionnaire souhaité : {profile.get('per_organisme') or 'À déterminer'}",
        f"- Versement mensuel prévu : {profile.get('per_versement_mensuel') or 'À déterminer'} €",
        f"- Versement ponctuel prévu : {profile.get('per_versement_ponctuel') or 'À déterminer'} €",
        f"- Type de gestion : {profile.get('per_gestion_type', 'a_definir')}",
        f"- Forme de sortie envisagée : {profile.get('per_forme_sortie', 'a_definir')}",
        f"- Option fiscale choisie : {profile.get('per_option_fiscale', 'a_decider')}",
        f"- Présence d'un plan PER entreprise : {profile.get('per_plan_entreprise', 'je_ne_sais_pas')}",
        f"- Anciens contrats à transférer : {profile.get('per_anciens_contrats', 'je_ne_sais_pas')}",
        "",
        "## Périodes à creuser",
        liste_periodes_md,
        "",
        "## Étapes recommandées (titres uniquement — ne pas recopier les liens ici, ils figurent ailleurs)",
        checklist_summary,
    ]
    return "\n".join(lines)


def build_fallback_synthese_markdown(
    *,
    nom_utilisateur: str,
    id_dossier: str,
    ville_signature: str,
    date_signature: str,
    age_legal: int,
    age_taux_plein: int,
    trimestres_ok: int,
    trimestres_requis: int,
    trimestres_restants: int,
    montant_line: str,
    liste_periodes_md: str,
) -> str:
    return "\n".join(
        [
            f"# Synthèse retraite — dossier `{id_dossier}`",
            "",
            f"**{nom_utilisateur}**, à **{ville_signature}**, le **{date_signature}**.",
            "",
            "## Chiffres clés (indicatifs, modèle simplifié)",
            f"- **Âge légal de départ** : {age_legal} ans",
            f"- **Âge de référence taux plein (âge)** : {age_taux_plein} ans — *à croiser avec votre durée d’assurance et les règles en vigueur*",
            f"- **Trimestres estimés** : {trimestres_ok} (à confirmer sur relevé officiel)",
            f"- **Trimestres requis (référence)** : {trimestres_requis}",
            f"- **Trimestres restants** : {trimestres_restants}",
            f"- **Montant estimé** : {montant_line}",
            "",
            "## Périodes à vérifier",
            liste_periodes_md,
            "",
            "> _Document généré automatiquement. Pour toute décision, utilisez les simulateurs et caisses officiels._",
        ]
    )


def format_special_cases_markdown(
    *,
    nb_enfants: int | None,
    nb_mois_armee: int | None,
    nb_trimestres_avant_20: int | None,
    pays_etranger: str,
    had_children: bool,
    had_military_service: bool,
) -> str:
    """Bloc markdown « cas particuliers » pour le document complet (cohérent avec nombres vs cases)."""
    lines = ["## Cas particuliers (formulaire / indicateurs)\n"]

    if nb_enfants is not None and nb_enfants > 0:
        lines.append(f"- **Nombre d’enfants** : {nb_enfants} _(renseigné)_")
    elif had_children:
        lines.append("- **Nombre d’enfants** : non précisé _(case famille : oui)_")
    else:
        lines.append("- **Nombre d’enfants** : non renseigné _(case famille : non)_")

    if nb_mois_armee is not None and nb_mois_armee > 0:
        lines.append(f"- **Mois de service militaire** : {nb_mois_armee} _(durée renseignée)_")
    elif had_military_service:
        lines.append("- **Mois de service militaire** : non précisé _(case militaire : oui)_")
    else:
        lines.append("- **Mois de service militaire** : non renseigné _(case militaire : non)_")
    lines.append(
        f"- **Trimestres cotisés avant 20 ans** : "
        f"{nb_trimestres_avant_20 if nb_trimestres_avant_20 is not None else 'non renseigné'}"
    )
    lines.append(
        f"- **Pays étrangers (carrière)** : {pays_etranger.strip() or '_Non renseigné_'}"
    )
    return "\n".join(lines)


def assemble_document_complet(
    synthese: str,
    checklist_md: str,
    cas_particuliers_md: str,
    parcours_guide_md: str = "",
) -> str:
    parts = [synthese.rstrip()]
    if parcours_guide_md.strip():
        parts.extend(["", "---", "", parcours_guide_md.rstrip()])
    parts.extend(["", "---", "", checklist_md.rstrip()])
    if cas_particuliers_md.strip():
        parts.extend(["", "---", "", cas_particuliers_md.rstrip()])
    return "\n".join(parts)
