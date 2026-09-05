# shard-tool-api Repository Guidance

## Purpose

`shard-tool-api` is the smallest shared Rust boundary in the Shard project. It
defines provider-neutral tool metadata and invocation contracts that can be
used by the host, provider request builders, MCP adapters, and portable tool
executors without coupling those layers together.

Sibling repositories:

- [`shard-v2`](https://github.com/oupadhyay/shard-v2) — desktop host and UI.
- [`shard-external-tools`](https://github.com/oupadhyay/shard-external-tools) —
  host-free external tool implementations.
- [`shard-provider`](https://github.com/oupadhyay/shard-provider) — host-free
  provider wire contracts and transports.

## Ownership

This repository owns only stable, provider-neutral contracts such as
`ToolDefinition`, `FunctionDefinition`, and borrowed invocation input. It owns
their serde wire shape and focused round-trip tests.

It does **not** own:

- tool registry/catalog composition, availability, hooks, caching, approval
  gates, execution, or result rendering;
- provider-specific DTOs, HTTP clients, streaming, credentials, or endpoints;
- Tauri commands/events, SQLite or other persistence, sessions, memory,
  personas, model selection, retry/fallback logic, or workflow policy.

If a proposed type needs host state, network access, a provider concept, or
tool implementation behavior, it belongs in another repository.

## Dependency Rules

The one-way graph is:

```text
shard-v2 ──> shard-tool-api
    ├──────> shard-external-tools ──> shard-tool-api
    └──────> shard-provider ─────────> shard-tool-api
```

`shard-tool-api` is a leaf boundary and must not depend on any sibling
repository. Keep its dependency set limited to libraries required to express
and serialize neutral contracts. In particular, do not add Tauri, reqwest,
Tokio, database crates, provider SDKs, or external-tool implementations.

`shard-provider` and `shard-external-tools` must never depend on each other.

## Build and Validation

Run from the repository root:

```bash
cargo fmt --all -- --check
cargo check --locked --all-targets
cargo test --locked --all-targets
cargo clippy --locked --all-targets -- -D warnings
RUSTDOCFLAGS="-D warnings" cargo doc --locked --no-deps
cargo tree --locked -e normal
cargo tree --locked -d
python3 scripts/audit_dependency_boundary.py
```

Contract changes require focused serialization/deserialization tests. Treat a
field rename, serde attribute change, or public-type change as a cross-repo API
change even if this crate's own tests pass.

## Updating Cross-Repository Revisions

This leaf repository does not pin sibling revisions. After merging a contract
change, record its immutable Git commit SHA and update all consumers in a
coordinated sequence:

1. update `shard-provider` and `shard-external-tools` to the same
   `shard-tool-api` revision;
2. validate and merge those standalone changes;
3. update `shard-v2` and regenerate its Cargo lockfile;
4. run `cargo tree -i shard-tool-api` in every consumer and confirm exactly one
   source/revision is present in the host graph.

Never mix path and Git copies in one host build: Rust treats their otherwise
identical public types as different nominal types.

The standalone cutover completed in
[`shard-v2` PR #123](https://github.com/oupadhyay/shard-v2/pull/123), initially
using this repository at `aea826a9e64b3035843aa8800f2f6c0f5fbe8b9a`.
Always use the host's
[`Cargo.toml`](https://github.com/oupadhyay/shard-v2/blob/main/src-tauri/Cargo.toml)
and
[`Cargo.lock`](https://github.com/oupadhyay/shard-v2/blob/main/src-tauri/Cargo.lock)
as the authoritative record of active pins; a docs-only sibling HEAD is not
necessarily consumed. Future portable changes remain standalone-first, then
require an explicit pinned host update and lockfile validation.

## Host GUI Regression Matrix

This crate has no GUI. Validate changed contracts in `shard-v2` through the
real Tauri application, not only unit tests. At minimum exercise normal
streaming chat plus a provider tool call and confirm the tool-call event,
execution, and rendered output. If the changed contract affects external tool
dispatch, also smoke-test one external tool; for YouTube-related metadata,
check short/long transcript behavior and heartbeat restrictions.

Changes that cannot affect wire shape or dispatch may document why host GUI
validation is unnecessary; do not claim a GUI check that was not run.
