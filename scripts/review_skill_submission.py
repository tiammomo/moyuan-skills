#!/usr/bin/env python3
"""Review a repo-compatible skill submission stored in the local inbox."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from market_utils import (
    ROOT,
    SUBMISSION_REVIEW_STATUSES,
    dump_json,
    repo_relative_path,
    validate_skill_submission_review_payload,
)
from validate_skill_submission import validate_submission_file


DEFAULT_REVIEWER = "market-maintainer"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review a skill submission stored in the local inbox.")
    parser.add_argument("path", type=Path, help="Path to submission.json.")
    parser.add_argument(
        "--status",
        "--review-status",
        dest="review_status",
        choices=sorted(SUBMISSION_REVIEW_STATUSES),
        default="approved",
        help="Review outcome to write. Defaults to approved.",
    )
    parser.add_argument("--reviewer", default=DEFAULT_REVIEWER, help="Reviewer label recorded in the review artifact.")
    parser.add_argument("--summary", help="Optional summary text. Defaults to a status-based summary.")
    parser.add_argument(
        "--finding",
        action="append",
        default=[],
        help="Optional finding in 'severity:message[:path]' form. Repeat to add multiple findings.",
    )
    parser.add_argument("--review-path", type=Path, help="Optional output path for the review artifact.")
    parser.add_argument("--run-checker", action="store_true", help="Run the uploaded checker command before writing the review artifact.")
    parser.add_argument("--force", action="store_true", help="Replace an existing review artifact.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    resolved = path if path.is_absolute() else (ROOT / path)
    resolved = resolved.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"path must stay inside the repository root: {resolved}") from exc
    return resolved


def parse_finding(raw: str) -> dict:
    parts = [part.strip() for part in raw.split(":", 2)]
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(f"invalid finding '{raw}'; expected 'severity:message[:path]'")

    finding = {
        "severity": parts[0],
        "message": parts[1],
    }
    if len(parts) == 3 and parts[2]:
        finding["path"] = parts[2]
    return finding


def default_summary(review_status: str, submission_id: str) -> str:
    if review_status == "approved":
        return f"Approved {submission_id} for ingest."
    if review_status == "needs-changes":
        return f"{submission_id} needs changes before ingest."
    if review_status == "rejected":
        return f"Rejected {submission_id} for ingest."
    return f"Recorded pending review for {submission_id}."


def is_python_command(token: str) -> bool:
    return Path(token).name.startswith("python")


def run_checker(command: str) -> subprocess.CompletedProcess[str]:
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        raise ValueError(f"invalid checker command: {exc}") from exc
    if not tokens:
        raise ValueError("checker command is empty")
    if is_python_command(tokens[0]):
        tokens[0] = sys.executable
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        tokens,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def review_submission(args: argparse.Namespace) -> int:
    try:
        submission_path = resolve_repo_path(args.path)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1

    submission, errors = validate_submission_file(submission_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    review_path = resolve_repo_path(args.review_path) if args.review_path else submission_path.parent / "review.json"
    if review_path.exists() and not args.force:
        print(f"ERROR: review artifact already exists: {repo_relative_path(review_path)}")
        return 1

    try:
        findings = [parse_finding(item) for item in args.finding]
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1

    if args.run_checker:
        try:
            result = run_checker(submission["checker_command"])
        except ValueError as error:
            print(f"ERROR: {error}")
            return 1
        if result.returncode != 0:
            print("ERROR: checker command failed during review")
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.stderr.strip():
                print(result.stderr.strip())
            return 1

    if args.review_status == "approved" and any(
        finding["severity"] in {"critical", "high"} for finding in findings
    ):
        print("ERROR: approved reviews cannot contain critical/high findings")
        return 1

    review_payload = {
        "review_format": "moyuan-skill-submission-review@v1",
        "submission_id": submission["submission_id"],
        "review_status": args.review_status,
        "reviewer": args.reviewer,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "summary": args.summary.strip() if args.summary else default_summary(args.review_status, submission["submission_id"]),
        "findings": findings,
    }
    label = repo_relative_path(review_path)
    review_errors = validate_skill_submission_review_payload(review_payload, label)
    if review_errors:
        for error in review_errors:
            print(f"ERROR: {error}")
        return 1

    dump_json(review_path, review_payload)
    print(f"Reviewed submission {submission['submission_id']} with status {args.review_status}")
    print(f"Review artifact: {review_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return review_submission(args)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
