from pathlib import Path

from atlas_runtime.core.runtime import init_workspace, read_tasks, verify
from atlas_runtime.platform.adapters import chat
from atlas_runtime.platform.agents import list_agents, run_agent
from atlas_runtime.platform.backends import backend_status, list_backends
from atlas_runtime.platform.loop import run_once
from atlas_runtime.platform.tools import list_tools, run_tool


def test_backend_registry_and_tool_catalog(tmp_path: Path) -> None:
    workspace = tmp_path / 'platform-workspace'
    init_workspace(workspace)
    backends = list_backends(workspace)
    assert backends['status'] == 'PASS'
    assert backends['active_backend'] == 'atlas_local'
    assert backends['count'] >= 5
    status = backend_status(workspace)
    assert status['active']['id'] == 'atlas_local'
    assert status['active']['verified'] is True
    tools = list_tools()
    assert tools['count'] >= 7
    tool_result = run_tool(workspace, 'list_tasks', actor='atlas-operator')
    assert tool_result['status'] == 'PASS'
    assert len(tool_result['tasks']) == 3


def test_agent_runner_completes_demo_pipeline(tmp_path: Path) -> None:
    workspace = tmp_path / 'agent-workspace'
    init_workspace(workspace)
    agents = list_agents(workspace)
    assert agents['status'] == 'PASS'
    assert agents['count'] >= 4
    result = run_agent(workspace, 'atlas-operator', 'deliver the demo pipeline and verify it')
    assert result['status'] == 'PASS'
    assert result['step_count'] >= 5
    assert Path(result['transcript']).exists()
    verification = verify(workspace)
    assert verification['status'] == 'PASS'
    assert verification['delivered'] == 3


def test_owner_agents_and_loop_dispatch_tasks(tmp_path: Path) -> None:
    workspace = tmp_path / 'loop-workspace'
    init_workspace(workspace)
    first = run_agent(workspace, 'oracle', 'advance assigned work')
    assert first['status'] == 'PASS'
    assert any(step['result'].get('task_id') == 'AR-0001' for step in first['steps'] if step['tool'] == 'deliver_next_task')
    second = run_once(workspace)
    assert second['status'] == 'PASS'
    tasks = read_tasks(workspace)
    assert sum(1 for task in tasks if task['status'] == 'delivered') >= 2


def test_local_chat_backend_returns_real_workspace_summary(tmp_path: Path) -> None:
    workspace = tmp_path / 'chat-workspace'
    init_workspace(workspace)
    result = chat(workspace, 'summarize current runtime state')
    assert result['status'] == 'PASS'
    assert result['backend'] == 'atlas_local'
    assert 'Delivered tasks' in result['content']
