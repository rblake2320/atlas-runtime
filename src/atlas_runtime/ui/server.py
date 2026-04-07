from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from atlas_runtime.ui.state import dashboard_model, run_demo_action


class AtlasUIHandler(BaseHTTPRequestHandler):
    workspace = Path.cwd()
    static_root = Path(__file__).resolve().parent / 'static'

    def _send(self, content: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        self._send(json.dumps(payload, indent=2).encode('utf-8'), 'application/json', status=status)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {'/', '/index.html'}:
            body = (self.static_root / 'index.html').read_bytes()
            self._send(body, 'text/html; charset=utf-8')
            return
        if self.path == '/app.js':
            self._send((self.static_root / 'app.js').read_bytes(), 'application/javascript; charset=utf-8')
            return
        if self.path == '/styles.css':
            self._send((self.static_root / 'styles.css').read_bytes(), 'text/css; charset=utf-8')
            return
        if self.path == '/api/status':
            self._send_json(dashboard_model(self.workspace))
            return
        self._send_json({'error': 'not_found'}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path == '/api/run-demo':
            self._send_json(run_demo_action(self.workspace))
            return
        self._send_json({'error': 'not_found'}, status=404)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def serve_ui(workspace: Path, host: str = '127.0.0.1', port: int = 8788) -> None:
    AtlasUIHandler.workspace = workspace
    server = HTTPServer((host, port), AtlasUIHandler)
    print(json.dumps({'status': 'PASS', 'server': 'atlas-runtime-ui', 'workspace': str(workspace), 'host': host, 'port': port}, indent=2))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(prog='atlas-ui')
    parser.add_argument('workspace', nargs='?', default='atlas-workspace')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8788)
    args = parser.parse_args()
    serve_ui(Path(args.workspace).resolve(), host=args.host, port=args.port)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
