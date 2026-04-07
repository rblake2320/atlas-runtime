from pathlib import Path

from atlas_runtime.core.runtime import init_workspace, run_demo
from atlas_runtime.ui.state import dashboard_model, run_demo_action


def test_dashboard_model_and_demo_action(tmp_path: Path) -> None:
    workspace = tmp_path / 'ui-workspace'
    init_workspace(workspace)
    model = dashboard_model(workspace)
    assert model['doctor']['status'] == 'PASS'
    assert model['verify']['status'] == 'PASS'
    assert 'metrics' in model
    assert len(model['tasks']) == 3
    assert len(model['events']) >= 1
    assert len(model['files']) >= 1
    result = run_demo_action(workspace)
    assert result['result']['delivered'] == 3
    refreshed = dashboard_model(workspace)
    assert refreshed['verify']['delivered'] == 3
    assert refreshed['metrics']['event_count'] >= 4
