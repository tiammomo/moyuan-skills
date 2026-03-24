#!/usr/bin/env python3
"""Smoke check for the incident-postmortem-writer skill."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "incident_postmortem_writer.py"
SAMPLE_INPUT = ROOT / "assets" / "sample-incident.json"
TEMPLATE = ROOT / "assets" / "postmortem-template.md"
REQUIRED_FILES = (
    ROOT / "SKILL.md",
    ROOT / "agents" / "openai.yaml",
    ROOT / "references" / "input-contract.md",
    ROOT / "references" / "communication-guardrails.md",
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
        output_path = Path(tmp_dir) / "incident-postmortem.md"
        draft_result = run_command(
            [sys.executable, str(SCRIPT), "draft", str(SAMPLE_INPUT), str(output_path), "--template", str(TEMPLATE)]
        )
        if draft_result.returncode != 0:
            print(draft_result.stdout)
            print(draft_result.stderr)
            print("ERROR: drafting sample incident postmortem failed")
            return 1

        lint_result = run_command([sys.executable, str(SCRIPT), "lint", str(output_path)])
        if lint_result.returncode != 0:
            print(lint_result.stdout)
            print(lint_result.stderr)
            print("ERROR: linting drafted incident postmortem failed")
            return 1

        text = output_path.read_text(encoding="utf-8")
        for required in (
            "# Incident INC-2048",
            "## Customer Impact",
            "Authentication API",
            "## Action Items",
        ):
            if required not in text:
                print(f"ERROR: drafted incident postmortem missing expected content: {required}")
                return 1

    print("incident-postmortem-writer skill check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
