from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, TextIO

from .state import DEFAULT_ATLAS_ROOT, gap_details, load_atlas_state, summarize_state

SERVER_NAME = "atlas-runtime-mcp"
SERVER_VERSION = "0.1.0"
TOOL_NAMES = ("doctor", "status", "gap_meter")


class AtlasMCPServer:
    def __init__(self, atlas_root: str | Path | None = None) -> None:
        self.atlas_root = Path(atlas_root) if atlas_root is not None else DEFAULT_ATLAS_ROOT
        self.state = load_atlas_state(self.atlas_root)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "doctor",
                "description": "Return the live Atlas doctor report from proven state.",
                "inputSchema": {"type": "object", "properties": {}},
                "outputSchema": {"type": "object"},
                "readOnly": True,
            },
            {
                "name": "status",
                "description": "Return a concise wrapper status summary from proven Atlas state.",
                "inputSchema": {"type": "object", "properties": {}},
                "outputSchema": {"type": "object"},
                "readOnly": True,
            },
            {
                "name": "gap_meter",
                "description": "Return the live Atlas gap meter summary from proven state.",
                "inputSchema": {"type": "object", "properties": {}},
                "outputSchema": {"type": "object"},
                "readOnly": True,
            },
        ]

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        if name == "doctor":
            return {"tool": name, "result": self.state.doctor}
        if name == "status":
            return {"tool": name, "result": summarize_state(self.state)}
        if name == "gap_meter":
            return {"tool": name, "result": gap_details(self.state)}
        raise KeyError(f"Unknown tool: {name}")

    def handle_message(self, message: dict[str, Any]) -> dict[str, Any] | None:
        method = message.get("method")
        request_id = message.get("id")
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    "capabilities": {"tools": {"listChanged": False}},
                },
            }
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.list_tools()},
            }
        if method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            tool_args = params.get("arguments") or {}
            result = self.call_tool(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                    "isError": False,
                },
            }
        if request_id is None:
            return None
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Unsupported method: {method}"},
        }

    def serve_stdio(self, input_stream: TextIO | None = None, output_stream: TextIO | None = None) -> None:
        input_stream = input_stream or sys.stdin
        output_stream = output_stream or sys.stdout
        for raw_line in input_stream:
            line = raw_line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
                response = self.handle_message(message)
            except Exception as exc:  # pragma: no cover - defensive wire guard
                request_id = message.get("id") if isinstance(message, dict) else None
                response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(exc)}}
            if response is None:
                continue
            output_stream.write(json.dumps(response) + "\n")
            output_stream.flush()


class AtlasHTTPRequestHandler(BaseHTTPRequestHandler):
    atlas_root = DEFAULT_ATLAS_ROOT

    def _write_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        server = AtlasMCPServer(self.atlas_root)
        if self.path in {"/", "/tools"}:
            self._write_json({"name": SERVER_NAME, "mode": "read_only", "tools": TOOL_NAMES})
            return
        if self.path == "/tools/doctor":
            self._write_json(server.call_tool("doctor")["result"])
            return
        if self.path in {"/tools/status", "/tools/summary"}:
            self._write_json(server.call_tool("status")["result"])
            return
        if self.path in {"/tools/gap-meter", "/tools/gap_meter"}:
            self._write_json(server.call_tool("gap_meter")["result"])
            return
        self._write_json({"error": "not_found"}, status=404)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def serve(workspace: Path | str, host: str = "127.0.0.1", port: int = 8766) -> None:
    AtlasHTTPRequestHandler.atlas_root = Path(workspace)
    server = HTTPServer((host, port), AtlasHTTPRequestHandler)
    print(json.dumps({"status": "PASS", "server": SERVER_NAME, "workspace": str(workspace), "host": host, "port": port}, indent=2))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atlas runtime MCP surface")
    parser.add_argument("--atlas-root", default=None, help="Path to a proven Atlas workspace")
    parser.add_argument("--once", action="store_true", help="Print the tool list and exit")
    parser.add_argument("--http", action="store_true", help="Serve the read-only HTTP surface instead of stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8766, type=int)
    args = parser.parse_args(argv)
    server = AtlasMCPServer(args.atlas_root)
    if args.once:
        print(json.dumps({"server": SERVER_NAME, "tools": server.list_tools()}, indent=2))
        return 0
    if args.http:
        serve(server.atlas_root, host=args.host, port=args.port)
        return 0
    server.serve_stdio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
