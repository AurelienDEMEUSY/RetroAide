"""Import serveur MCP (sans lancer stdio)."""

from __future__ import annotations


def test_mcp_server_fastmcp_instance_exists() -> None:
    import mcp_server.server as srv

    assert srv.mcp is not None
    assert srv.retroaide_open_data_context is not None
    assert srv.retroaide_llm_plan_open_data_tools is not None
