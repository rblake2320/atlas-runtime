from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from atlas_runtime.core.events import utc_now
from atlas_runtime.core.runtime import (
    deliver_next_task,
    doctor,
    gap_meter,
    init_workspace,
    read_tasks,
    replay,
    verify,
    workspace_paths,
)

TOOL_CATALOG = [
    {
        "name": "list_tasks",
        "mutating": False,
        "description": "Return the current task registry and delivery counts.",
    },
    {
        "name": "deliver_next_task",
        "mutating": True,
        "description": "Deliver the next dependency-ready task and emit evidence.",
    },
    {
        "name": "doctor",
        "mutating": False,
        "description": "Run the truthful runtime health checks.",
    },
    {
        "name": "verify",
        "mutating": False,
        "description": "Run the public verification surface.",
    },
    {
        "name": "gap_meter",
        "mutating": False,
        "description": "Return the gap progress summary.",
    },
    {
        "name": "replay",
        "mutating": False,
        "description": "Verify the event spine replay integrity.",
    },
    {
        "name": "loop_once",
        "mutating": True,
        "description": "Run one deterministic multi-agent dispatch tick.",
    },
]


def _append_tool_run(root: Path, actor: str, tool_name: str, arguments: dict[str, Any], result: dict[str, Any]) -> None:
    paths = workspace_paths(root)
    row = {
        "timestamp": utc_now(),
        "actor": actor,
        "tool": tool_name,
        "arguments": arguments,
        "status": result.get("status", "PASS"),
    }
    with paths.tool_runs_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")


def list_tools() -> dict[str, Any]:
    return {"status": "PASS", "count": len(TOOL_CATALOG), "tools": TOOL_CATALOG}


def run_tool(root: Path, tool_name: str, arguments: dict[str, Any] | None = None, actor: str = "atlas-operator") -> dict[str, Any]:
    init_workspace(root)
    args = arguments or {}
    if tool_name == "list_tasks":
        tasks = read_tasks(root)
        result = {
            "status": "PASS",
            "tasks": tasks,
            "delivered": sum(1 for task in tasks if task.get("status") == "delivered"),
        }
    elif tool_name == "deliver_next_task":
        result = deliver_next_task(root, actor=actor, owner_filter=args.get("owner_filter"))
    elif tool_name == "doctor":
        result = doctor(root)
    elif tool_name == "verify":
        result = verify(root)
    elif tool_name == "gap_meter":
        result = gap_meter(root)
    elif tool_name == "replay":
        result = replay(root)
    elif tool_name == "loop_once":
        from atlas_runtime.platform.loop import run_once

        result = run_once(root)
    else:
        result = {"status": "FAIL", "reason": "unknown_tool", "tool": tool_name}
    _append_tool_run(root, actor=actor, tool_name=tool_name, arguments=args, result=result)
    return result
