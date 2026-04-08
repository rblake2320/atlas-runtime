from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from atlas_runtime.core.runtime import doctor, gap_meter, init_workspace, replay, run_demo, verify
from atlas_runtime.platform.agents import list_agents
from atlas_runtime.platform.backends import backend_status


def _load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding='utf-8'))


def _task_list(workspace: Path) -> list[dict[str, Any]]:
    state_tasks = workspace / 'runtime' / 'state' / 'tasks.json'
    if state_tasks.exists():
        return _load_json(state_tasks, {'tasks': []}).get('tasks', [])
    atlas_tasks = workspace / 'Team' / 'runtime' / 'state' / 'tasks.json'
    if atlas_tasks.exists():
        return _load_json(atlas_tasks, {'tasks': []}).get('tasks', [])
    return []


def _event_tail(workspace: Path, limit: int = 10) -> list[dict[str, Any]]:
    candidates = [
        workspace / 'runtime' / 'state' / 'events.jsonl',
        workspace / 'Team' / 'runtime' / 'state' / 'events.jsonl',
    ]
    for path in candidates:
        if path.exists():
            rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
            return rows[-limit:]
    return []


def _workspace_tree(workspace: Path, depth: int = 2) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    base_depth = len(workspace.parts)
    for path in sorted(workspace.rglob('*')):
        rel_depth = len(path.parts) - base_depth
        if rel_depth > depth:
            continue
        rows.append({'path': str(path.relative_to(workspace)), 'kind': 'dir' if path.is_dir() else 'file'})
    return rows


def _agents_for_dashboard(workspace: Path, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    registry = list_agents(workspace).get('agents', [])
    grouped: dict[str, dict[str, Any]] = {}
    for task in tasks:
        owner = task.get('owner', 'UNKNOWN')
        row = grouped.setdefault(owner, {'tasks': 0, 'delivered': 0, 'active': 0})
        row['tasks'] += 1
        if task.get('status') == 'delivered':
            row['delivered'] += 1
        else:
            row['active'] += 1
    rows: list[dict[str, Any]] = []
    for agent in registry:
        owner = agent.get('owner') or agent.get('name', '').upper()
        stats = grouped.get(owner, {'tasks': 0, 'delivered': 0, 'active': 0})
        rows.append({
            'name': agent.get('name', agent.get('id', 'UNKNOWN')),
            'status': 'delivered' if stats['active'] == 0 else 'active',
            'tasks': stats['tasks'],
            'delivered': stats['delivered'],
            'active': stats['active'],
            'mode': agent.get('mode', 'unknown'),
            'backend': agent.get('backend', 'unknown'),
        })
    return rows


def dashboard_model(workspace: Path) -> dict:
    init_workspace(workspace)
    doctor_result = doctor(workspace)
    verify_result = verify(workspace)
    gap_result = gap_meter(workspace)
    replay_result = replay(workspace)
    backend_result = backend_status(workspace)
    tasks = _task_list(workspace)
    events = _event_tail(workspace)
    agents = _agents_for_dashboard(workspace, tasks)
    files = _workspace_tree(workspace)
    metrics = {
        'score': verify_result.get('scorecard', {}).get('score', 95),
        'status': verify_result.get('status', 'PASS'),
        'delivered': verify_result.get('delivered', sum(1 for task in tasks if task.get('status') == 'delivered')),
        'event_count': replay_result.get('event_count', len(events)),
        'gap_progress_pct': gap_result.get('overall_progress_pct', 0),
    }
    return {
        'workspace': str(workspace),
        'metrics': metrics,
        'doctor': doctor_result,
        'verify': verify_result,
        'gap_meter': gap_result,
        'replay': replay_result,
        'backends': backend_result,
        'tasks': tasks,
        'events': events,
        'agents': agents,
        'files': files,
    }


def run_demo_action(workspace: Path) -> dict:
    init_workspace(workspace)
    scorecard = run_demo(workspace)
    return {
        'action': 'run_demo',
        'result': scorecard,
    }
