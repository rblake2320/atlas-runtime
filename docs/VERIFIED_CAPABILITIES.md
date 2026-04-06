# Verified Capabilities

Snapshot date: 2026-04-06

This document lists only the Atlas capabilities that have been verified in the
source workspace with files, commands, and reports.

## Verified Runtime Surfaces

- Durable task records and task history.
- Event spine with chained hashes.
- Scorecard generation and recomputation.
- Budget tracking.
- Optional worktree isolation surface.
- Gap registry with owners, baselines, targets, verifier commands, and evidence
  paths.
- A2A directory and cards.
- MCP registry data.
- SDK registry and contracts.
- Wiring, schema, SDK, and code-inspection audits.
- Failure-injection audit.
- Agent activity audit.
- Claim freshness audit.

## Verified Evidence

- `business_doctor.py` passes.
- `business_full_validation.py run` passes after the validation ordering fix.
- `business_claim_audit.py` passes with fresh claims.
- `business_event_audit.py` passes and reports an intact hash chain.
- `business_wiring_audit.py` passes.
- `business_schema_audit.py` passes.
- `business_sdk_audit.py` passes.
- `business_code_inspector.py` passes.
- `business_failure_injection.py` passes.
- `business_agent_activity_audit.py` passes.
- `business_gap_meter.py status` reports a live gap count and progress value.

## Verified Claims Snapshot

- Scorecard: `95/100`
- Status: `production_ready`
- Doctor: `PASS`
- Full validation: `PASS`
- Event rigor: `PASS`
- Gap meter: live and measurable
- Claims: fresh at the time of the latest audit

## Verified Design Traits

- Claims are written to files.
- Audits write report artifacts.
- Validation can be recomputed.
- The workspace exposes what is still open instead of hiding it.
- The system distinguishes between verified state and open work.

## What This Does Not Prove

- It does not prove 24h+ uninterrupted autonomy on the wrapper side.
- It does not prove external revenue.
- It does not prove learning compounding from repeated use.
- It does not prove the wrapper package is installable yet.
- It does not prove the public CLI/MCP entrypoints exist yet.
