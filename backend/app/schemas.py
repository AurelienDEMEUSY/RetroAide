"""Schémas API RetroAide (profil utilisateur, réponse analyse)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

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


class MissingQuarterItem(BaseModel):
    period: str
    reason: str
    action: str


class ChecklistItem(BaseModel):
    title: str
    detail: str = ""
    url: str = ""


class AnalyzeResponse(BaseModel):
    departure_age: int
    quarters_worked: int
    quarters_remaining: int
    missing_quarters: list[MissingQuarterItem]
    checklist: list[ChecklistItem]


class GlossaryRequest(BaseModel):
    term: str = Field(..., min_length=1, max_length=200)


class GlossaryResponse(BaseModel):
    explanation: str
