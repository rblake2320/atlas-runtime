from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from atlas_runtime.core.runtime import init_workspace, run_demo
from atlas_runtime.mcp.server import AtlasMCPServer


def build_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "mcp-workspace"
    init_workspace(workspace)
    run_demo(workspace)
    return workspace


def test_tool_catalog_is_read_only(tmp_path: Path) -> None:
    server = AtlasMCPServer(build_workspace(tmp_path))
    tools = server.list_tools()
    assert [tool["name"] for tool in tools] == ["doctor", "status", "gap_meter"]
    assert all(tool["readOnly"] is True for tool in tools)


def test_status_reads_wrapper_state(tmp_path: Path) -> None:
    server = AtlasMCPServer(build_workspace(tmp_path))
    result = server.call_tool("status")
    payload = result["result"]
    assert payload["doctor_status"] == "PASS"
    assert payload["delivered"] == 3
    assert payload["gap_progress_pct"] == 29.0
    assert len(payload["verified_capabilities"]) >= 1
    assert len(payload["open_gaps"]) == 3


def test_gap_meter_reflects_wrapper_gap_registry(tmp_path: Path) -> None:
    server = AtlasMCPServer(build_workspace(tmp_path))
    result = server.call_tool("gap_meter")
    payload = result["result"]
    assert payload["verified"] == 1
    assert payload["active"] == 3
    assert payload["gap_count"] == 4


def test_stdio_json_rpc_initialize_and_tools_list(tmp_path: Path) -> None:
    server = AtlasMCPServer(build_workspace(tmp_path))
    message = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    response = server.handle_message(message)
    assert response["result"]["serverInfo"]["name"] == "atlas-runtime-mcp"

    message = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    response = server.handle_message(message)
    assert len(response["result"]["tools"]) == 3


def test_stdio_stream_round_trip(tmp_path: Path) -> None:
    server = AtlasMCPServer(build_workspace(tmp_path))
    input_stream = io.StringIO(json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "doctor", "arguments": {}}}) + "\n")
    output_stream = io.StringIO()
    server.serve_stdio(input_stream=input_stream, output_stream=output_stream)
    output = json.loads(output_stream.getvalue().strip())
    assert output["id"] == 7
    assert output["result"]["content"][0]["type"] == "text"
