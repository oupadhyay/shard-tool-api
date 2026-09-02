#!/usr/bin/env python3
"""Fail when shard-tool-api's dependency boundary changes unexpectedly."""

import json
import subprocess
import sys


PACKAGE = "shard-tool-api"
EXPECTED_REPOSITORY = "https://github.com/oupadhyay/shard-tool-api"
EXPECTED_DIRECT_DEPENDENCIES = {"serde", "serde_json"}
FORBIDDEN_GRAPH_PACKAGES = {
    "diesel",
    "reqwest",
    "rusqlite",
    "sea-orm",
    "shard-external-tools",
    "shard-provider",
    "shard-v2",
    "sqlx",
    "tauri",
    "tauri-build",
    "tokio",
}


def fail(message: str) -> None:
    print(f"dependency boundary audit failed: {message}", file=sys.stderr)
    raise SystemExit(1)


metadata = json.loads(
    subprocess.run(
        ["cargo", "metadata", "--locked", "--format-version", "1"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
)

roots = [
    package
    for package in metadata["packages"]
    if package["name"] == PACKAGE and package["source"] is None
]
if len(roots) != 1:
    fail(f"expected one local {PACKAGE} package, found {len(roots)}")

direct_dependencies = {dependency["name"] for dependency in roots[0]["dependencies"]}
if direct_dependencies != EXPECTED_DIRECT_DEPENDENCIES:
    fail(
        "direct dependencies changed; expected "
        f"{sorted(EXPECTED_DIRECT_DEPENDENCIES)}, found {sorted(direct_dependencies)}"
    )

graph_packages = {package["name"] for package in metadata["packages"]}
forbidden = sorted(graph_packages & FORBIDDEN_GRAPH_PACKAGES)
if forbidden:
    fail(f"forbidden packages entered the graph: {forbidden}")

git_sources = sorted(
    package["source"]
    for package in metadata["packages"]
    if package["source"] and package["source"].startswith("git+")
)
if git_sources:
    fail(f"leaf crate must not use Git dependencies: {git_sources}")

if roots[0]["publish"] != []:
    fail("Cargo.toml must keep publish = false")
if roots[0]["repository"] != EXPECTED_REPOSITORY:
    fail(f"repository metadata must be {EXPECTED_REPOSITORY}")
if roots[0]["readme"] != "README.md":
    fail("Cargo.toml must name the repository README")
if roots[0]["license"] is not None or roots[0]["license_file"] is not None:
    fail("no license has been selected; update the documented policy before adding one")

print("dependency boundary audit passed")
