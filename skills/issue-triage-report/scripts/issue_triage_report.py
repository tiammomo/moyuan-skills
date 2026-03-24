#!/usr/bin/env python3
"""Draft and lint issue triage reports from CSV exports."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "assets" / "issue-triage-template.md"
NONE_MARKER = "_None._"
REQUIRED_COLUMNS = (
    "id",
    "title",
    "severity",
    "status",
    "owner",
    "action",
    "customer_impact",
    "highlight",
)
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
ALLOWED_STATUS = {"open", "in-progress", "blocked", "backlog", "resolved"}
REQUIRED_HEADINGS = (
    "## Summary",
    "## Hot Issues",
    "## Needs Decision",
    "## Assigned Follow-ups",
    "## Backlog Watch",
)


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_issues(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("issue CSV must contain a header row")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"issue CSV is missing columns: {', '.join(missing)}")

        rows: list[dict[str, str]] = []
        for index, row in enumerate(reader, start=2):
            issue = {key: (row.get(key) or "").strip() for key in REQUIRED_COLUMNS}
            if not issue["id"] or not issue["title"]:
                raise ValueError(f"row {index} must include non-empty id and title")
            if issue["severity"] not in SEVERITY_ORDER:
                raise ValueError(f"row {index} has unsupported severity '{issue['severity']}'")
            if issue["status"] not in ALLOWED_STATUS:
                raise ValueError(f"row {index} has unsupported status '{issue['status']}'")
            rows.append(issue)
    return rows


def render_issue(issue: dict[str, str]) -> str:
    parts = [f"- **{issue['id']} {issue['title']}**"]
    detail_bits = [f"Severity: {issue['severity']}", f"Status: {issue['status']}"]
    if issue["owner"]:
        detail_bits.append(f"Owner: {issue['owner']}")
    if issue["action"]:
        detail_bits.append(f"Action: {issue['action']}")
    if issue["customer_impact"]:
        detail_bits.append(f"Impact: {issue['customer_impact']}")
    parts.append(f" ({'; '.join(detail_bits)})")
    return "".join(parts)


def render_section(lines: list[str]) -> str:
    return "\n".join(lines) if lines else NONE_MARKER


def prioritize(issues: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        issues,
        key=lambda issue: (
            SEVERITY_ORDER[issue["severity"]],
            issue["status"] == "resolved",
            issue["id"],
        ),
    )


def build_context(issues: list[dict[str, str]]) -> dict[str, str]:
    highlighted = [issue for issue in issues if parse_bool(issue["highlight"])]
    hot_issues = [
        issue
        for issue in issues
        if issue["status"] != "resolved"
        and (issue["severity"] in {"critical", "high"} or parse_bool(issue["highlight"]))
    ]
    needs_decision = [issue for issue in issues if issue["action"].lower().startswith("decision:")]
    assigned_follow_ups = [
        issue
        for issue in issues
        if issue["status"] not in {"resolved", "backlog"} and issue["owner"]
    ]
    backlog_watch = [
        issue
        for issue in issues
        if issue["status"] == "backlog" or issue["severity"] in {"medium", "low"}
    ]

    active = [issue for issue in issues if issue["status"] != "resolved"]
    critical_count = sum(issue["severity"] == "critical" for issue in active)
    decision_count = len(needs_decision)
    assigned_count = len(assigned_follow_ups)
    summary_lines = [
        f"- Active issues tracked: {len(active)}",
        f"- Critical issues requiring attention: {critical_count}",
        f"- Items needing a decision: {decision_count}",
        f"- Follow-ups already assigned: {assigned_count}",
    ]
    if highlighted:
        summary_lines.append(f"- Explicitly highlighted issues: {len(highlighted)}")

    return {
        "generated_date": date.today().isoformat(),
        "summary": "\n".join(summary_lines),
        "hot_issues": render_section([render_issue(issue) for issue in prioritize(hot_issues)]),
        "needs_decision": render_section([render_issue(issue) for issue in prioritize(needs_decision)]),
        "assigned_follow_ups": render_section([render_issue(issue) for issue in prioritize(assigned_follow_ups)]),
        "backlog_watch": render_section([render_issue(issue) for issue in prioritize(backlog_watch)]),
    }


def draft_report(input_path: Path, output_path: Path, template_path: Path) -> None:
    issues = load_issues(input_path)
    template = template_path.read_text(encoding="utf-8")
    output = template.format(**build_context(issues))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output.strip() + "\n", encoding="utf-8")


def lint_report(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not re.search(r"^# .+\S", text, re.MULTILINE):
        errors.append("missing top-level title heading")
    if not re.search(r"^_Generated on: .+_$", text, re.MULTILINE):
        errors.append("missing generated date line")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing required heading: {heading}")
    if re.search(r"\{[a-z_]+\}", text):
        errors.append("draft still contains unresolved template placeholders")

    summary_match = re.search(r"## Summary\s+(.+?)(?:\n## |\Z)", text, re.DOTALL)
    if summary_match and "-" not in summary_match.group(1):
        errors.append("summary section should include bullet points")

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Draft and lint structured issue triage reports.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser("draft", help="Generate an issue triage report from CSV input.")
    draft_parser.add_argument("input", type=Path, help="Path to the issue CSV file.")
    draft_parser.add_argument("output", type=Path, help="Path to write the generated markdown report.")
    draft_parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Path to the markdown template.")

    lint_parser = subparsers.add_parser("lint", help="Validate a generated or edited issue triage report.")
    lint_parser.add_argument("draft", type=Path, help="Path to the markdown report to lint.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "draft":
            draft_report(args.input, args.output, args.template)
            print(f"Wrote issue triage report to {args.output}")
            return 0
        if args.command == "lint":
            errors = lint_report(args.draft)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}")
                return 1
            print(f"Issue triage lint passed for {args.draft}")
            return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

