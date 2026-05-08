#!/usr/bin/env python3
"""Classify the schema delta between two OpenAPI files as major/minor/none.

Wraps `openapi-changes report` and reduces its output to a single semver level
plus a markdown summary suitable for posting as a PR comment.

Usage:
    python scripts/classify_semver.py <base.yaml> <head.yaml>

Outputs JSON to stdout:
    {"level": "major|minor|none", "comment": "<markdown>"}

Exit code is always 0 — gating happens in the CI workflow based on the level.
"""

import json
import shutil
import subprocess
import sys
from typing import Any

LEVEL_LABELS = {
    "major": "🔴 MAJOR — breaking changes",
    "minor": "🟢 MINOR — non-breaking additions",
    "none": "⚪ NONE — no schema changes",
}


def run_openapi_changes(base: str, head: str) -> list[dict[str, Any]]:
    if shutil.which("openapi-changes") is None:
        raise RuntimeError("openapi-changes not found on PATH")
    result = subprocess.run(
        ["openapi-changes", "report", "--no-logo", "--reproducible", base, head],
        capture_output=True,
        text=True,
    )
    if not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return data.get("changes", [])


def classify(changes: list[dict[str, Any]]) -> str:
    if any(c.get("breaking") for c in changes):
        return "major"
    if changes:
        return "minor"
    return "none"


def render_comment(level: str, changes: list[dict[str, Any]]) -> str:
    breaking = [c for c in changes if c.get("breaking")]
    others = [c for c in changes if not c.get("breaking")]

    lines = [
        "<!-- semver-classification -->",
        f"## {LEVEL_LABELS[level]}",
        "",
        "Generated from `openapi-changes` against the base branch.",
        "",
    ]

    if breaking:
        lines += ["### Breaking changes"]
        for c in breaking:
            path = c.get("path", "")
            text = c.get("changeText", "").replace("_", " ")
            old = c.get("old", "")
            new = c.get("new", "")
            detail = f"{old} → {new}" if old and new else (new or old)
            lines.append(f"- **{path}** — {text}" + (f": {detail}" if detail else ""))
        lines.append("")

    if others:
        lines += ["### Non-breaking changes"]
        for c in others:
            path = c.get("path", "")
            text = c.get("changeText", "").replace("_", " ")
            lines.append(f"- {path} — {text}")
        lines.append("")

    if not changes:
        lines += ["No schema-level changes detected against the base branch."]
        lines.append("")

    if level == "major":
        lines += [
            "---",
            "⚠️ If this break is intentional, signal it with `feat!:` or `fix!:` in the PR title.",
            "release-please will bump the major version on the next release.",
        ]

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: classify_semver.py <base.yaml> <head.yaml>", file=sys.stderr)
        sys.exit(2)
    base, head = sys.argv[1], sys.argv[2]
    changes = run_openapi_changes(base, head)
    level = classify(changes)
    print(json.dumps({"level": level, "comment": render_comment(level, changes)}))


if __name__ == "__main__":
    main()
