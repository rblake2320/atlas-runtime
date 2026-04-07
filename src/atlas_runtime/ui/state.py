from __future__ import annotations

from pathlib import Path

from atlas_runtime.core.runtime import doctor, gap_meter, init_workspace, replay, run_demo, verify


def dashboard_model(workspace: Path) -> dict:
    init_workspace(workspace)
    doctor_result = doctor(workspace)
    verify_result = verify(workspace)
    gap_result = gap_meter(workspace)
    replay_result = replay(workspace)
    return {
        'workspace': str(workspace),
        'doctor': doctor_result,
        'verify': verify_result,
        'gap_meter': gap_result,
        'replay': replay_result,
    }


def run_demo_action(workspace: Path) -> dict:
    init_workspace(workspace)
    scorecard = run_demo(workspace)
    return {
        'action': 'run_demo',
        'result': scorecard,
    }
