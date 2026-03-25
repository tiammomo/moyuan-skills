#!/usr/bin/env python3
"""Smoke check for the api-change-risk-review skill."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "api_change_risk_review.py"
BEFORE = ROOT / "assets" / "sample-before.json"
AFTER = ROOT / "assets" / "sample-after.json"
TEMPLATE = ROOT / "assets" / "api-change-risk-template.md"
REQUIRED_FILES = (
    ROOT / "SKILL.md",
    ROOT / "agents" / "openai.yaml",
    ROOT / "references" / "input-contract.md",
    ROOT / "references" / "risk-rules.md",
    ROOT / "references" / "review-checklist.md",
    BEFORE,
    AFTER,
    TEMPLATE,
    SCRIPT,
)


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT).as_posix()}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    with tempfile.TemporaryDirectory() as tmp_dir:
        diff_path = Path(tmp_dir) / "api-diff.json"
        draft_path = Path(tmp_dir) / "api-risk-review.md"

        diff_result = run_command([sys.executable, str(SCRIPT), "diff", str(BEFORE), str(AFTER), str(diff_path)])
        if diff_result.returncode != 0:
            print(diff_result.stdout)
            print(diff_result.stderr)
            print("ERROR: computing sample API diff failed")
            return 1

        draft_result = run_command(
            [sys.executable, str(SCRIPT), "draft", str(diff_path), str(draft_path), "--template", str(TEMPLATE)]
        )
        if draft_result.returncode != 0:
            print(draft_result.stdout)
            print(draft_result.stderr)
            print("ERROR: drafting sample API risk review failed")
            return 1

        lint_result = run_command([sys.executable, str(SCRIPT), "lint", str(draft_path)])
        if lint_result.returncode != 0:
            print(lint_result.stdout)
            print(lint_result.stderr)
            print("ERROR: linting drafted API risk review failed")
            return 1

        text = draft_path.read_text(encoding="utf-8")
        for required in (
            "# Billing API Change Risk Review",
            "## Breaking Changes",
            "GET /v1/invoices/{invoice_id}",
            "## Rollout Checks",
        ):
            if required not in text:
                print(f"ERROR: drafted API risk review missing expected content: {required}")
                return 1

    print("api-change-risk-review skill check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
