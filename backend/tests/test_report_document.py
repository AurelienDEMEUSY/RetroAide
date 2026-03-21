"""core/report_document — formats liste / markdown."""

from __future__ import annotations

from core.report_document import (
    format_checklist_summary_for_seed,
    format_missing_periods_plain,
    format_missing_periods_markdown,
    format_special_cases_markdown,
)


def test_format_missing_periods_plain_joins() -> None:
    rows = [
        {"period": "Chômage 1998", "reason": "", "action": ""},
        {"period": "Stage 1985", "reason": "x", "action": "y"},
    ]
    assert format_missing_periods_plain(rows) == "Chômage 1998, Stage 1985"


def test_format_missing_periods_markdown_bullets() -> None:
    rows = [{"period": "P1", "reason": "R", "action": "A"}]
    md = format_missing_periods_markdown(rows)
    assert "- P1" in md
    assert "R" in md
    assert "A" in md


def test_format_checklist_summary_for_seed_titles_only() -> None:
    raw = [
        {"title": "Étape A", "detail": "long detail", "url": "https://x"},
        {"title": "Étape B", "detail": "", "url": ""},
    ]
    s = format_checklist_summary_for_seed(raw)
    assert "1. Étape A" in s
    assert "2. Étape B" in s
    assert "https://" not in s


def test_format_special_cases_coherent_enfants_militaire() -> None:
    md = format_special_cases_markdown(
        nb_enfants=2,
        nb_mois_armee=12,
        nb_trimestres_avant_20=None,
        pays_etranger="",
        had_children=False,
        had_military_service=False,
    )
    assert ": 2 _(renseigné)_" in md
    assert ": 12 _(durée renseignée)_" in md
    assert "case famille : non" not in md
