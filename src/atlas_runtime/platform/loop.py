from __future__ import annotations

from pathlib import Path

from atlas_runtime.core.events import EventStore, utc_now
from atlas_runtime.core.runtime import init_workspace, workspace_paths
from atlas_runtime.platform.agents import ensure_agents, run_agent
from atlas_runtime.platform.tools import run_tool


def run_once(root: Path) -> dict:
    init_workspace(root)
    registry = ensure_agents(root)
    steps: list[dict] = []
    progress = 0
    for agent in registry.get('agents', []):
        if agent.get('mode') != 'owner_dispatch':
            continue
        result = run_agent(root, agent['id'], 'advance assigned work')
        steps.append({"agent_id": agent['id'], "result": result})
        deliver_steps = [step for step in result.get('steps', []) if step['tool'] == 'deliver_next_task']
        if any(step['result'].get('status') == 'PASS' for step in deliver_steps):
            progress += 1
    if progress == 0:
        steps.append({"tool": "doctor", "result": run_tool(root, 'doctor', actor='HELM')})
        steps.append({"tool": "verify", "result": run_tool(root, 'verify', actor='HELM')})
    EventStore(workspace_paths(root).events_file).append(
        'loop.tick',
        'HELM',
        {'timestamp': utc_now(), 'progress': progress, 'steps': len(steps)},
    )
    return {
        'status': 'PASS',
        'progress': progress,
        'step_count': len(steps),
        'steps': steps,
    }
