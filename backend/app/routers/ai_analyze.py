"""Étape 2 du pipeline : appels LLM (périodes manquantes, checklist, parcours, synthèse)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from ai.advisor import (
    detect_missing_quarters,
    generate_checklist,
    generate_guided_journey,
    synthesize_report_markdown,
)
from app.converters import tools_summary_text
from app.schemas import (
    AiAnalyzeRequest,
    AnalyzeReportResponse,
    AnalyzeResponse,
    ChecklistItem,
    EnrichmentSection,
    GuidedJourneyStep,
    IdentitySection,
    KeyFiguresSection,
    MarkdownSections,
    MissingQuarterItem,
    SpecialCasesSection,
)
from core.calculator import TRIMESTRES_REQUIS_TAUX_PLEIN
from core.report_document import (
    assemble_document_complet,
    build_document_seed_markdown,
    build_fallback_synthese_markdown,
    format_checklist_markdown,
    format_checklist_summary_for_seed,
    format_guided_journey_markdown,
    format_missing_periods_markdown,
    format_missing_periods_plain,
    format_special_cases_markdown,
    new_dossier_id,
    today_iso,
)

router = APIRouter(tags=["ai-analyze"])
log = logging.getLogger(__name__)





def run_ai_analyze(body: AiAnalyzeRequest) -> AnalyzeReportResponse:
    """Exécute la phase LLM + assemblage rapport — réutilisable en interne."""
    c = body.compute
    profile_dict = c.profile
    ctx = c.enrichment.context_block

    # ---- LLM calls ----
    missing_raw = detect_missing_quarters(profile_dict, retrieval_context=ctx)
    checklist_raw = generate_checklist(profile_dict, missing_raw, retrieval_context=ctx)

    tools_summary = tools_summary_text(c.enrichment)
    journey_raw = generate_guided_journey(
        profile_dict,
        missing_raw,
        checklist_raw,
        retrieval_context=ctx,
        tools_summary=tools_summary,
    )

    # ---- Identité ----
    nom = (body.full_name or "").strip() or "Non renseigné"
    ville = (body.ville_signature or "").strip() or "Non renseignée"
    dossier_id = new_dossier_id()
    date_sig = today_iso()
    montant = body.montant_estime_euros

    # ---- Markdown ----
    liste_plain = format_missing_periods_plain(missing_raw)
    liste_md = format_missing_periods_markdown(missing_raw)
    checklist_md = format_checklist_markdown(checklist_raw)
    checklist_seed = format_checklist_summary_for_seed(checklist_raw)
    cas_md = format_special_cases_markdown(
        nb_enfants=body.nb_enfants,
        nb_mois_armee=body.nb_mois_armee,
        nb_trimestres_avant_20=body.nb_trimestres_avant_20,
        pays_etranger=body.pays_etranger,
        had_children=body.nb_enfants is not None and body.nb_enfants > 0,
        had_military_service=body.nb_mois_armee is not None and body.nb_mois_armee > 0,
    )

    seed = build_document_seed_markdown(
        profile=profile_dict,
        age_legal=c.departure_age,
        age_taux_plein=c.age_taux_plein_auto,
        trimestres_ok=c.quarters_worked,
        trimestres_requis=TRIMESTRES_REQUIS_TAUX_PLEIN,
        trimestres_restants=c.quarters_remaining,
        montant_estime=montant,
        liste_periodes_md=liste_md,
        checklist_summary=checklist_seed,
    )

    synthese = synthesize_report_markdown(seed, retrieval_context=ctx)
    montant_line = (
        f"{montant} € / mois (déclaratif utilisateur)"
        if montant is not None
        else "Non renseigné — simulation officielle recommandée (ex. info-retraite.fr)."
    )
    if len(synthese.strip()) < 80:
        synthese = build_fallback_synthese_markdown(
            nom_utilisateur=nom,
            id_dossier=dossier_id,
            ville_signature=ville,
            date_signature=date_sig,
            age_legal=c.departure_age,
            age_taux_plein=c.age_taux_plein_auto,
            trimestres_ok=c.quarters_worked,
            trimestres_requis=TRIMESTRES_REQUIS_TAUX_PLEIN,
            trimestres_restants=c.quarters_remaining,
            montant_line=montant_line,
            liste_periodes_md=liste_md,
        )

    parcours_md = format_guided_journey_markdown(journey_raw)
    document_complet = assemble_document_complet(synthese, checklist_md, cas_md, parcours_md)

    # ---- Réponse structurée ----
    core = AnalyzeResponse(
        departure_age=c.departure_age,
        quarters_worked=c.quarters_worked,
        quarters_remaining=c.quarters_remaining,
        missing_quarters=[MissingQuarterItem(**m) for m in missing_raw],
        checklist=[ChecklistItem(**ck) for ck in checklist_raw],
        guided_journey=[GuidedJourneyStep(**j) for j in journey_raw],
        enrichment=c.enrichment,
    )

    return AnalyzeReportResponse(
        enrichment=c.enrichment,
        identity=IdentitySection(
            nom_utilisateur=nom,
            id_dossier=dossier_id,
            ville_signature=ville,
            date_signature=date_sig,
        ),
        key_figures=KeyFiguresSection(
            age_legal=c.departure_age,
            age_taux_plein_auto=c.age_taux_plein_auto,
            trimestres_ok=c.quarters_worked,
            trimestres_requis=TRIMESTRES_REQUIS_TAUX_PLEIN,
            trimestres_restants=c.quarters_remaining,
            montant_estime=montant,
        ),
        special_cases=SpecialCasesSection(
            nb_enfants=body.nb_enfants,
            nb_mois_armee=body.nb_mois_armee,
            nb_trimestres_avant_20=body.nb_trimestres_avant_20,
            pays_etranger=body.pays_etranger.strip(),
            liste_periodes_manquantes=liste_plain,
        ),
        markdown=MarkdownSections(
            synthese=synthese,
            checklist=checklist_md,
            cas_particuliers=cas_md,
            parcours_guide=parcours_md,
            document_complet=document_complet,
        ),
        analyze=core,
    )


@router.post("/ai/analyze", response_model=AnalyzeReportResponse)
def post_ai_analyze(body: AiAnalyzeRequest) -> AnalyzeReportResponse:
    """Étape 2 : appels LLM (périodes, checklist, parcours) + synthèse markdown."""
    log.info("[ai_analyze] POST /ai/analyze — phase LLM")
    return run_ai_analyze(body)
