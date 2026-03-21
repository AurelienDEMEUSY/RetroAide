"""Schémas API RetroAide (profil utilisateur, réponse analyse)."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator

EmploymentStatus = Literal["salarie_prive", "fonctionnaire", "autre"]


class UserProfile(BaseModel):
    birth_year: int = Field(..., ge=1900, le=2100)
    career_start_year: int = Field(..., ge=1900, le=2100)
    status: EmploymentStatus
    currently_employed: bool
    had_children: bool = False
    had_unemployment: bool = False
    had_long_sick_leave: bool = False
    had_military_service: bool = False
    long_part_time_years: bool = False

    @model_validator(mode="after")
    def check_career_after_birth(self):
        """Vérifie que la carrière commence après l'âge légal minimum de travail."""
        if self.career_start_year < self.birth_year + 14:
            raise ValueError(
                f"career_start_year ({self.career_start_year}) doit être ≥ birth_year + 14 "
                f"({self.birth_year + 14})"
            )
        return self
    # Document / cas particuliers (optionnel — pour export PDF / fusion)
    full_name: str = Field(default="", max_length=200)
    ville_signature: str = Field(default="", max_length=120)
    # Bornes volontairement serrées (usage pédagogique / hackathon, pas extrêmes absurdes)
    nb_enfants: Optional[int] = Field(default=None, ge=0, le=15)
    nb_mois_armee: Optional[int] = Field(default=None, ge=0, le=120)
    nb_trimestres_avant_20: Optional[int] = Field(default=None, ge=0, le=24)
    pays_etranger: str = Field(default="", max_length=2000)
    # Omettre le champ ou null = non renseigné ; 0 € n’est pas accepté (évite confusion avec « vide »)
    montant_estime_euros: Optional[int] = Field(default=None, ge=1)


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

