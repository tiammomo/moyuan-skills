#!/usr/bin/env python3
"""Draft and lint release notes from a structured JSON change feed."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "assets" / "release-note-template.md"
NONE_MARKER = "_None._"
TYPE_TO_SECTION = {
    "feature": "features",
    "improvement": "improvements",
    "fix": "fixes",
    "security": "fixes",
    "docs": "improvements",
    "internal": "improvements",
}
REQUIRED_INPUT_KEYS = (
    "product_name",
    "version",
    "release_date",
    "summary",
    "changes",
    "breaking_changes",
    "known_issues",
)
REQUIRED_HEADINGS = (
    "## Summary",
    "## Highlights",
    "## Features",
    "## Improvements",
    "## Fixes",
    "## Breaking Changes",
    "## Known Issues",
)


def load_release_input(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("release input must be a JSON object")

    missing_keys = [key for key in REQUIRED_INPUT_KEYS if key not in data]
    if missing_keys:
        raise ValueError(f"release input is missing keys: {', '.join(missing_keys)}")

    for key in ("product_name", "version", "release_date", "summary"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"'{key}' must be a non-empty string")

    if not isinstance(data["changes"], list):
        raise ValueError("'changes' must be a list")
    if not isinstance(data["breaking_changes"], list):
        raise ValueError("'breaking_changes' must be a list")
    if not isinstance(data["known_issues"], list):
        raise ValueError("'known_issues' must be a list")

    for index, change in enumerate(data["changes"], start=1):
        if not isinstance(change, dict):
            raise ValueError(f"change #{index} must be an object")
        for field in ("type", "title", "description"):
            if not isinstance(change.get(field), str) or not change[field].strip():
                raise ValueError(f"change #{index} is missing a non-empty '{field}'")
        if change["type"] not in TYPE_TO_SECTION:
            raise ValueError(
                f"change #{index} has unsupported type '{change['type']}'"
            )

    return data


def render_change(change: dict) -> str:
    text = f"- **{change['title'].strip()}**: {change['description'].strip()}"
    extras: list[str] = []
    impact = change.get("impact")
    ticket = change.get("ticket")
    if isinstance(impact, str) and impact.strip():
        extras.append(f"Impact: {impact.strip()}")
    if isinstance(ticket, str) and ticket.strip():
        extras.append(ticket.strip())
    if extras:
        text += f" ({'; '.join(extras)})"
    return text


def render_simple_item(item: object) -> str:
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
    raise ValueError("breaking_changes and known_issues items must be strings or objects with title/description")


def render_section(lines: list[str]) -> str:
    return "\n".join(lines) if lines else NONE_MARKER


def choose_highlights(changes: list[dict]) -> list[dict]:
    explicit = [change for change in changes if change.get("highlight") is True]
    if explicit:
        return explicit[:3]
    fallback = [change for change in changes if change["type"] != "internal"]
    return fallback[:3]


def build_template_context(data: dict) -> dict[str, str]:
    grouped: dict[str, list[str]] = {
        "features": [],
        "improvements": [],
        "fixes": [],
    }
    for change in data["changes"]:
        grouped[TYPE_TO_SECTION[change["type"]]].append(render_change(change))

    highlights = [render_change(change) for change in choose_highlights(data["changes"])]
    breaking_changes = [render_simple_item(item) for item in data["breaking_changes"]]
    known_issues = [render_simple_item(item) for item in data["known_issues"]]

    return {
        "product_name": data["product_name"].strip(),
        "version": data["version"].strip(),
        "release_date": data["release_date"].strip(),
        "summary": data["summary"].strip(),
        "highlights": render_section(highlights),
        "features": render_section(grouped["features"]),
        "improvements": render_section(grouped["improvements"]),
        "fixes": render_section(grouped["fixes"]),
        "breaking_changes": render_section(breaking_changes),
        "known_issues": render_section(known_issues),
    }


def draft_release_notes(input_path: Path, output_path: Path, template_path: Path) -> None:
    data = load_release_input(input_path)
    template = template_path.read_text(encoding="utf-8")
    output = template.format(**build_template_context(data))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output.strip() + "\n", encoding="utf-8")


def lint_release_notes(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not re.search(r"^# .+\S", text, re.MULTILINE):
        errors.append("missing top-level title heading")
    if not re.search(r"^_Release date: .+_$", text, re.MULTILINE):
        errors.append("missing release date line")

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing required heading: {heading}")

    if re.search(r"\{[a-z_]+\}", text):
        errors.append("draft still contains unresolved template placeholders")

    if "## Summary" in text:
        summary_match = re.search(
            r"## Summary\s+(.+?)(?:\n## |\Z)",
            text,
            re.DOTALL,
        )
        if summary_match and not summary_match.group(1).strip():
            errors.append("summary section is empty")

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Draft and lint structured release notes.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser("draft", help="Generate a release-note draft from JSON input.")
    draft_parser.add_argument("input", type=Path, help="Path to the structured release JSON file.")
    draft_parser.add_argument("output", type=Path, help="Path to write the generated markdown draft.")
    draft_parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="Path to the markdown template file.",
    )

    lint_parser = subparsers.add_parser("lint", help="Validate a generated or edited release-note draft.")
    lint_parser.add_argument("draft", type=Path, help="Path to the markdown draft to lint.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "draft":
            draft_release_notes(args.input, args.output, args.template)
            print(f"Wrote release notes to {args.output}")
            return 0

        if args.command == "lint":
            errors = lint_release_notes(args.draft)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}")
                return 1
            print(f"Release note lint passed for {args.draft}")
            return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

