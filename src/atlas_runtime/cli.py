from __future__ import annotations

import argparse
import json
from pathlib import Path

from atlas_runtime import __version__
from atlas_runtime.core.runtime import doctor, gap_meter, init_workspace, replay, run_demo, verify
from atlas_runtime.mcp.server import serve as serve_mcp
from atlas_runtime.platform.adapters import chat
from atlas_runtime.platform.agents import list_agents, run_agent
from atlas_runtime.platform.backends import backend_status, list_backends, set_active_backend
from atlas_runtime.platform.loop import run_once
from atlas_runtime.platform.tools import list_tools, run_tool
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

    backend_cmd = sub.add_parser("backend", help="Inspect and manage runtime backends.")
    backend_sub = backend_cmd.add_subparsers(dest="backend_command", required=True)
    backend_list_cmd = backend_sub.add_parser("list", help="List configured backends.")
    backend_list_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    backend_status_cmd = backend_sub.add_parser("status", help="Show backend readiness.")
    backend_status_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    backend_set_cmd = backend_sub.add_parser("set", help="Set the active backend.")
    backend_set_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    backend_set_cmd.add_argument("backend_id")

    tool_cmd = sub.add_parser("tool", help="Inspect or run built-in runtime tools.")
    tool_sub = tool_cmd.add_subparsers(dest="tool_command", required=True)
    tool_list_cmd = tool_sub.add_parser("list", help="List the tool catalog.")
    tool_list_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    tool_run_cmd = tool_sub.add_parser("run", help="Run one built-in tool.")
    tool_run_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    tool_run_cmd.add_argument("tool_name")
    tool_run_cmd.add_argument("--args", default="{}")
    tool_run_cmd.add_argument("--actor", default="atlas-operator")

    loop_cmd = sub.add_parser("loop", help="Run the deterministic multi-agent control loop.")
    loop_sub = loop_cmd.add_subparsers(dest="loop_command", required=True)
    loop_once_cmd = loop_sub.add_parser("once", help="Run one owner-aware dispatch tick.")
    loop_once_cmd.add_argument("target", nargs="?", default="atlas-workspace")

    agent_cmd = sub.add_parser("agent", help="List agents or run a local agent objective.")
    agent_sub = agent_cmd.add_subparsers(dest="agent_command", required=True)
    agent_list_cmd = agent_sub.add_parser("list", help="List registered agents.")
    agent_list_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    agent_run_cmd = agent_sub.add_parser("run", help="Run one agent objective through the active backend.")
    agent_run_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    agent_run_cmd.add_argument("agent_id")
    agent_run_cmd.add_argument("objective")

    chat_cmd = sub.add_parser("chat", help="Run a prompt through the active backend.")
    chat_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    chat_cmd.add_argument("prompt")
    chat_cmd.add_argument("--system", default=None)

    mcp_cmd = sub.add_parser("mcp", help="Serve the read-only MCP-like tool surface.")
    mcp_sub = mcp_cmd.add_subparsers(dest="mcp_command", required=True)
    serve_cmd = mcp_sub.add_parser("serve", help="Serve Atlas runtime tools over HTTP.")
    serve_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", default=8766, type=int)

    ui_cmd = sub.add_parser("ui", help="Launch the local Atlas Runtime dashboard.")
    ui_cmd.add_argument("target", nargs="?", default="atlas-workspace")
    ui_cmd.add_argument("--host", default="127.0.0.1")
    ui_cmd.add_argument("--port", default=8788)

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
    elif args.command == "backend":
        if args.backend_command == "list":
            result = list_backends(target)
        elif args.backend_command == "status":
            result = backend_status(target)
        elif args.backend_command == "set":
            result = set_active_backend(target, args.backend_id)
        else:
            parser.error(f"unknown backend command: {args.backend_command}")
            return 2
    elif args.command == "tool":
        if args.tool_command == "list":
            result = list_tools()
        elif args.tool_command == "run":
            result = run_tool(target, args.tool_name, arguments=json.loads(args.args), actor=args.actor)
        else:
            parser.error(f"unknown tool command: {args.tool_command}")
            return 2
    elif args.command == "loop":
        if args.loop_command == "once":
            result = run_once(target)
        else:
            parser.error(f"unknown loop command: {args.loop_command}")
            return 2
    elif args.command == "agent":
        if args.agent_command == "list":
            result = list_agents(target)
        elif args.agent_command == "run":
            result = run_agent(target, args.agent_id, args.objective)
        else:
            parser.error(f"unknown agent command: {args.agent_command}")
            return 2
    elif args.command == "chat":
        result = chat(target, args.prompt, system=args.system)
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
    success_statuses = {"PASS", "production_ready", "developing", "bootstrapping", "NOOP"}
    return 0 if result.get("status", "PASS") in success_statuses else 1


if __name__ == "__main__":
    raise SystemExit(main())
