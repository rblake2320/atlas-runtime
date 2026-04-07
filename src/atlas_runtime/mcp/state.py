from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_ATLAS_ROOT = Path(os.getenv("ATLAS_RUNTIME_ROOT", r"C:\Users\techai\Desktop\Atlas Autonomous Group"))


@dataclass(frozen=True)
class AtlasState:
    atlas_root: Path
    scorecard: dict[str, Any]
    doctor: dict[str, Any]
    claims: dict[str, Any]
    gap_meter: dict[str, Any]
    gaps: dict[str, Any]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def resolve_atlas_root(atlas_root: str | Path | None = None) -> Path:
    root = Path(atlas_root) if atlas_root is not None else DEFAULT_ATLAS_ROOT
    if not root.exists():
        raise FileNotFoundError(f"Atlas root not found: {root}")
    return root


def load_atlas_state(atlas_root: str | Path | None = None) -> AtlasState:
    root = resolve_atlas_root(atlas_root)
    reports = root / "Owner's Inbox" / "reports"
    runtime = root / "Team" / "runtime" / "state"
    scorecard = _read_json(runtime / "scorecard.json")
    doctor = _read_json(reports / "ATLAS-DOCTOR.json")
    claims = _read_json(reports / "ATLAS-CLAIMS.json")
    gap_meter = _read_text(reports / "ATLAS-GAP-METER.md")
    gaps = _read_json(runtime / "gaps.json")
    gap_meter_summary = summarize_gaps(gaps)
    if gap_meter_summary:
        gap_meter_summary["source"] = str(reports / "ATLAS-GAP-METER.md")
    return AtlasState(
        atlas_root=root,
        scorecard=scorecard,
        doctor=doctor,
        claims=claims,
        gap_meter=gap_meter_summary,
        gaps=gaps,
    )


def summarize_gaps(gaps_doc: dict[str, Any]) -> dict[str, Any]:
    gaps = gaps_doc.get("gaps", []) if isinstance(gaps_doc, dict) else []
    active = [gap for gap in gaps if gap.get("status") == "active"]
    verified = [gap for gap in gaps if gap.get("status") == "verified"]
    progress = 0.0
    if gaps:
        total = 0.0
        earned = 0.0
        for gap in gaps:
            target = float(gap.get("target", 0) or 0)
            current = float(gap.get("current", 0) or 0)
            if target > 0:
                total += 1.0
                earned += max(0.0, min(1.0, current / target))
        progress = round((earned / total) * 100.0, 1) if total else 0.0
    return {
        "gap_count": len(gaps),
        "overall_progress_pct": progress,
        "active": len(active),
        "verified": len(verified),
        "gaps": gaps,
    }


def summarize_state(state: AtlasState) -> dict[str, Any]:
    scorecard = state.scorecard
    doctor = state.doctor
    claims = state.claims
    gap_meter = state.gap_meter
    return {
        "atlas_root": str(state.atlas_root),
        "scorecard": {
            "status": scorecard.get("status"),
            "score": scorecard.get("score"),
            "delivered": scorecard.get("delivered"),
            "evidence_coverage": scorecard.get("evidence_coverage"),
        },
        "doctor": {
            "status": doctor.get("status"),
            "checks": doctor.get("checks"),
        },
        "claims": {
            "status": claims.get("status"),
            "count": len(claims.get("claims", [])) if isinstance(claims, dict) else 0,
        },
        "gap_meter": {
            "gap_count": gap_meter.get("gap_count", 0),
            "overall_progress_pct": gap_meter.get("overall_progress_pct", 0.0),
            "active": gap_meter.get("active", 0),
            "verified": gap_meter.get("verified", 0),
        },
        "version_control": {
            "local_state": "git-tracked",
            "claims_source": "proven Atlas reports",
        },
    }


def gap_details(state: AtlasState) -> dict[str, Any]:
    gaps = state.gap_meter.get("gaps", []) if isinstance(state.gap_meter, dict) else []
    return {
        "atlas_root": str(state.atlas_root),
        "gap_count": state.gap_meter.get("gap_count", 0),
        "overall_progress_pct": state.gap_meter.get("overall_progress_pct", 0.0),
        "active": state.gap_meter.get("active", 0),
        "verified": state.gap_meter.get("verified", 0),
        "gaps": gaps,
    }
