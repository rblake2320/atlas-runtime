from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib import request

from atlas_runtime.core.runtime import init_workspace, read_tasks, verify
from atlas_runtime.platform.backends import backend_status


class AdapterError(RuntimeError):
    pass


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
    req = request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json", **(headers or {})},
        method='POST',
    )
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))


def _atlas_local_response(root: Path, prompt: str, system: str | None = None) -> dict[str, Any]:
    verification = verify(root)
    tasks = read_tasks(root)
    delivered = sum(1 for task in tasks if task.get('status') == 'delivered')
    content = (
        f"atlas_local responded to the prompt using verified workspace state. "
        f"Delivered tasks: {delivered}. "
        f"Current wrapper status: {verification['status']}. "
        f"Open gaps: {len(verification['open_gaps'])}. "
        f"Prompt: {prompt}"
    )
    if system:
        content = f"System: {system}\n{content}"
    return {
        "status": "PASS",
        "backend": "atlas_local",
        "provider_verified": True,
        "content": content,
    }


def _openai_like(prompt: str, system: str | None = None) -> dict[str, Any]:
    base_url = os.getenv('ATLAS_OPENAI_BASE_URL')
    api_key = os.getenv('ATLAS_OPENAI_API_KEY')
    model = os.getenv('ATLAS_OPENAI_MODEL')
    if not all([base_url, api_key, model]):
        raise AdapterError('openai_compatible backend is not fully configured')
    payload = {
        "model": model,
        "messages": ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}],
    }
    data = _post_json(f"{base_url.rstrip('/')}/chat/completions", payload, headers={"Authorization": f"Bearer {api_key}"})
    return {
        "status": "PASS",
        "backend": "openai_compatible",
        "provider_verified": False,
        "content": data["choices"][0]["message"]["content"],
    }


def _anthropic_like(prompt: str, system: str | None = None) -> dict[str, Any]:
    base_url = os.getenv('ATLAS_ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1/messages')
    api_key = os.getenv('ATLAS_ANTHROPIC_API_KEY')
    model = os.getenv('ATLAS_ANTHROPIC_MODEL')
    if not all([base_url, api_key, model]):
        raise AdapterError('anthropic_compatible backend is not fully configured')
    payload = {
        "model": model,
        "max_tokens": 512,
        "system": system or '',
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _post_json(base_url, payload, headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"})
    first = data.get('content', [{}])[0]
    return {
        "status": "PASS",
        "backend": "anthropic_compatible",
        "provider_verified": False,
        "content": first.get('text', ''),
    }


def _gemini_like(prompt: str, system: str | None = None) -> dict[str, Any]:
    base_url = os.getenv('ATLAS_GEMINI_BASE_URL')
    api_key = os.getenv('ATLAS_GEMINI_API_KEY')
    model = os.getenv('ATLAS_GEMINI_MODEL')
    if not all([base_url, api_key, model]):
        raise AdapterError('gemini_compatible backend is not fully configured')
    payload = {
        "system_instruction": {"parts": [{"text": system or ''}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    data = _post_json(f"{base_url.rstrip('/')}/models/{model}:generateContent?key={api_key}", payload)
    content = data['candidates'][0]['content']['parts'][0]['text']
    return {
        "status": "PASS",
        "backend": "gemini_compatible",
        "provider_verified": False,
        "content": content,
    }


def _ollama_like(prompt: str, system: str | None = None) -> dict[str, Any]:
    base_url = os.getenv('ATLAS_OLLAMA_BASE_URL')
    model = os.getenv('ATLAS_OLLAMA_MODEL')
    if not all([base_url, model]):
        raise AdapterError('ollama_http backend is not fully configured')
    payload = {
        "model": model,
        "messages": ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}],
        "stream": False,
    }
    data = _post_json(f"{base_url.rstrip('/')}/api/chat", payload)
    return {
        "status": "PASS",
        "backend": "ollama_http",
        "provider_verified": False,
        "content": data['message']['content'],
    }


def chat(root: Path, prompt: str, system: str | None = None) -> dict[str, Any]:
    init_workspace(root)
    active = backend_status(root).get('active')
    if active is None:
        return {"status": "FAIL", "reason": "no_active_backend"}
    kind = active.get('kind')
    try:
        if kind == 'builtin':
            return _atlas_local_response(root, prompt, system)
        if kind == 'openai_compatible':
            return _openai_like(prompt, system)
        if kind == 'anthropic_compatible':
            return _anthropic_like(prompt, system)
        if kind == 'gemini_compatible':
            return _gemini_like(prompt, system)
        if kind == 'ollama_http':
            return _ollama_like(prompt, system)
        return {"status": "FAIL", "reason": "unsupported_backend", "backend": active.get('id')}
    except AdapterError as exc:
        return {"status": "FAIL", "reason": str(exc), "backend": active.get('id')}
