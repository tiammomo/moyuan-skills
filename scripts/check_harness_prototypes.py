#!/usr/bin/env python3
"""Validate harness prototype examples, schemas, and template packs."""

from __future__ import annotations

import tomllib
from pathlib import Path

from harness_proto_utils import get_nested, load_json, load_simple_yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "examples" / "harness-prototypes" / "schemas"
TOOL_SCHEMA = SCHEMA_DIR / "tool-contract.schema.json"
GATE_SCHEMA = SCHEMA_DIR / "safety-gate.schema.json"
AUTOMATION_SCHEMA = SCHEMA_DIR / "automation.schema.json"
RUNTIME_SCHEMA = SCHEMA_DIR / "runtime-blueprint.schema.json"
TOOL_FILES = (
    ROOT / "examples" / "harness-prototypes" / "tool-contracts" / "release-note-writer.yaml",
    ROOT / "examples" / "harness-prototypes" / "tool-contracts" / "incident-postmortem-writer.yaml",
    ROOT / "templates" / "harness" / "harness-ready" / "tool-contract.yaml.template",
)
GATE_FILES = (
    ROOT / "examples" / "harness-prototypes" / "safety-gates" / "publication-review.yaml",
    ROOT / "templates" / "harness" / "harness-ready" / "safety-gate.yaml.template",
)
AUTOMATION_FILES = (
    ROOT / "examples" / "harness-prototypes" / "automation" / "weekly-triage-digest.toml",
    ROOT / "examples" / "harness-prototypes" / "automation" / "release-note-publication.toml",
    ROOT / "templates" / "harness" / "harness-ready" / "automation.toml.template",
)
RUNTIME_FILES = (
    ROOT / "examples" / "harness-prototypes" / "runtime-blueprints" / "release-note-publication.yaml",
    ROOT / "templates" / "harness" / "harness-ready" / "runtime-blueprint.yaml.template",
)


def validate_yaml_payload(path: Path, schema_path: Path) -> list[str]:
    errors: list[str] = []
    schema = load_json(schema_path)
    payload = load_simple_yaml(path)
    root_name = schema["root"]

    if root_name not in payload:
        return [f"{path.relative_to(ROOT).as_posix()}: missing root section '{root_name}'"]

    required = schema.get("required", {})
    list_fields = schema.get("list_fields", {})
    for section, keys in required.items():
        section_path = [section] if section == root_name else [root_name, section]
        block = get_nested(payload, section_path)
        if not isinstance(block, dict):
            errors.append(f"{path.relative_to(ROOT).as_posix()}: missing object section '{'.'.join(section_path)}'")
            continue
        for key in keys:
            if key not in block:
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}: missing required field '{'.'.join(section_path + [key])}'"
                )

    for section, keys in list_fields.items():
        section_path = [section] if section == root_name else [root_name, section]
        block = get_nested(payload, section_path)
        if not isinstance(block, dict):
            continue
        for key in keys:
            value = block.get(key)
            if not isinstance(value, list) or not value:
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}: '{'.'.join(section_path + [key])}' must be a non-empty list"
                )

    root_block = payload[root_name]
    if root_name == "tool_contract":
        contract_id = root_block.get("id", "")
        if "." not in str(contract_id):
            errors.append(f"{path.relative_to(ROOT).as_posix()}: tool contract id should look like skill-name.command")
    if root_name == "gate":
        gate_id = root_block.get("id", "")
        if not str(gate_id).strip():
            errors.append(f"{path.relative_to(ROOT).as_posix()}: gate id must be non-empty")

    return errors


def validate_toml_payload(path: Path, schema_path: Path) -> list[str]:
    errors: list[str] = []
    schema = load_json(schema_path)
    payload = tomllib.loads(path.read_text(encoding="utf-8"))

    for key in schema.get("required", []):
        if key not in payload:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: missing required field '{key}'")

    for key in schema.get("string_fields", []):
        value = payload.get(key)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"{path.relative_to(ROOT).as_posix()}: '{key}' must be a non-empty string")

    for key in schema.get("bool_fields", []):
        value = payload.get(key)
        if value is not None and not isinstance(value, bool):
            errors.append(f"{path.relative_to(ROOT).as_posix()}: '{key}' must be a boolean")

    for key in schema.get("list_fields", []):
        value = payload.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{path.relative_to(ROOT).as_posix()}: '{key}' must be a non-empty list of strings")

    schedule = str(payload.get("schedule", ""))
    if schedule and len(schedule.split()) < 3:
        errors.append(f"{path.relative_to(ROOT).as_posix()}: 'schedule' should look like a readable recurring schedule")

    return errors


def validate_runtime_blueprint(path: Path) -> list[str]:
    errors: list[str] = []
    payload = load_simple_yaml(path)["runtime_blueprint"]

    action = str(payload.get("action", "")).strip()
    if not action:
        errors.append(f"{path.relative_to(ROOT).as_posix()}: runtime blueprint action must be non-empty")

    outputs = payload.get("outputs", {})
    if isinstance(outputs, dict):
        report_json = str(outputs.get("report_json", ""))
        report_markdown = str(outputs.get("report_markdown", ""))
        if report_json and not report_json.endswith(".json"):
            errors.append(f"{path.relative_to(ROOT).as_posix()}: outputs.report_json should end with .json")
        if report_markdown and not report_markdown.endswith(".md"):
            errors.append(f"{path.relative_to(ROOT).as_posix()}: outputs.report_markdown should end with .md")

    if path.suffix == ".template":
        return errors

    for key in ("automation", "tool_contract", "gate"):
        raw_value = str(payload.get(key, "")).strip()
        if not raw_value:
            continue
        resolved = (ROOT / raw_value).resolve()
        if not resolved.is_file():
            errors.append(
                f"{path.relative_to(ROOT).as_posix()}: referenced file '{raw_value}' is missing"
            )

    return errors


def main() -> int:
    errors: list[str] = []

    for schema in (TOOL_SCHEMA, GATE_SCHEMA, AUTOMATION_SCHEMA, RUNTIME_SCHEMA):
        if not schema.is_file():
            errors.append(f"missing schema file: {schema.relative_to(ROOT).as_posix()}")

    for path in TOOL_FILES:
        if not path.is_file():
            errors.append(f"missing tool contract file: {path.relative_to(ROOT).as_posix()}")
        else:
            errors.extend(validate_yaml_payload(path, TOOL_SCHEMA))

    for path in GATE_FILES:
        if not path.is_file():
            errors.append(f"missing safety gate file: {path.relative_to(ROOT).as_posix()}")
        else:
            errors.extend(validate_yaml_payload(path, GATE_SCHEMA))

    for path in AUTOMATION_FILES:
        if not path.is_file():
            errors.append(f"missing automation file: {path.relative_to(ROOT).as_posix()}")
        else:
            errors.extend(validate_toml_payload(path, AUTOMATION_SCHEMA))

    for path in RUNTIME_FILES:
        if not path.is_file():
            errors.append(f"missing runtime blueprint file: {path.relative_to(ROOT).as_posix()}")
        else:
            errors.extend(validate_yaml_payload(path, RUNTIME_SCHEMA))
            errors.extend(validate_runtime_blueprint(path))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Harness prototype check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
