"""Schémas API RetroAide (profil utilisateur, réponse analyse)."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator

MaritalStatus = Literal["marie", "pacse", "celibataire", "divorce", "veuf"]
ProfessionalStatus = Literal["salarie_prive", "fonctionnaire", "independant", "liberale", "agriculteur"]
CareerStartAge = Literal["avant_16", "avant_18", "avant_20", "avant_21", "apres_21", ""]
CareerBreak = Literal["chomage", "maladie", "invalidite", "etranger", "parental"]
MainObjective = Literal["partir_tot", "retraite_max", "lever_pied", "augmenter_revenus", ""]
PerGestionType = Literal["pilotee", "libre", "a_definir", ""]
PerFormeSortie = Literal["capital", "rente", "mixte", "a_definir", ""]
PerOptionFiscale = Literal["deductible", "non_deductible", "a_decider", ""]
PerBooleanOptions = Literal["oui", "non", "je_ne_sais_pas", ""]

class UserProfile(BaseModel):
    birth_month: int = Field(..., ge=1, le=12)
    birth_year: int = Field(..., ge=1900, le=2100)
    marital_status: MaritalStatus
    nb_enfants: int = Field(default=0, ge=0, le=15)
    
    professional_statuses: list[ProfessionalStatus] = Field(default_factory=list)
    career_start_age: CareerStartAge
    career_breaks: list[CareerBreak] = Field(default_factory=list)
    
    currently_employed: bool
    current_income_annual: Optional[int] = Field(default=None, ge=0)
    validated_quarters: int = Field(default=0, ge=0, le=300)
    
    main_objective: MainObjective
    target_departure_age: Optional[int] = Field(default=None, ge=50, le=80)

    # Document / cas particuliers (optionnel — pour export PDF / fusion)
    full_name: str = Field(default="", max_length=200)
    ville_signature: str = Field(default="", max_length=120)
    nb_mois_armee: Optional[int] = Field(default=None, ge=0, le=120)
    # kept for compatibility with pdf generation payload if needed
    nb_trimestres_avant_20: Optional[int] = Field(default=None, ge=0, le=24)
    pays_etranger: str = Field(default="", max_length=2000)
    montant_estime_euros: Optional[int] = Field(default=None, ge=1)

    # Nouveaux champs pour la génération du Contrat PER spécifique
    per_organisme: Optional[str] = Field(default="", max_length=500)
    per_versement_mensuel: Optional[int] = Field(default=None, ge=0)
    per_versement_ponctuel: Optional[int] = Field(default=None, ge=0)
    per_gestion_type: Optional[PerGestionType] = Field(default="")
    per_forme_sortie: Optional[PerFormeSortie] = Field(default="")
    per_option_fiscale: Optional[PerOptionFiscale] = Field(default="")
    per_plan_entreprise: Optional[PerBooleanOptions] = Field(default="")
    per_anciens_contrats: Optional[PerBooleanOptions] = Field(default="")


class MissingQuarterItem(BaseModel):
    period: str
    reason: str
    action: str


class ChecklistItem(BaseModel):
    title: str
    detail: str = ""
    url: str = ""


GuidedPhase = Literal["recap", "point_a_clarifier", "prochaine_etape"]


class GuidedJourneyStep(BaseModel):
    """Parcours guidé type assistant : récap → points à clarifier → prochaines étapes."""

    step: int = Field(..., ge=1, le=15)
    phase: GuidedPhase
    title: str
    content: str
    optional_prompt: str = ""


class EnrichmentTraceItem(BaseModel):
    """Trace d’un outil MCP équivalent (appel API externe ou bundle)."""

    tool: str
    ok: bool
    sources: list[str] = Field(default_factory=list)
    error: str | None = None
    sub_steps: list[dict[str, Any]] = Field(default_factory=list)


class EnrichmentSection(BaseModel):
    """Contexte injecté au LLM + traçabilité des outils (CNAV, data.gouv, …)."""

    context_block: str
    sources_touched: list[str] = Field(default_factory=list)
    tools: list[EnrichmentTraceItem] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    departure_age: int
    quarters_worked: int
    quarters_remaining: int
    missing_quarters: list[MissingQuarterItem]
    checklist: list[ChecklistItem]
    guided_journey: list[GuidedJourneyStep]
    enrichment: EnrichmentSection


class IdentitySection(BaseModel):
    nom_utilisateur: str
    id_dossier: str
    ville_signature: str
    date_signature: str


class KeyFiguresSection(BaseModel):
    age_legal: int
    age_taux_plein_auto: int
    trimestres_ok: int
    trimestres_requis: int
    trimestres_restants: int
    montant_estime: Optional[int] = None


class SpecialCasesSection(BaseModel):
    nb_enfants: Optional[int] = None
    nb_mois_armee: Optional[int] = None
    nb_trimestres_avant_20: Optional[int] = None
    pays_etranger: str = ""
    liste_periodes_manquantes: str


class MarkdownSections(BaseModel):
    """Blocs markdown prêts pour MDX, Pandoc ou rendu React."""

    synthese: str
    checklist: str
    cas_particuliers: str
    parcours_guide: str
    document_complet: str


class AnalyzeReportResponse(BaseModel):
    """
    Réponse enrichie : blocs structurés (`identity`, `key_figures`, `special_cases`) = source unique
    pour affichage et pour une fusion PDF (plus de dict `placeholders` dupliqué).
    Inclut aussi `analyze` (même contenu que POST /analyze seul).
    """

    identity: IdentitySection
    key_figures: KeyFiguresSection
    special_cases: SpecialCasesSection
    markdown: MarkdownSections
    enrichment: EnrichmentSection
    analyze: AnalyzeResponse


# ---------------------------------------------------------------------------
# Pipeline chaîné : schémas intermédiaires
# ---------------------------------------------------------------------------


class ComputeResponse(BaseModel):
    """Sortie de l'étape compute (calculs déterministes + enrichissement open data)."""

    departure_age: int
    age_taux_plein_auto: int
    quarters_worked: int
    quarters_remaining: int
    enrichment: EnrichmentSection
    profile: dict[str, Any]


class AiAnalyzeRequest(BaseModel):
    """Entrée de l'étape AI : résultat compute + champs identité optionnels."""

    compute: ComputeResponse
    # Champs facultatifs pour la génération du rapport complet
    full_name: str = ""
    ville_signature: str = ""
    nb_enfants: Optional[int] = None
    nb_mois_armee: Optional[int] = None
    nb_trimestres_avant_20: Optional[int] = None
    pays_etranger: str = ""
    montant_estime_euros: Optional[int] = Field(default=None, ge=1)


class GlossaryRequest(BaseModel):
    term: str = Field(..., min_length=1, max_length=200)


class GlossaryResponse(BaseModel):
    explanation: str

