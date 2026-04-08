from __future__ import annotations

from pathlib import Path
from typing import Any

from atlas_runtime.core.events import EventStore, utc_now
from atlas_runtime.core.runtime import dump_json, init_workspace, load_json, workspace_paths
from atlas_runtime.platform.backends import backend_status, ensure_backends
from atlas_runtime.platform.tools import run_tool

DEFAULT_AGENTS = {
    "agents": [
        {
            "id": "atlas-operator",
            "name": "Atlas Operator",
            "backend": "atlas_local",
            "mode": "tool_orchestrator",
            "verified": True,
            "owner": None,
            "tools": ["list_tasks", "deliver_next_task", "doctor", "verify", "gap_meter", "replay"],
        },
        {
            "id": "oracle",
            "name": "ORACLE",
            "backend": "atlas_local",
            "mode": "owner_dispatch",
            "verified": True,
            "owner": "ORACLE",
            "tools": ["list_tasks", "deliver_next_task"],
        },
        {
            "id": "prism",
            "name": "PRISM",
            "backend": "atlas_local",
            "mode": "owner_dispatch",
            "verified": True,
            "owner": "PRISM",
            "tools": ["list_tasks", "deliver_next_task"],
        },
        {
            "id": "sentinel",
            "name": "SENTINEL",
            "backend": "atlas_local",
            "mode": "owner_dispatch",
            "verified": True,
            "owner": "SENTINEL",
            "tools": ["list_tasks", "deliver_next_task", "verify"],
        }
    ]
}


def _file(root: Path) -> Path:
    return workspace_paths(root).agents_file


def ensure_agents(root: Path) -> dict[str, Any]:
    init_workspace(root)
    ensure_backends(root)
    path = _file(root)
    if not path.exists():
        dump_json(path, DEFAULT_AGENTS)
        return DEFAULT_AGENTS
    data = load_json(path, DEFAULT_AGENTS)
    current = {row["id"]: row for row in data.get("agents", [])}
    for row in DEFAULT_AGENTS["agents"]:
        current.setdefault(row["id"], row)
    merged = {"agents": list(current.values())}
    dump_json(path, merged)
    return merged


def list_agents(root: Path) -> dict[str, Any]:
    data = ensure_agents(root)
    return {"status": "PASS", "count": len(data.get("agents", [])), "agents": data.get("agents", [])}


def _write_transcript(root: Path, agent_id: str, objective: str, steps: list[dict[str, Any]], status: str) -> Path:
    paths = workspace_paths(root)
    timestamp = utc_now().replace(':', '').replace('-', '')
    path = paths.transcripts_dir / f"{timestamp}_{agent_id}.json"
    dump_json(path, {
        "timestamp": utc_now(),
        "agent_id": agent_id,
        "objective": objective,
        "status": status,
        "step_count": len(steps),
        "steps": steps,
    })
    return path


def _complete_demo(root: Path, agent_id: str) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    steps.append({"tool": "list_tasks", "result": run_tool(root, "list_tasks", actor=agent_id)})
    while True:
        result = run_tool(root, "deliver_next_task", actor=agent_id)
        steps.append({"tool": "deliver_next_task", "result": result})
        if result.get("status") == "NOOP":
            break
    steps.append({"tool": "doctor", "result": run_tool(root, "doctor", actor=agent_id)})
    steps.append({"tool": "verify", "result": run_tool(root, "verify", actor=agent_id)})
    steps.append({"tool": "gap_meter", "result": run_tool(root, "gap_meter", actor=agent_id)})
    return steps


def _owner_step(root: Path, agent: dict[str, Any]) -> list[dict[str, Any]]:
    owner = agent.get("owner")
    steps = [{"tool": "list_tasks", "result": run_tool(root, "list_tasks", actor=agent["id"]) }]
    steps.append({
        "tool": "deliver_next_task",
        "result": run_tool(root, "deliver_next_task", arguments={"owner_filter": owner}, actor=agent["id"]),
    })
    if agent["id"] == "sentinel":
        steps.append({"tool": "verify", "result": run_tool(root, "verify", actor=agent["id"])})
    return steps


def run_agent(root: Path, agent_id: str, objective: str) -> dict[str, Any]:
    init_workspace(root)
    registry = ensure_agents(root)
    agent = next((row for row in registry.get("agents", []) if row["id"] == agent_id), None)
    if agent is None:
        return {"status": "FAIL", "reason": "unknown_agent", "agent_id": agent_id}

    backends = backend_status(root)
    active = backends.get("active")
    if active is None or active.get("id") != agent.get("backend"):
        return {
            "status": "FAIL",
            "reason": "backend_mismatch",
            "active_backend": backends.get("active_backend"),
            "agent_backend": agent.get("backend"),
        }

    if active.get("kind") != "builtin":
        return {
            "status": "FAIL",
            "reason": "external_backend_not_verified",
            "active_backend": active.get("id"),
            "message": "The wrapper only verifies atlas_local execution today. External providers are adapter-ready but not yet proven.",
        }

    lowered = objective.lower()
    if agent.get("mode") == "owner_dispatch" and any(token in lowered for token in ["assigned", "next", "work", "deliver", "advance"]):
        steps = _owner_step(root, agent)
    elif any(token in lowered for token in ["deliver", "ship", "demo", "pipeline", "close"]):
        steps = _complete_demo(root, agent_id)
    elif "doctor" in lowered or "health" in lowered:
        steps = [{"tool": "doctor", "result": run_tool(root, "doctor", actor=agent_id)}]
    elif "gap" in lowered:
        steps = [{"tool": "gap_meter", "result": run_tool(root, "gap_meter", actor=agent_id)}]
    elif "replay" in lowered:
        steps = [{"tool": "replay", "result": run_tool(root, "replay", actor=agent_id)}]
    else:
        steps = [
            {"tool": "list_tasks", "result": run_tool(root, "list_tasks", actor=agent_id)},
            {"tool": "verify", "result": run_tool(root, "verify", actor=agent_id)},
        ]

    final_status = "PASS" if all(step["result"].get("status") in {"PASS", "NOOP", "production_ready"} for step in steps) else "FAIL"
    transcript = _write_transcript(root, agent_id, objective, steps, final_status)
    EventStore(workspace_paths(root).events_file).append(
        "agent.run.completed",
        agent_id,
        {"objective": objective, "status": final_status, "transcript": transcript.name},
    )
    return {
        "status": final_status,
        "agent_id": agent_id,
        "objective": objective,
        "step_count": len(steps),
        "transcript": str(transcript),
        "steps": steps,
    }

