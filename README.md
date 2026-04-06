# Atlas Runtime Wrapper

This repository is the public wrapper scaffold for the Atlas runtime.

It is meant to become an installable, CLI-first, MCP-capable wrapper around the
proven Atlas workspace surfaces. This repo is docs-first for now: it states
what is verified, what is only a target, and what still needs to be built.

## What Is Verified In The Atlas Source

Snapshot date: 2026-04-06

- Atlas has a durable task-and-evidence workspace.
- Atlas has a real event spine with tamper-evident hashing.
- Atlas has a doctor, full validation, claim audit, wiring audit, schema audit,
  SDK audit, code inspector, failure injection, and agent activity audit.
- Atlas has explicit gap owners with baselines, targets, verifier commands, and
  evidence paths.
- Atlas has budget and worktree surfaces.
- Atlas has A2A cards, MCP registry data, and SDK registry data.
- Atlas has evidence-backed reports for score, runtime, and validation.

See:
- [Verified capabilities](docs/VERIFIED_CAPABILITIES.md)
- [Open gaps](docs/OPEN_GAPS.md)

## What This Wrapper Is Intended To Become

The wrapper should expose a small public surface:

- `atlas init`
- `atlas doctor`
- `atlas verify`
- `atlas gap-meter`
- `atlas replay`
- `atlas mcp serve`

The goal is not to hide Atlas behind branding. The goal is to make the proven
parts easy to install, run, verify, and review.

## Truth Rules

- Only verified behavior belongs in the wrapper claim set.
- If a capability is not backed by a file, command, or report, it belongs in
  [Open gaps](docs/OPEN_GAPS.md), not in marketing copy.
- Freshness matters. Claims should be revalidated, not assumed.
- No mocks should count toward production claims.
- No human relay should be counted as autonomous interop.

## Current Repo State

This repository currently contains docs only.
The code package, entrypoints, and release tooling still need to be added.

That is deliberate. The wrapper should be built from the verified Atlas
surfaces, not from assumptions.
