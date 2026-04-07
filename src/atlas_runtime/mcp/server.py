from __future__ import annotations

import argparse
import io
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, TextIO

from atlas_runtime.mcp.state import snapshot


class AtlasMCPServer:
    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {'name': 'doctor', 'readOnly': True},
            {'name': 'status', 'readOnly': True},
            {'name': 'gap_meter', 'readOnly': True},
        ]

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        data = snapshot(self.workspace)
        key = 'gap_meter' if name == 'gap_meter' else name
        if key not in data:
            raise KeyError(name)
        return {'result': data[key]}

    def handle_message(self, message: dict[str, Any]) -> dict[str, Any]:
        method = message.get('method')
        ident = message.get('id')
        if method == 'initialize':
            return {'jsonrpc': '2.0', 'id': ident, 'result': {'serverInfo': {'name': 'atlas-runtime-mcp', 'version': '0.1.0'}}}
        if method == 'tools/list':
            return {'jsonrpc': '2.0', 'id': ident, 'result': {'tools': self.list_tools()}}
        if method == 'tools/call':
            params = message.get('params', {})
            result = self.call_tool(params.get('name', ''), params.get('arguments', {}))
            return {'jsonrpc': '2.0', 'id': ident, 'result': {'content': [{'type': 'text', 'text': json.dumps(result['result'])}]}}
        return {'jsonrpc': '2.0', 'id': ident, 'error': {'code': -32601, 'message': 'method_not_found'}}

    def serve_stdio(self, input_stream: TextIO | None = None, output_stream: TextIO | None = None) -> None:
        source = input_stream or io.TextIOWrapper(getattr(__import__('sys'), 'stdin').buffer, encoding='utf-8')
        sink = output_stream or io.TextIOWrapper(getattr(__import__('sys'), 'stdout').buffer, encoding='utf-8')
        for line in source:
            line = line.strip()
            if not line:
                continue
            response = self.handle_message(json.loads(line))
            sink.write(json.dumps(response) + '\n')
            sink.flush()


class Handler(BaseHTTPRequestHandler):
    server_obj = AtlasMCPServer(Path.cwd())

    def _write_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {'/', '/tools'}:
            self._write_json({'name': 'atlas-runtime-mcp', 'mode': 'read_only', 'tools': [tool['name'] for tool in Handler.server_obj.list_tools()]})
            return
        if self.path == '/tools/doctor':
            self._write_json(Handler.server_obj.call_tool('doctor')['result'])
            return
        if self.path == '/tools/status':
            self._write_json(Handler.server_obj.call_tool('status')['result'])
            return
        if self.path == '/tools/gap-meter':
            self._write_json(Handler.server_obj.call_tool('gap_meter')['result'])
            return
        self._write_json({'error': 'not_found'}, status=404)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def serve(workspace: Path, host: str = '127.0.0.1', port: int = 8766) -> None:
    Handler.server_obj = AtlasMCPServer(workspace)
    server = HTTPServer((host, port), Handler)
    print(json.dumps({'status': 'PASS', 'server': 'atlas-runtime-mcp', 'workspace': str(workspace), 'host': host, 'port': port}, indent=2))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(prog='atlas-mcp')
    parser.add_argument('workspace', nargs='?', default='atlas-workspace')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--stdio', action='store_true')
    args = parser.parse_args()
    server = AtlasMCPServer(Path(args.workspace).resolve())
    if args.once:
        print(json.dumps(snapshot(server.workspace), indent=2))
        return 0
    if args.stdio:
        server.serve_stdio()
        return 0
    serve(server.workspace, host=args.host, port=args.port)
    return 0
