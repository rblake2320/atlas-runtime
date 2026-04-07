# Atlas Runtime

`atlas-runtime` is the public wrapper around the proven Atlas runtime surfaces.

It is intentionally small:
- installable Python package
- one CLI entry point
- one local dashboard UI
- one read-only MCP-like server
- append-only event spine with deterministic replay
- truthful verification that separates verified capabilities from open gaps

## Verified now
- standalone workspace bootstrap
- append-only event log with hash-chain verification
- dependency-aware demo pipeline
- `doctor`, `verify`, `gap-meter`, `interop-replay`, and `ui` commands
- local dashboard UI for status, replay, and gap inspection
- read-only MCP-like HTTP server exposing doctor/status tools
- portable test suite that passes from a clean clone

## Not yet proven
- 24h+ autonomous runtime
- non-zero learning-proof deltas
- non-zero external-value wins
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
atlas run-demo demo-workspace
atlas doctor demo-workspace
atlas verify demo-workspace
atlas interop-replay demo-workspace
atlas gap-meter demo-workspace
atlas ui demo-workspace --host 127.0.0.1 --port 8788
```

## UI
`atlas ui` launches a local dashboard with:
- doctor status
- verify status
- gap meter
- replay summary
- one-click demo execution

## MCP surface
```powershell
atlas mcp serve demo-workspace --host 127.0.0.1 --port 8766
```

Then browse or fetch:
- `/tools`
- `/tools/doctor`
- `/tools/gap-meter`
- `/tools/status`

## Atlas-source mode
The MCP server can also read a full Atlas workspace if you point it at one, but the published test suite does not require that local workspace.

## Why this exists
The original Atlas workspace proved the governance and validation model. This wrapper makes the proven parts runnable by strangers without asking them to understand the whole internal workspace.
