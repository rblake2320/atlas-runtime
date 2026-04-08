from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from atlas_runtime.core.runtime import dump_json, load_json, init_workspace, workspace_paths


DEFAULT_BACKENDS = {
    "active_backend": "atlas_local",
    "backends": [
        {
            "id": "atlas_local",
            "kind": "builtin",
            "description": "Deterministic local orchestration backend used for truthful wrapper execution.",
            "configured": True,
            "verified": True,
            "status": "ready",
            "capabilities": ["tool_use", "task_orchestration", "deterministic_replay"],
        },
        {
            "id": "openai_compatible",
            "kind": "openai_compatible",
            "description": "OpenAI-compatible chat/completions endpoint.",
            "configured": False,
            "verified": False,
            "status": "not_configured",
            "env": ["ATLAS_OPENAI_BASE_URL", "ATLAS_OPENAI_API_KEY", "ATLAS_OPENAI_MODEL"],
        },
        {
            "id": "anthropic_compatible",
            "kind": "anthropic_compatible",
            "description": "Anthropic-style messages endpoint.",
            "configured": False,
            "verified": False,
            "status": "not_configured",
            "env": ["ATLAS_ANTHROPIC_BASE_URL", "ATLAS_ANTHROPIC_API_KEY", "ATLAS_ANTHROPIC_MODEL"],
        },
        {
            "id": "gemini_compatible",
            "kind": "gemini_compatible",
            "description": "Gemini-style generateContent endpoint.",
            "configured": False,
            "verified": False,
            "status": "not_configured",
            "env": ["ATLAS_GEMINI_BASE_URL", "ATLAS_GEMINI_API_KEY", "ATLAS_GEMINI_MODEL"],
        },
        {
            "id": "ollama_http",
            "kind": "ollama_http",
            "description": "Local Ollama-compatible HTTP backend.",
            "configured": False,
            "verified": False,
            "status": "not_configured",
            "env": ["ATLAS_OLLAMA_BASE_URL", "ATLAS_OLLAMA_MODEL"],
        },
    ],
}


def _file(root: Path) -> Path:
    return workspace_paths(root).backends_file


def _apply_env_state(backends: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for backend in backends:
        row = dict(backend)
        if row["kind"] != "builtin":
            required = row.get("env", [])
            configured = all(os.getenv(name) for name in required)
            row["configured"] = configured
            row["status"] = "configured" if configured else "not_configured"
        rows.append(row)
    return rows


def ensure_backends(root: Path) -> dict[str, Any]:
    init_workspace(root)
    path = _file(root)
    if not path.exists():
        dump_json(path, DEFAULT_BACKENDS)
    data = load_json(path, DEFAULT_BACKENDS)
    data["backends"] = _apply_env_state(data.get("backends", []))
    dump_json(path, data)
    return data


def list_backends(root: Path) -> dict[str, Any]:
    data = ensure_backends(root)
    return {
        "status": "PASS",
        "active_backend": data.get("active_backend", "atlas_local"),
        "count": len(data.get("backends", [])),
        "backends": data.get("backends", []),
    }


def set_active_backend(root: Path, backend_id: str) -> dict[str, Any]:
    data = ensure_backends(root)
    backends = data.get("backends", [])
    match = next((row for row in backends if row["id"] == backend_id), None)
    if match is None:
        return {"status": "FAIL", "reason": "unknown_backend", "backend_id": backend_id}
    if not match.get("configured"):
        return {"status": "FAIL", "reason": "backend_not_configured", "backend_id": backend_id}
    data["active_backend"] = backend_id
    dump_json(_file(root), data)
    return {"status": "PASS", "active_backend": backend_id}


def backend_status(root: Path) -> dict[str, Any]:
    data = ensure_backends(root)
    backends = data.get("backends", [])
    active = next((row for row in backends if row["id"] == data.get("active_backend")), None)
    ready = sum(1 for row in backends if row.get("configured"))
    return {
        "status": "PASS",
        "active_backend": data.get("active_backend"),
        "ready_backends": ready,
        "count": len(backends),
        "active": active,
        "backends": backends,
    }

