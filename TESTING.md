# Testing Atlas Runtime Wrapper

This repository is the wrapper contract and test plan.
The wrapper code exists and the suite is already passing; this file defines the
commands that should keep it honest as it evolves.

## Run This First

```powershell
python -m pip install -e .
python -m pytest
```

Expected result at the time of this snapshot:
- editable install succeeds
- `9` tests pass

## Wrapper Commands To Verify

```powershell
atlas init atlas-workspace
atlas doctor atlas-workspace
atlas verify atlas-workspace
atlas gap-meter atlas-workspace
atlas replay atlas-workspace
atlas run-demo atlas-workspace
atlas mcp serve atlas-workspace --host 127.0.0.1 --port 8766
```

## What Those Commands Must Prove

- `atlas init` creates a workspace with event state and evidence dirs.
- `atlas doctor` reports the truth-oriented health check.
- `atlas verify` reports the current verified capability snapshot.
- `atlas gap-meter` reports live gap progress.
- `atlas replay` verifies the event chain.
- `atlas run-demo` advances the small demo pipeline and writes evidence.
- `atlas mcp serve` exposes read-only `doctor`, `status`, and `gap_meter`
  tools.

## Source Verification Commands

Run these against the Atlas source workspace when you want to verify the
upstream capabilities that this wrapper reads from:

```powershell
python scripts\business_doctor.py
python scripts\business_full_validation.py run
python scripts\business_claim_audit.py
python scripts\business_event_audit.py
python scripts\business_wiring_audit.py
python scripts\business_schema_audit.py
python scripts\business_sdk_audit.py
python scripts\business_code_inspector.py
python scripts\business_failure_injection.py
python scripts\business_agent_activity_audit.py
python scripts\business_gap_meter.py status
```

## Non-Negotiables

- Do not count mock results as proof.
- Do not count stale reports as current claims.
- Do not count chat statements as evidence unless they are backed by a file or
  command output.
- Do not claim the wrapper is complete until the wrapper commands actually run.
