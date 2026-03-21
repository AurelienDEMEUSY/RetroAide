"""Endpoint analyse : métriques déterministes + OpenHosta (advisor)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import APIRouter

from ai.advisor import (
    detect_missing_quarters,
    generate_checklist,
    synthesize_report_markdown,
)
from app.schemas import (
    AnalyzeReportResponse,
    AnalyzeResponse,
    ChecklistItem,
    EnrichmentSection,
    EnrichmentTraceItem,
    IdentitySection,
    KeyFiguresSection,
    MarkdownSections,
    MissingQuarterItem,
    SpecialCasesSection,
    UserProfile,
)
from core.calculator import (
    TRIMESTRES_REQUIS_TAUX_PLEIN,
    calculate_departure_age,
    estimate_quarters_worked,
    quarters_remaining,
    statutory_full_rate_age,
)
from core.report_document import (
    assemble_document_complet,
    build_document_seed_markdown,
    build_fallback_synthese_markdown,
    format_checklist_markdown,
    format_checklist_summary_for_seed,
    format_missing_periods_markdown,
    format_missing_periods_plain,
    format_special_cases_markdown,
    new_dossier_id,
    today_iso,
)
from tools.mcp_pipeline import EnrichmentResult, run_enrichment

router = APIRouter(tags=["analyze"])
log = logging.getLogger(__name__)


@dataclass(frozen=True)
class _AnalyzeRun:
    profile_dict: dict
    departure_age: int
    age_taux_plein_auto: int
    quarters_worked: int
    quarters_remaining: int
    enrichment: EnrichmentResult
    missing_raw: list[dict[str, str]]
    checklist_raw: list[dict[str, str]]

    @property
    def ctx_block(self) -> str:
        return self.enrichment.context_block


def _run_analyze_pipeline(body: UserProfile) -> _AnalyzeRun:
    profile_dict = body.model_dump()
    log.debug(
        "[analyze] profil reçu (aperçu non exhaustif): birth_year=%s career_start=%s status=%s "
        "employed=%s flags={children:%s chômage:%s arrêt_long:%s militaire:%s temps_partiel:%s}",
        body.birth_year,
        body.career_start_year,
        body.status,
        body.currently_employed,
        body.had_children,
        body.had_unemployment,
        body.had_long_sick_leave,
        body.had_military_service,
        body.long_part_time_years,
    )

    log.debug("[analyze] étape calculator: calculate_departure_age(%s)", body.birth_year)
    departure_age = calculate_departure_age(body.birth_year)
    log.debug("[analyze] → departure_age=%s", departure_age)

    age_taux = statutory_full_rate_age(body.birth_year)

    log.debug("[analyze] étape calculator: estimate_quarters_worked(%s)", body.career_start_year)
    quarters_worked = estimate_quarters_worked(body.career_start_year)
    log.debug("[analyze] → quarters_worked=%s", quarters_worked)

    log.debug("[analyze] étape calculator: quarters_remaining(%s)", quarters_worked)
    q_remaining = quarters_remaining(
        quarters_worked,
        trimestres_requis=TRIMESTRES_REQUIS_TAUX_PLEIN,
    )
    log.debug("[analyze] → quarters_remaining=%s", q_remaining)

    log.info("[analyze] enrichissement (pipeline MCP équivalent — APIs externes)")
    enrichment = run_enrichment(profile_dict)
    log.info(
        "[analyze] enrichissement | sources=%s | longueur_bloc=%s | outils=%s",
        enrichment.sources_touched,
        len(enrichment.context_block),
        [t.tool for t in enrichment.tools],
    )

    log.info("[analyze] appel OpenHosta detect_missing_quarters")
    missing_raw = detect_missing_quarters(profile_dict, retrieval_context=enrichment.context_block)
    log.info("[analyze] detect_missing_quarters terminé | %s entrée(s)", len(missing_raw))

    log.info("[analyze] appel OpenHosta generate_checklist")
    checklist_raw = generate_checklist(profile_dict, missing_raw, retrieval_context=enrichment.context_block)
    log.info("[analyze] generate_checklist terminé | %s entrée(s)", len(checklist_raw))

    return _AnalyzeRun(
        profile_dict=profile_dict,
        departure_age=departure_age,
        age_taux_plein_auto=age_taux,
        quarters_worked=quarters_worked,
        quarters_remaining=q_remaining,
        enrichment=enrichment,
        missing_raw=missing_raw,
        checklist_raw=checklist_raw,
    )


def _enrichment_to_section(er: EnrichmentResult) -> EnrichmentSection:
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


def _analyze_response_from_run(run: _AnalyzeRun) -> AnalyzeResponse:
    return AnalyzeResponse(
        departure_age=run.departure_age,
        quarters_worked=run.quarters_worked,
        quarters_remaining=run.quarters_remaining,
        missing_quarters=[MissingQuarterItem(**m) for m in run.missing_raw],
        checklist=[ChecklistItem(**c) for c in run.checklist_raw],
        enrichment=_enrichment_to_section(run.enrichment),
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def post_analyze(body: UserProfile) -> AnalyzeResponse:
    log.info("[analyze] début traitement POST /analyze")
    run = _run_analyze_pipeline(body)
    log.info(
        "[analyze] réponse construite | departure_age=%s quarters_worked=%s quarters_remaining=%s "
        "checklist_items=%s missing_quarters_items=%s",
        run.departure_age,
        run.quarters_worked,
        run.quarters_remaining,
        len(run.checklist_raw),
        len(run.missing_raw),
    )
    return _analyze_response_from_run(run)


@router.post("/analyze/report", response_model=AnalyzeReportResponse)
def post_analyze_report(body: UserProfile) -> AnalyzeReportResponse:
    """
    Même pipeline que `/analyze`, plus un paquet JSON pour export PDF / MDX :
    identité, chiffres clés, cas particuliers (source unique), blocs markdown (synthèse LLM + repli).
    """
    log.info("[analyze] début traitement POST /analyze/report")
    run = _run_analyze_pipeline(body)

    nom = (body.full_name or "").strip() or "Non renseigné"
    ville = (body.ville_signature or "").strip() or "Non renseignée"
    dossier_id = new_dossier_id()
    date_sig = today_iso()
    montant = body.montant_estime_euros

    liste_plain = format_missing_periods_plain(run.missing_raw)
    liste_md = format_missing_periods_markdown(run.missing_raw)
    checklist_md = format_checklist_markdown(run.checklist_raw)
    checklist_seed = format_checklist_summary_for_seed(run.checklist_raw)
    cas_md = format_special_cases_markdown(
        nb_enfants=body.nb_enfants,
        nb_mois_armee=body.nb_mois_armee,
        nb_trimestres_avant_20=body.nb_trimestres_avant_20,
        pays_etranger=body.pays_etranger,
        had_children=body.had_children,
        had_military_service=body.had_military_service,
    )

    seed = build_document_seed_markdown(
        profile=run.profile_dict,
        age_legal=run.departure_age,
        age_taux_plein=run.age_taux_plein_auto,
        trimestres_ok=run.quarters_worked,
        trimestres_requis=TRIMESTRES_REQUIS_TAUX_PLEIN,
        trimestres_restants=run.quarters_remaining,
        montant_estime=montant,
        liste_periodes_md=liste_md,
        checklist_summary=checklist_seed,
    )

    synthese = synthesize_report_markdown(seed, retrieval_context=run.ctx_block)
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
            age_legal=run.departure_age,
            age_taux_plein=run.age_taux_plein_auto,
            trimestres_ok=run.quarters_worked,
            trimestres_requis=TRIMESTRES_REQUIS_TAUX_PLEIN,
            trimestres_restants=run.quarters_remaining,
            montant_line=montant_line,
            liste_periodes_md=liste_md,
        )

    document_complet = assemble_document_complet(synthese, checklist_md, cas_md)

    core = _analyze_response_from_run(run)

    log.info(
        "[analyze] rapport construit | dossier=%s | document_complet=%s caractères",
        dossier_id,
        len(document_complet),
    )

    return AnalyzeReportResponse(
        enrichment=_enrichment_to_section(run.enrichment),
        identity=IdentitySection(
            nom_utilisateur=nom,
            id_dossier=dossier_id,
            ville_signature=ville,
            date_signature=date_sig,
        ),
        key_figures=KeyFiguresSection(
            age_legal=run.departure_age,
            age_taux_plein_auto=run.age_taux_plein_auto,
            trimestres_ok=run.quarters_worked,
            trimestres_requis=TRIMESTRES_REQUIS_TAUX_PLEIN,
            trimestres_restants=run.quarters_remaining,
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
            document_complet=document_complet,
        ),
        analyze=core,
    )
