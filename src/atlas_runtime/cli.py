from __future__ import annotations

import argparse
import json
from pathlib import Path

from atlas_runtime import __version__
from atlas_runtime.core.runtime import doctor, gap_meter, init_workspace, replay, run_demo, verify
from atlas_runtime.mcp.server import serve as serve_mcp
from atlas_runtime.ui.server import serve_ui


def emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(prog="atlas")
    parser.add_argument("--version", action="version", version=f"atlas-runtime {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="Create a standalone Atlas runtime workspace.")
    init_cmd.add_argument("target", nargs="?", default="atlas-workspace")

    for name, help_text in [
        ("doctor", "Run the truth-oriented health checks."),
        ("run-demo", "Run the demo delivery pipeline."),
        ("verify", "Run the public verification surface."),
        ("interop-replay", "Verify the event spine replay surface."),
        ("gap-meter", "Show the gap progress summary."),
    ]:
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("target", nargs="?", default="atlas-workspace")

    mcp_cmd = sub.add_parser("mcp", help="Serve the read-only MCP-like tool surface.")
    mcp_sub = mcp_cmd.add_subparsers(dest="mcp_command", required=True)
    serve_cmd = mcp_sub.add_parser("serve", help="Serve Atlas runtime tools over HTTP.")
    serve_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", default=8766, type=int)

    ui_cmd = sub.add_parser("ui", help="Launch the local Atlas Runtime dashboard.")
    ui_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    ui_cmd.add_argument("--host", default="127.0.0.1")
    ui_cmd.add_argument("--port", default=8788, type=int)

    args = parser.parse_args()

    if args.command == "init":
        paths = init_workspace(Path(args.target).resolve())
        emit({"status": "PASS", "workspace": str(paths.root)})
        return 0

    target = Path(getattr(args, "target", "atlas-workspace")).resolve()
    if args.command == "doctor":
        result = doctor(target)
    elif args.command == "run-demo":
        result = run_demo(target)
    elif args.command == "verify":
        result = verify(target)
    elif args.command == "interop-replay":
        result = replay(target)
    elif args.command == "gap-meter":
        result = gap_meter(target)
    elif args.command == "mcp":
        serve_mcp(target, host=args.host, port=args.port)
        return 0
    elif args.command == "ui":
        serve_ui(target, host=args.host, port=args.port)
        return 0
    else:
        parser.error(f"unknown command: {args.command}")
        return 2

    emit(result)
    success_statuses = {"PASS", "production_ready", "developing", "bootstrapping"}
    return 0 if result.get("status", "PASS") in success_statuses else 1


if __name__ == "__main__":
    raise SystemExit(main())
