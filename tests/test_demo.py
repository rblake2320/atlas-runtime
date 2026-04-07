from pathlib import Path

from atlas_runtime.core.runtime import doctor, init_workspace, replay, run_demo, verify


def test_demo_pipeline_and_verify(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    init_workspace(root)
    scorecard = run_demo(root)
    assert scorecard["delivered"] == 3
    assert doctor(root)["status"] == "PASS"
    assert verify(root)["status"] == "PASS"
    assert replay(root)["status"] == "PASS"
    assert (root / "evidence" / "AR-0003-release-verdict.md").exists()
