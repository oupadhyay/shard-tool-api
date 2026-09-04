# shard-tool-api

`shard-tool-api` is the smallest shared Rust boundary in the Shard project. It
contains provider-neutral tool definitions and borrowed invocation inputs used
by the desktop host, provider transports, MCP adapters, and portable tool
executors.

It deliberately does not own tool execution, provider transports, host state,
credentials, persistence, UI events, retries, fallback behavior, or workflow
policy. See [AGENTS.md](AGENTS.md) for the complete ownership rules and host GUI
regression expectations.

## Repository graph

```text
shard-v2 ──> shard-tool-api
    ├──────> shard-external-tools ──> shard-tool-api
    └──────> shard-provider ─────────> shard-tool-api
```

Sibling repositories:

- [`shard-v2`](https://github.com/oupadhyay/shard-v2) — Tauri desktop host and UI
- [`shard-external-tools`](https://github.com/oupadhyay/shard-external-tools) — host-free external tools
- [`shard-provider`](https://github.com/oupadhyay/shard-provider) — host-free provider transports

`shard-tool-api` is a leaf and must not depend on any sibling repository.
`shard-provider` and `shard-external-tools` must never depend on each other.

## Consumption and releases

This crate is distributed from GitHub, not crates.io. Consumers must pin a
reviewed, immutable 40-character commit SHA:

```toml
[dependencies]
shard-tool-api = { git = "https://github.com/oupadhyay/shard-tool-api", rev = "<reviewed-commit-sha>" }
```

Keep all consumers on the same revision. Mixing path and Git sources—or two Git
revisions—creates distinct nominal Rust types even when their source is
identical. `publish = false` in `Cargo.toml` intentionally prevents accidental
crates.io publication.

## Host cutover status

The standalone-crate cutover was completed in
[`shard-v2` PR #123](https://github.com/oupadhyay/shard-v2/pull/123). The
initial host cutover consumed `shard-tool-api` revision
`aea826a9e64b3035843aa8800f2f6c0f5fbe8b9a`. The authoritative record of the
revisions currently consumed by the host is the host's
[`Cargo.toml`](https://github.com/oupadhyay/shard-v2/blob/main/src-tauri/Cargo.toml)
and resolved
[`Cargo.lock`](https://github.com/oupadhyay/shard-v2/blob/main/src-tauri/Cargo.lock),
not this documentation branch or this repository's current HEAD.

Future portable contract changes must be merged and validated here first.
Consumers must then pin the resulting immutable revision, followed by a pinned
host dependency update and lockfile validation.

## Development

The repository pins its Rust toolchain in `rust-toolchain.toml` and commits
`Cargo.lock` so local and CI validation resolve the same dependency versions.

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

Contract or wire-shape changes also require integration testing through the
real `shard-v2` Tauri application as described in [AGENTS.md](AGENTS.md).

## License

No open-source license has been selected for this repository. All rights are
reserved. The absence of a license file is deliberate; availability of the
source does not grant permission to use, copy, modify, or distribute it.
