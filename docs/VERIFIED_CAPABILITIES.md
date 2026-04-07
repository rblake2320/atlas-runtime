# Verified Capabilities

Snapshot date: 2026-04-07

This document lists the capabilities that are verified in the wrapper repo or
in the Atlas source workspace that the wrapper reads from.

## Verified In This Wrapper Repo

- Installable package metadata in `pyproject.toml`.
- `atlas` console script entrypoint.
- Local dashboard UI served by `atlas ui`.
- Read-only MCP-style server with `doctor`, `status`, and `gap_meter` tools.
- Event store with append-only hash chain and witness file.
- Workspace initializer, demo pipeline, replay, and verify surfaces.
- Portable test suite that passes on Windows.

## Verified From The Atlas Source

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

## Verified Evidence Snapshot

- Wrapper tests: `10 passed`.
- Editable install: `PASS`.
- Atlas doctor: `PASS`.
- Atlas full validation: `PASS`.
- Atlas claim audit: `PASS`.
- Atlas event audit: `PASS`.
- Atlas wiring/schema/SDK/code-inspector audits: `PASS`.

## Verified Claims Snapshot

- Wrapper demo score: `95/100`
- Wrapper status: `production_ready`
- Wrapper UI launches locally
- Gap meter: live and measurable
- Claims: fresh at the time of the latest Atlas audit

## What This Does Not Prove

- It does not prove 24h+ uninterrupted autonomy on the wrapper side.
- It does not prove external revenue.
- It does not prove learning compounding from repeated use.
- It does not prove the wrapper is ready for a public release workflow yet.
