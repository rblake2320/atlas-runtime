from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from atlas_runtime.mcp.server import AtlasMCPServer

ATLAS_ROOT = Path(r"C:\Users\techai\Desktop\Atlas Autonomous Group")


def test_tool_catalog_is_read_only() -> None:
    server = AtlasMCPServer(str(ATLAS_ROOT))
    tools = server.list_tools()
    assert [tool["name"] for tool in tools] == ["doctor", "status", "gap_meter"]
    assert all(tool["readOnly"] is True for tool in tools)


def test_status_reads_proven_atlas_state() -> None:
    server = AtlasMCPServer(str(ATLAS_ROOT))
    result = server.call_tool("status")
    payload = result["result"]
    assert payload["scorecard"]["status"] == "production_ready"
    assert payload["scorecard"]["score"] == 95
    assert payload["doctor"]["status"] == "PASS"
    assert payload["claims"]["status"] == "PASS"
    assert payload["gap_meter"]["gap_count"] == 5
    assert payload["gap_meter"]["overall_progress_pct"] == 29.9


def test_gap_meter_reflects_real_gap_registry() -> None:
    server = AtlasMCPServer(str(ATLAS_ROOT))
    result = server.call_tool("gap_meter")
    payload = result["result"]
    assert payload["verified"] == 1
    assert payload["active"] == 4
    assert any(gap["id"] == "autonomy_hours" for gap in payload["gaps"])


def test_stdio_json_rpc_initialize_and_tools_list() -> None:
    server = AtlasMCPServer(str(ATLAS_ROOT))
    message = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    response = server.handle_message(message)
    assert response["result"]["serverInfo"]["name"] == "atlas-runtime-mcp"

    message = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    response = server.handle_message(message)
    assert len(response["result"]["tools"]) == 3


def test_stdio_stream_round_trip() -> None:
    server = AtlasMCPServer(str(ATLAS_ROOT))
    input_stream = io.StringIO(json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "doctor", "arguments": {}}}) + "\n")
    output_stream = io.StringIO()
    server.serve_stdio(input_stream=input_stream, output_stream=output_stream)
    output = json.loads(output_stream.getvalue().strip())
    assert output["id"] == 7
    assert output["result"]["content"][0]["type"] == "text"
