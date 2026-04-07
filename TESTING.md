# Testing

## Install
```powershell
pip install -e .
```

## Run tests
```powershell
pytest
```

The published test suite is portable. It does not depend on a local Atlas monorepo checkout.

## Manual verification
```powershell
atlas init demo-workspace
atlas run-demo demo-workspace
atlas doctor demo-workspace
atlas verify demo-workspace
atlas interop-replay demo-workspace
atlas gap-meter demo-workspace
atlas ui demo-workspace --host 127.0.0.1 --port 8788
python -m atlas_runtime.mcp demo-workspace --once
```

Expected truths:
- `atlas doctor` returns `PASS`
- `atlas verify` returns `PASS`
- `atlas interop-replay` returns `PASS`
- `atlas run-demo` delivers 3 seeded tasks
- `atlas gap-meter` shows non-zero progress and still-open gaps
- `atlas ui` launches a local dashboard
- `python -m atlas_runtime.mcp demo-workspace --once` returns doctor/status/gap meter JSON

## Optional Atlas-source verification
If you also have a full Atlas workspace locally, you can point the MCP snapshot mode at it:
```powershell
python -m atlas_runtime.mcp "C:\path\to\Atlas Autonomous Group" --once
```
That path is optional and is not part of the public test contract.
