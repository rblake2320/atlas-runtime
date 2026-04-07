# Atlas Runtime Wrapper

This repository contains the initial installable Atlas runtime wrapper.
It exposes a CLI, a read-only MCP-style surface, and a small event-sourced
workspace model built from verified Atlas capabilities.

## Verified In This Repo

- `atlas` CLI entrypoint is present.
- The package installs in editable mode with `pip install -e .`.
- The MCP surface exposes read-only `doctor`, `status`, and `gap_meter` tools.
- The event spine is append-only and tamper-evident.
- The wrapper can initialize a workspace, run a demo pipeline, replay events,
  and produce truth-oriented reports.
- The test suite passes on Windows.

## Verified Atlas Source Capabilities Used By The Wrapper

Snapshot date: 2026-04-06

- Durable task-and-evidence workspace.
- Event spine with chained hashes.
- Doctor, full validation, claim audit, wiring audit, schema audit, SDK audit,
  code inspector, failure injection, and agent activity audit.
- Explicit gap owners with baselines, targets, verifier commands, and evidence
  paths.
- Budget and worktree surfaces.
- A2A cards, MCP registry data, and SDK registry data.
- Evidence-backed reports for score, runtime, and validation.

See:
- [Verified capabilities](docs/VERIFIED_CAPABILITIES.md)
- [Open gaps](docs/OPEN_GAPS.md)

## Current Wrapper Surface

The wrapper is intentionally small and truthful:

- `atlas init`
- `atlas doctor`
- `atlas verify`
- `atlas gap-meter`
- `atlas replay`
- `atlas run-demo`
- `atlas mcp serve`

## Truth Rules

- Only verified behavior belongs in the claim set.
- If a capability is not backed by a file, command, or report, it belongs in
  [Open gaps](docs/OPEN_GAPS.md).
- Freshness matters. Claims should be revalidated, not assumed.
- No mocks should count toward production claims.
- No human relay should be counted as autonomous interop.

## Current Repo State

This repo is version controlled and currently has the first working wrapper
implementation committed.
The remaining work is productization, not a rewrite.
