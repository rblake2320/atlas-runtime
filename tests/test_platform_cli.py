import json
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str) -> dict:
    command = [sys.executable, '-m', 'atlas_runtime.cli', *args]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    return json.loads(completed.stdout)


def test_backend_and_agent_cli(tmp_path: Path) -> None:
    workspace = tmp_path / 'cli-platform'
    run_cli('init', str(workspace))
    backend = run_cli('backend', 'status', str(workspace))
    assert backend['status'] == 'PASS'
    assert backend['active_backend'] == 'atlas_local'
    result = run_cli('agent', 'run', str(workspace), 'atlas-operator', 'deliver the demo pipeline')
    assert result['status'] == 'PASS'
    assert result['step_count'] >= 5


def test_local_chat_cli(tmp_path: Path) -> None:
    workspace = tmp_path / 'cli-chat'
    run_cli('init', str(workspace))
    result = run_cli('chat', str(workspace), 'summarize runtime state')
    assert result['status'] == 'PASS'
    assert result['backend'] == 'atlas_local'


def test_loop_cli(tmp_path: Path) -> None:
    workspace = tmp_path / 'cli-loop'
    run_cli('init', str(workspace))
    result = run_cli('loop', 'once', str(workspace))
    assert result['status'] == 'PASS'
    assert result['step_count'] >= 1
