import json
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> dict:
    cmd = [sys.executable, "-m", "atlas_runtime.cli", *args]
    result = subprocess.run(cmd, cwd=REPO, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def test_cli_init_doctor_and_gap_meter(tmp_path: Path) -> None:
    target = tmp_path / "cli-workspace"
    init_result = run_cli("init", str(target))
    assert init_result["status"] == "PASS"
    doctor_result = run_cli("doctor", str(target))
    assert doctor_result["status"] == "PASS"
    gap_result = run_cli("gap-meter", str(target))
    assert gap_result["gap_count"] >= 1
