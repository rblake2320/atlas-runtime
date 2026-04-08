# Atlas Runtime

`atlas-runtime` is a public agent-platform wrapper around the proven Atlas runtime surfaces.

It is no longer just a dashboard shell:
- installable Python package
- truthful local dashboard UI
- append-only event spine with replay verification
- backend registry with one verified local backend and adapter-ready external backends
- tool catalog with real execution against workspace state
- agent registry with owner-aware workers
- deterministic multi-agent loop tick
- read-only MCP-like server for doctor/status/gap inspection

## Verified now
- standalone workspace bootstrap
- append-only event log with hash-chain verification
- dependency-aware demo pipeline with durable evidence
- `doctor`, `verify`, `gap-meter`, `interop-replay`, `tool`, `agent`, `backend`, `loop`, and `chat` commands
- owner-aware multi-agent local execution through the verified `atlas_local` backend
- local dashboard UI for status, replay, tasks, agents, and gaps
- read-only MCP-like HTTP server exposing doctor/status/gap tools
- portable test suite that passes from a clean clone

## Verified limits
- only `atlas_local` is currently provider-verified
- external backends are adapter-ready, not yet provider-verified
- the wrapper is still deterministic and policy-first, not model-parity with Claude/ChatGPT/Gemini

## Not yet proven
- 24h+ autonomous runtime
- non-zero learning-proof deltas
- non-zero external-value wins
- heterogeneous external provider orchestration under live credentials
- broad extension ecosystem
- public release workflow or package publishing

## Install
```powershell
cd atlas-runtime-repo
pip install -e .
```

## 5-minute path
```powershell
atlas init demo-workspace
atlas backend status demo-workspace
atlas agent list demo-workspace
atlas run-demo demo-workspace
atlas chat demo-workspace "summarize current runtime state"
atlas loop once demo-workspace
atlas doctor demo-workspace
atlas verify demo-workspace
atlas interop-replay demo-workspace
atlas gap-meter demo-workspace
atlas ui demo-workspace --host 127.0.0.1 --port 8788
```

## Backend model
- `atlas_local` is the only verified execution backend today.
- `openai_compatible`, `anthropic_compatible`, `gemini_compatible`, and `ollama_http` are real adapters with CLI routing, but they are not counted as proven until exercised with live credentials and audited results.

## Why this exists
The original Atlas workspace proved the governance and validation model. This wrapper makes the proven parts runnable by strangers without asking them to understand the whole internal workspace, while still refusing to overclaim model capability that has not yet been verified.
