"""Plan LLM des outils d’enrichissement (liste blanche)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from tools.enrichment_handlers import TOOL_OPEN_DATA_BUNDLE
from tools.llm_research_orchestrator import (
    build_plan_preamble,
    llm_tool_orchestration_enabled,
    plan_retroaide_tool_calls,
    _parse_tool_plan,
)
from tools.mcp_pipeline import run_enrichment


def test_parse_tool_plan_accepts_fenced_json() -> None:
    raw = '```json\n{"tool_calls":[{"name":"x","rationale_for_user":"parce que"}]}\n```'
    out = _parse_tool_plan(raw)
    assert len(out) == 1
    assert out[0]["name"] == "x"
    assert "parce" in out[0]["rationale_for_user"]


def test_llm_tool_orchestration_enabled_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RETROAIDE_LLM_TOOL_ORCHESTRATION", raising=False)
    assert llm_tool_orchestration_enabled() is False
    monkeypatch.setenv("RETROAIDE_LLM_TOOL_ORCHESTRATION", "true")
    assert llm_tool_orchestration_enabled() is True


def test_build_plan_preamble_lists_calls() -> None:
    text = build_plan_preamble(
        [{"name": TOOL_OPEN_DATA_BUNDLE, "rationale_for_user": "Voir les tendances nationales."}]
    )
    assert "Choix des outils" in text
    assert TOOL_OPEN_DATA_BUNDLE in text
    assert "nationales" in text


@patch("tools.llm_research_orchestrator.emulate")
def test_plan_retroaide_tool_calls_parses_dict(mock_emulate) -> None:
    mock_emulate.return_value = {
        "tool_calls": [
            {
                "name": TOOL_OPEN_DATA_BUNDLE,
                "rationale_for_user": "Contexte public.",
            }
        ]
    }
    out = plan_retroaide_tool_calls({"birth_year": 1960})
    assert len(out) == 1
    assert out[0]["name"] == TOOL_OPEN_DATA_BUNDLE


def test_run_enrichment_prefixes_context_when_orchestration_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RETROAIDE_LLM_TOOL_ORCHESTRATION", "true")
    monkeypatch.setenv("ENABLE_OPENDATA_CONTEXT", "false")

    with patch(
        "tools.mcp_pipeline.plan_retroaide_tool_calls",
        return_value=[
            {"name": TOOL_OPEN_DATA_BUNDLE, "rationale_for_user": "Pour illustrer le cadre national."}
        ],
    ):
        r = run_enrichment({"birth_year": 1960})

    assert "Choix des outils" in r.context_block
    assert r.tools[0].sub_steps[0].get("source") == "llm_tool_plan"
    assert "Pour illustrer" in (r.tools[0].sub_steps[0].get("detail") or "")
