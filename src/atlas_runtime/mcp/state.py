from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from atlas_runtime.core.runtime import doctor as wrapper_doctor
from atlas_runtime.core.runtime import gap_meter as wrapper_gap_meter
from atlas_runtime.core.runtime import verify as wrapper_verify


def _load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding='utf-8'))


def _atlas_gap_meter(root: Path) -> dict[str, Any]:
    gaps = _load_json(root / 'Team' / 'runtime' / 'state' / 'gaps.json', {'gaps': []}).get('gaps', [])
    report_path = root / "Owner's Inbox" / 'reports' / 'ATLAS-GAP-METER.md'
    overall = None
    if report_path.exists():
        match = re.search(r'Overall progress: ([0-9.]+)%', report_path.read_text(encoding='utf-8'))
        if match:
            overall = float(match.group(1))
    if overall is None:
        values = []
        for gap in gaps:
            target = max(float(gap.get('target', 0) or 0), 1.0)
            current = float(gap.get('current', 0) or 0)
            values.append(min(100.0, (current / target) * 100.0))
        overall = round(sum(values) / len(values), 1) if values else 0.0
    return {
        'gap_count': len(gaps),
        'overall_progress_pct': overall,
        'active': sum(1 for gap in gaps if gap.get('status') == 'active'),
        'verified': sum(1 for gap in gaps if gap.get('status') == 'verified'),
        'gaps': gaps,
    }


def _atlas_snapshot(root: Path) -> dict[str, Any]:
    scorecard = _load_json(root / 'Team' / 'runtime' / 'state' / 'scorecard.json')
    doctor = _load_json(root / "Owner's Inbox" / 'reports' / 'ATLAS-DOCTOR.json')
    claims = _load_json(root / "Owner's Inbox" / 'reports' / 'ATLAS-CLAIMS.json')
    gap_meter = _atlas_gap_meter(root)
    status = {
        'status': 'PASS' if doctor.get('status') == 'PASS' and claims.get('status') == 'PASS' else 'FAIL',
        'scorecard': scorecard,
        'doctor': doctor,
        'claims': claims,
        'gap_meter': gap_meter,
    }
    return {
        'doctor': doctor,
        'status': status,
        'gap_meter': gap_meter,
    }


def _wrapper_snapshot(root: Path) -> dict[str, Any]:
    return {
        'doctor': wrapper_doctor(root),
        'status': wrapper_verify(root),
        'gap_meter': wrapper_gap_meter(root),
    }


def snapshot(workspace: Path) -> dict[str, Any]:
    if (workspace / 'Owner\'s Inbox').exists() and (workspace / 'Team' / 'runtime' / 'state' / 'scorecard.json').exists():
        return _atlas_snapshot(workspace)
    return _wrapper_snapshot(workspace)
