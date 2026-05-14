import importlib
import sys

from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def test_mcp_tool_registration_logs_arguments_as_key_value_pairs(monkeypatch):
    monkeypatch.setenv("ABACUSAGENT_MODEL", "test")

    import abacusagent.init_mcp as init_mcp

    init_mcp = importlib.reload(init_mcp)

    @init_mcp.mcp.tool()
    def demo_tool(sample, options=None, limit=3):
        return {"sample": sample, "options": options, "limit": limit}

    with patch("abacusagent.init_mcp.logger.info") as mock_info:
        result = demo_tool("alpha", options={"beta": 2, "gamma": [1, 2]}, limit=7)

    assert result == {"sample": "alpha", "options": {"beta": 2, "gamma": [1, 2]}, "limit": 7}
    assert mock_info.call_count == 1

    message, tool_name, formatted_arguments = mock_info.call_args.args
    assert message == "MCP tool call: %s\n%s"
    assert tool_name == "demo_tool"
    assert "sample = 'alpha'" in formatted_arguments
    assert "options =" in formatted_arguments
    assert "beta" in formatted_arguments
    assert "limit = 7" in formatted_arguments
