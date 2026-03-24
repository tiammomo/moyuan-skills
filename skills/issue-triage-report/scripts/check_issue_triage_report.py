#!/usr/bin/env python3
"""Smoke check for the issue-triage-report skill."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "issue_triage_report.py"
SAMPLE_INPUT = ROOT / "assets" / "sample-issues.csv"
TEMPLATE = ROOT / "assets" / "issue-triage-template.md"
REQUIRED_FILES = (
    ROOT / "SKILL.md",
    ROOT / "agents" / "openai.yaml",
    ROOT / "references" / "input-contract.md",
    ROOT / "references" / "writing-rules.md",
    ROOT / "references" / "review-checklist.md",
    SAMPLE_INPUT,
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
        output_path = Path(tmp_dir) / "triage-report.md"
        draft_result = run_command(
            [sys.executable, str(SCRIPT), "draft", str(SAMPLE_INPUT), str(output_path), "--template", str(TEMPLATE)]
        )
        if draft_result.returncode != 0:
            print(draft_result.stdout)
            print(draft_result.stderr)
            print("ERROR: drafting sample issue triage report failed")
            return 1

        lint_result = run_command([sys.executable, str(SCRIPT), "lint", str(output_path)])
        if lint_result.returncode != 0:
            print(lint_result.stdout)
            print(lint_result.stderr)
            print("ERROR: linting drafted issue triage report failed")
            return 1

        text = output_path.read_text(encoding="utf-8")
        for required in (
            "# Issue Triage Report",
            "## Hot Issues",
            "API-901 Token refresh retries keep looping",
            "## Needs Decision",
        ):
            if required not in text:
                print(f"ERROR: drafted issue triage report missing expected content: {required}")
                return 1

    print("issue-triage-report skill check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
