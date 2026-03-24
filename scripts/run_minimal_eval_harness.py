#!/usr/bin/env python3
"""Run a minimal eval harness against the release-note-writer skill."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "examples" / "eval-harness" / "release-note-writer" / "eval-cases.json"
SKILL_SCRIPT = ROOT / "skills" / "release-note-writer" / "scripts" / "release_note_writer.py"


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        text=True,
        capture_output=True,
        check=False,
    )


def run_case(cases_root: Path, case: dict) -> list[str]:
    errors: list[str] = []
    input_path = cases_root / str(case["input"])

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / f"{case['name']}.md"
        draft_result = run_command(
            [
                sys.executable,
                str(SKILL_SCRIPT),
                "draft",
                str(input_path),
                str(output_path),
            ]
        )
        if draft_result.returncode != 0:
            errors.append(f"{case['name']}: draft command failed")
            errors.append(draft_result.stdout.strip())
            errors.append(draft_result.stderr.strip())
            return [error for error in errors if error]

        lint_result = run_command(
            [
                sys.executable,
                str(SKILL_SCRIPT),
                "lint",
                str(output_path),
            ]
        )
        if lint_result.returncode != 0:
            errors.append(f"{case['name']}: lint command failed")
            errors.append(lint_result.stdout.strip())
            errors.append(lint_result.stderr.strip())
            return [error for error in errors if error]

        text = output_path.read_text(encoding="utf-8")
        for required in case.get("required_substrings", []):
            if required not in text:
                errors.append(f"{case['name']}: missing required substring: {required}")
        for forbidden in case.get("forbidden_substrings", []):
            if forbidden in text:
                errors.append(f"{case['name']}: found forbidden substring: {forbidden}")

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the repository's minimal eval harness example.")
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES,
        help="Path to the eval case definition JSON file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = json.loads(args.cases.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if not isinstance(cases, list) or not cases:
        print("ERROR: eval case file must contain a non-empty 'cases' list")
        return 1

    cases_root = args.cases.parent
    all_errors: list[str] = []
    for case in cases:
        all_errors.extend(run_case(cases_root, case))

    if all_errors:
        for error in all_errors:
            if error:
                print(f"ERROR: {error}")
        return 1

    print(f"Minimal eval harness passed for {len(cases)} case(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
