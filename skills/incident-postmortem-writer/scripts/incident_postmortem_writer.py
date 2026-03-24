#!/usr/bin/env python3
"""Draft and lint incident postmortems from structured JSON input."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "assets" / "postmortem-template.md"
NONE_MARKER = "_None._"
REQUIRED_KEYS = (
    "incident_id",
    "service",
    "severity",
    "start_time",
    "end_time",
    "summary",
    "customer_impact",
    "root_cause",
    "timeline",
    "action_items",
    "follow_up_risks",
)
ALLOWED_SEVERITY = {"sev1", "sev2", "sev3", "sev4"}
REQUIRED_HEADINGS = (
    "## Summary",
    "## Customer Impact",
    "## Timeline",
    "## Root Cause",
    "## Action Items",
    "## Follow-up Risks",
)


def render_section(lines: list[str]) -> str:
    return "\n".join(lines) if lines else NONE_MARKER


def render_follow_up_risk(item: object) -> str:
    if isinstance(item, str) and item.strip():
        return f"- {item.strip()}"
    if isinstance(item, dict):
        title = str(item.get("title", "")).strip()
        description = str(item.get("description", "")).strip()
        if title and description:
            return f"- **{title}**: {description}"
        if title:
            return f"- {title}"
        if description:
            return f"- {description}"
    raise ValueError("follow_up_risks items must be strings or objects with title/description")


def load_incident(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("incident input must be a JSON object")

    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ValueError(f"incident input is missing keys: {', '.join(missing)}")

    for key in ("incident_id", "service", "severity", "start_time", "end_time", "summary", "customer_impact", "root_cause"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"'{key}' must be a non-empty string")

    if data["severity"] not in ALLOWED_SEVERITY:
        raise ValueError(f"unsupported severity '{data['severity']}'")

    if not isinstance(data["timeline"], list):
        raise ValueError("'timeline' must be a list")
    if not isinstance(data["action_items"], list):
        raise ValueError("'action_items' must be a list")
    if not isinstance(data["follow_up_risks"], list):
        raise ValueError("'follow_up_risks' must be a list")

    for index, entry in enumerate(data["timeline"], start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"timeline entry #{index} must be an object")
        for field in ("time", "event"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise ValueError(f"timeline entry #{index} is missing a non-empty '{field}'")

    for index, item in enumerate(data["action_items"], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"action item #{index} must be an object")
        for field in ("title", "owner"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"action item #{index} is missing a non-empty '{field}'")

    return data


def build_context(data: dict) -> dict[str, str]:
    timeline = []
    for entry in data["timeline"]:
        owner = str(entry.get("owner", "")).strip()
        suffix = f" ({owner})" if owner else ""
        timeline.append(f"- **{entry['time'].strip()}**: {entry['event'].strip()}{suffix}")

    action_items = []
    for item in data["action_items"]:
        parts = [f"- **{item['title'].strip()}**"]
        detail_bits = [f"Owner: {item['owner'].strip()}"]
        status = str(item.get("status", "")).strip()
        due_date = str(item.get("due_date", "")).strip()
        if status:
            detail_bits.append(f"Status: {status}")
        if due_date:
            detail_bits.append(f"Due: {due_date}")
        parts.append(f" ({'; '.join(detail_bits)})")
        action_items.append("".join(parts))

    follow_up_risks = [render_follow_up_risk(item) for item in data["follow_up_risks"]]

    return {
        "incident_id": data["incident_id"].strip(),
        "service": data["service"].strip(),
        "severity": data["severity"].strip(),
        "start_time": data["start_time"].strip(),
        "end_time": data["end_time"].strip(),
        "summary": data["summary"].strip(),
        "customer_impact": data["customer_impact"].strip(),
        "root_cause": data["root_cause"].strip(),
        "timeline": render_section(timeline),
        "action_items": render_section(action_items),
        "follow_up_risks": render_section(follow_up_risks),
    }


def draft_postmortem(input_path: Path, output_path: Path, template_path: Path) -> None:
    data = load_incident(input_path)
    template = template_path.read_text(encoding="utf-8")
    output = template.format(**build_context(data))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output.strip() + "\n", encoding="utf-8")


def lint_postmortem(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not re.search(r"^# Incident .+\S", text, re.MULTILINE):
        errors.append("missing top-level incident heading")
    if not re.search(r"^_Service: .+_$", text, re.MULTILINE):
        errors.append("missing service metadata line")
    if not re.search(r"^_Severity: .+_$", text, re.MULTILINE):
        errors.append("missing severity metadata line")
    if not re.search(r"^_Window: .+_$", text, re.MULTILINE):
        errors.append("missing incident window metadata line")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing required heading: {heading}")
    if re.search(r"\{[a-z_]+\}", text):
        errors.append("draft still contains unresolved template placeholders")
    if "blame" in text.lower():
        errors.append("postmortem should avoid blame-oriented wording")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Draft and lint structured incident postmortems.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser("draft", help="Generate a postmortem from structured JSON input.")
    draft_parser.add_argument("input", type=Path, help="Path to the incident JSON file.")
    draft_parser.add_argument("output", type=Path, help="Path to write the generated markdown postmortem.")
    draft_parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Path to the markdown template.")

    lint_parser = subparsers.add_parser("lint", help="Validate a generated or edited postmortem.")
    lint_parser.add_argument("draft", type=Path, help="Path to the markdown postmortem to lint.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "draft":
            draft_postmortem(args.input, args.output, args.template)
            print(f"Wrote incident postmortem to {args.output}")
            return 0
        if args.command == "lint":
            errors = lint_postmortem(args.draft)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}")
                return 1
            print(f"Incident postmortem lint passed for {args.draft}")
            return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

