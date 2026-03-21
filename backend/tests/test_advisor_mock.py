from unittest.mock import patch

from ai.advisor import (
    FALLBACK_CHECKLIST,
    detect_missing_quarters,
    explain_term,
    generate_checklist,
    generate_guided_journey,
    synthesize_report_markdown,
)


def test_detect_missing_quarters_mock_normalizes() -> None:
    raw = [
        {"period": "Chômage 2003", "reason": "Droits possibles", "action": "Relevé Pôle emploi"},
        {"bad": "skipped"},
    ]
    with patch("ai.advisor.emulate", return_value=raw):
        out = detect_missing_quarters({"birth_year": 1963})
    assert len(out) == 1
    assert out[0]["period"] == "Chômage 2003"
    assert out[0]["reason"] == "Droits possibles"
    assert out[0]["action"] == "Relevé Pôle emploi"


def test_detect_missing_quarters_on_error_returns_empty() -> None:
    with patch("ai.advisor.emulate", side_effect=RuntimeError("no api key")):
        out = detect_missing_quarters({})
    assert out == []


def test_generate_checklist_mock_accepts_strings() -> None:
    with patch("ai.advisor.emulate", return_value=["Étape une", "Étape deux"]):
        out = generate_checklist({}, [])
    assert [x["title"] for x in out] == ["Étape une", "Étape deux"]
    assert all("detail" in x and "url" in x for x in out)


def test_generate_checklist_empty_raw_uses_fallback() -> None:
    with patch("ai.advisor.emulate", return_value=[]):
        out = generate_checklist({}, [])
    assert out == FALLBACK_CHECKLIST


def test_generate_checklist_on_error_uses_fallback() -> None:
    with patch("ai.advisor.emulate", side_effect=ConnectionError):
        out = generate_checklist({}, [])
    assert out == FALLBACK_CHECKLIST


def test_synthesize_report_markdown_mock() -> None:
    with patch("ai.advisor.emulate", return_value="# Titre\n\nCorps du rapport."):
        text = synthesize_report_markdown("seed", retrieval_context="ctx")
    assert text.startswith("# Titre")


def test_explain_term_mock() -> None:
    with patch("ai.advisor.emulate", return_value="  Un trimestre, c’est une unité de cotisation.  "):
        text = explain_term("trimestre")
    assert "trimestre" in text.lower() or "cotisation" in text.lower()


def test_generate_guided_journey_mock_normalizes() -> None:
    raw = [
        {
            "step": 2,
            "phase": "recap",
            "title": "B",
            "content": "Texte.",
            "optional_prompt": "",
        },
        {
            "step": 1,
            "phase": "prochaine_etape",
            "title": "A",
            "content": "Suite.",
            "optional_prompt": "Continuer ?",
        },
    ]
    with patch("ai.advisor.emulate", return_value=raw):
        out = generate_guided_journey({}, [], [])
    assert [x["step"] for x in out] == [1, 2]
    assert out[0]["title"] == "A"


def test_generate_guided_journey_empty_uses_fallback() -> None:
    with patch("ai.advisor.emulate", return_value=[]):
        out = generate_guided_journey(
            {"birth_year": 1955, "career_start_year": 1975},
            [{"period": "P1", "reason": "r", "action": "a"}],
            [{"title": "Aller à la caisse", "detail": "d", "url": ""}],
        )
    assert len(out) >= 2
    assert any("1955" in str(s.get("content", "")) for s in out)


def test_explain_term_empty_or_error_uses_fallback() -> None:
    with patch("ai.advisor.emulate", return_value=""):
        text = explain_term("décote")
    assert "décote" in text
    with patch("ai.advisor.emulate", side_effect=OSError):
        text2 = explain_term("Agirc-Arrco")
    assert "Agirc-Arrco" in text2
