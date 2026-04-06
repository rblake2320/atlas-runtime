# Testing Atlas Runtime Wrapper

This repository is the wrapper contract and test plan.
The current repo state is docs-only, so the real executable proof still lives in
the Atlas source workspace until the wrapper code lands here.

## What Must Be Tested

- The Atlas source capabilities that the wrapper will expose.
- The wrapper CLI surface once it exists.
- The wrapper MCP surface once it exists.
- The event spine and replay path.
- The claim freshness and evidence regeneration path.
- The audit chain: doctor, wiring, schema, SDK, code inspector, failure
  injection, agent activity.

## Source Verification Commands

Run these against the Atlas workspace when you want to verify the proven
capabilities that this wrapper should inherit:

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

## Expected Truthful Results

The wrapper should only promote claims that are already verified in Atlas.
At minimum, the test output should be able to prove:

- the event chain is intact
- the scorecard is recomputable
- claims are fresh
- audits pass
- evidence files exist
- the remaining gaps are still visible and not hidden

## Wrapper Acceptance Criteria

When the wrapper code lands, the repo should support at least:

- `atlas init`
- `atlas doctor`
- `atlas verify`
- `atlas gap-meter`
- `atlas replay`
- `atlas mcp serve`

The test plan for those commands should cover:

- exit code
- stdout/stderr
- generated evidence files
- timestamp freshness
- version control cleanliness

## Non-Negotiables

- Do not count mock results as proof.
- Do not count stale reports as current claims.
- Do not count chat statements as evidence unless they are backed by a file or
  command output.
- Do not claim the wrapper is complete until the wrapper commands actually run.
