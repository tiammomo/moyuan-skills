#!/usr/bin/env python3
"""Diff, draft, and lint API change risk reviews."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "assets" / "api-change-risk-template.md"
NONE_MARKER = "_None._"
REQUIRED_DIFF_KEYS = (
    "api_name",
    "from_version",
    "to_version",
    "risk_level",
    "summary",
    "breaking_changes",
    "additive_changes",
    "deprecations",
    "migration_notes",
    "rollout_checks",
    "open_questions",
)
REQUIRED_HEADINGS = (
    "## Summary",
    "## Breaking Changes",
    "## Additive Changes",
    "## Deprecations",
    "## Migration Notes",
    "## Rollout Checks",
    "## Open Questions",
)
TEMPLATE_PLACEHOLDER_RE = re.compile(
    r"\{("
    r"api_name|from_version|to_version|risk_level|summary|"
    r"breaking_changes|additive_changes|deprecations|migration_notes|"
    r"rollout_checks|open_questions"
    r")\}"
)


def load_json_object(path: Path, label: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object")
    return data


def validate_field_list(items: object, label: str) -> list[dict]:
    if not isinstance(items, list):
        raise ValueError(f"'{label}' must be a list")
    parsed: list[dict] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{label} item #{index} must be an object")
        for field in ("name", "type", "required"):
            if field not in item:
                raise ValueError(f"{label} item #{index} is missing '{field}'")
        if not isinstance(item["name"], str) or not item["name"].strip():
            raise ValueError(f"{label} item #{index} must have a non-empty 'name'")
        if not isinstance(item["type"], str) or not item["type"].strip():
            raise ValueError(f"{label} item #{index} must have a non-empty 'type'")
        if not isinstance(item["required"], bool):
            raise ValueError(f"{label} item #{index} must have a boolean 'required'")
        parsed.append(item)
    return parsed


def validate_snapshot(path: Path) -> dict:
    data = load_json_object(path, "schema snapshot")
    for key in ("api_name", "version"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"schema snapshot '{key}' must be a non-empty string")
    endpoints = data.get("endpoints")
    if not isinstance(endpoints, list) or not endpoints:
        raise ValueError("schema snapshot 'endpoints' must be a non-empty list")

    for index, endpoint in enumerate(endpoints, start=1):
        if not isinstance(endpoint, dict):
            raise ValueError(f"endpoint #{index} must be an object")
        for key in ("path", "method", "summary", "auth"):
            if not isinstance(endpoint.get(key), str) or not endpoint[key].strip():
                raise ValueError(f"endpoint #{index} is missing a non-empty '{key}'")
        for section in ("request", "response"):
            block = endpoint.get(section)
            if not isinstance(block, dict):
                raise ValueError(f"endpoint #{index} is missing a '{section}' object")
            block["fields"] = validate_field_list(block.get("fields"), f"endpoint #{index} {section}.fields")
    return data


def endpoint_key(endpoint: dict) -> str:
    return f"{endpoint['method'].strip().upper()} {endpoint['path'].strip()}"


def field_index(fields: list[dict]) -> dict[str, dict]:
    return {field["name"].strip(): field for field in fields}


def render_section(lines: list[str]) -> str:
    return "\n".join(lines) if lines else NONE_MARKER


def render_bullet_list(items: object, label: str) -> str:
    if not isinstance(items, list):
        raise ValueError(f"'{label}' must be a list")
    lines: list[str] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"'{label}' item #{index} must be a non-empty string")
        lines.append(f"- {item.strip()}")
    return render_section(lines)


def build_diff(before: dict, after: dict) -> dict:
    before_endpoints = {endpoint_key(endpoint): endpoint for endpoint in before["endpoints"]}
    after_endpoints = {endpoint_key(endpoint): endpoint for endpoint in after["endpoints"]}

    breaking_changes: list[str] = []
    additive_changes: list[str] = []
    deprecations: list[str] = []
    migration_notes: list[str] = []
    rollout_checks: list[str] = []
    open_questions: list[str] = []

    for key in sorted(before_endpoints.keys() - after_endpoints.keys()):
        breaking_changes.append(f"Removed endpoint {key}.")
        deprecations.append(f"{key} no longer appears in the target snapshot.")
        migration_notes.append(f"Confirm all callers of {key} have a migration path before the target release.")

    for key in sorted(after_endpoints.keys() - before_endpoints.keys()):
        additive_changes.append(f"Added endpoint {key}.")

    for key in sorted(before_endpoints.keys() & after_endpoints.keys()):
        before_endpoint = before_endpoints[key]
        after_endpoint = after_endpoints[key]
        if before_endpoint["auth"] != after_endpoint["auth"]:
            breaking_changes.append(
                f"{key} changed auth from {before_endpoint['auth']} to {after_endpoint['auth']}."
            )
            rollout_checks.append(f"Confirm all callers of {key} can satisfy the new auth requirement.")

        before_request_fields = field_index(before_endpoint["request"]["fields"])
        after_request_fields = field_index(after_endpoint["request"]["fields"])
        before_response_fields = field_index(before_endpoint["response"]["fields"])
        after_response_fields = field_index(after_endpoint["response"]["fields"])

        for field_name in sorted(after_request_fields.keys() - before_request_fields.keys()):
            field = after_request_fields[field_name]
            if field["required"]:
                breaking_changes.append(f"{key} added required request field `{field_name}`.")
                migration_notes.append(f"Callers of {key} must send the new required request field `{field_name}`.")
            else:
                additive_changes.append(f"{key} added optional request field `{field_name}`.")

        for field_name in sorted(before_response_fields.keys() - after_response_fields.keys()):
            breaking_changes.append(f"{key} removed response field `{field_name}`.")
            migration_notes.append(f"Downstream readers of {key} must stop depending on response field `{field_name}`.")

        for field_name in sorted(after_response_fields.keys() - before_response_fields.keys()):
            additive_changes.append(f"{key} added response field `{field_name}`.")

        for field_name in sorted(before_request_fields.keys() & after_request_fields.keys()):
            before_field = before_request_fields[field_name]
            after_field = after_request_fields[field_name]
            if before_field["type"] != after_field["type"]:
                breaking_changes.append(
                    f"{key} changed request field `{field_name}` type from {before_field['type']} to {after_field['type']}."
                )
            if not before_field["required"] and after_field["required"]:
                breaking_changes.append(f"{key} made request field `{field_name}` required.")

        for field_name in sorted(before_response_fields.keys() & after_response_fields.keys()):
            before_field = before_response_fields[field_name]
            after_field = after_response_fields[field_name]
            if before_field["type"] != after_field["type"]:
                breaking_changes.append(
                    f"{key} changed response field `{field_name}` type from {before_field['type']} to {after_field['type']}."
                )

    if not rollout_checks:
        rollout_checks.append("Confirm compatibility checks and owning-team review before rollout.")
    else:
        rollout_checks.append("Add or refresh contract tests for the touched endpoints before rollout.")

    if breaking_changes:
        risk_level = "high"
    elif deprecations:
        risk_level = "medium"
    else:
        risk_level = "low"

    if not open_questions:
        open_questions.append("Are all downstream clients and SDKs covered by the rollout plan?")

    summary = (
        f"{before['api_name']} changes from {before['version']} to {after['version']} introduce "
        f"{len(breaking_changes)} breaking change(s), {len(additive_changes)} additive change(s), "
        f"and {len(deprecations)} deprecation/removal note(s)."
    )

    return {
        "api_name": before["api_name"],
        "from_version": before["version"],
        "to_version": after["version"],
        "risk_level": risk_level,
        "summary": summary,
        "breaking_changes": breaking_changes,
        "additive_changes": additive_changes,
        "deprecations": deprecations,
        "migration_notes": migration_notes,
        "rollout_checks": rollout_checks,
        "open_questions": open_questions,
    }


def load_diff(path: Path) -> dict:
    data = load_json_object(path, "api diff")
    missing = [key for key in REQUIRED_DIFF_KEYS if key not in data]
    if missing:
        raise ValueError(f"api diff is missing keys: {', '.join(missing)}")
    for key in ("api_name", "from_version", "to_version", "risk_level", "summary"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"api diff '{key}' must be a non-empty string")
    for key in ("breaking_changes", "additive_changes", "deprecations", "migration_notes", "rollout_checks", "open_questions"):
        if not isinstance(data[key], list):
            raise ValueError(f"api diff '{key}' must be a list")
    return data


def build_context(diff: dict) -> dict[str, str]:
    return {
        "api_name": diff["api_name"].strip(),
        "from_version": diff["from_version"].strip(),
        "to_version": diff["to_version"].strip(),
        "risk_level": diff["risk_level"].strip(),
        "summary": diff["summary"].strip(),
        "breaking_changes": render_bullet_list(diff["breaking_changes"], "breaking_changes"),
        "additive_changes": render_bullet_list(diff["additive_changes"], "additive_changes"),
        "deprecations": render_bullet_list(diff["deprecations"], "deprecations"),
        "migration_notes": render_bullet_list(diff["migration_notes"], "migration_notes"),
        "rollout_checks": render_bullet_list(diff["rollout_checks"], "rollout_checks"),
        "open_questions": render_bullet_list(diff["open_questions"], "open_questions"),
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def draft_review(diff_path: Path, output_path: Path, template_path: Path) -> None:
    diff = load_diff(diff_path)
    template = template_path.read_text(encoding="utf-8")
    output = template.format(**build_context(diff))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output.strip() + "\n", encoding="utf-8")


def lint_review(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not re.search(r"^# .+ Change Risk Review$", text, re.MULTILINE):
        errors.append("missing top-level API risk review heading")
    if not re.search(r"^_Versions: .+ -> .+_$", text, re.MULTILINE):
        errors.append("missing versions metadata line")
    if not re.search(r"^_Risk level: (low|medium|high)_$", text, re.MULTILINE):
        errors.append("missing risk level metadata line")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing required heading: {heading}")
    if TEMPLATE_PLACEHOLDER_RE.search(text):
        errors.append("draft still contains unresolved template placeholders")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diff, draft, and lint API change risk reviews.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    diff_parser = subparsers.add_parser("diff", help="Compare before/after schema snapshots and write a diff JSON.")
    diff_parser.add_argument("before", type=Path, help="Path to the before schema snapshot JSON.")
    diff_parser.add_argument("after", type=Path, help="Path to the after schema snapshot JSON.")
    diff_parser.add_argument("output", type=Path, help="Path to write the generated diff JSON.")

    draft_parser = subparsers.add_parser("draft", help="Generate a markdown risk review from a diff JSON.")
    draft_parser.add_argument("input", type=Path, help="Path to the diff JSON file.")
    draft_parser.add_argument("output", type=Path, help="Path to write the generated markdown draft.")
    draft_parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Path to the markdown template.")

    lint_parser = subparsers.add_parser("lint", help="Validate a generated or edited risk review draft.")
    lint_parser.add_argument("draft", type=Path, help="Path to the markdown draft to lint.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "diff":
            before = validate_snapshot(args.before)
            after = validate_snapshot(args.after)
            diff = build_diff(before, after)
            write_json(args.output, diff)
            print(f"Wrote API diff to {args.output}")
            return 0
        if args.command == "draft":
            draft_review(args.input, args.output, args.template)
            print(f"Wrote API risk review to {args.output}")
            return 0
        if args.command == "lint":
            errors = lint_review(args.draft)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}")
                return 1
            print(f"API change risk review lint passed for {args.draft}")
            return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
