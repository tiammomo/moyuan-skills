#!/usr/bin/env python3
"""Helpers for lightweight harness prototype parsing."""

from __future__ import annotations

import json
from pathlib import Path


def parse_scalar(value: str):
    text = value.strip()
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    if text.startswith("'") and text.endswith("'"):
        return text[1:-1]
    if text == "true":
        return True
    if text == "false":
        return False
    return text


def _prepare_yaml_lines(path: Path) -> list[tuple[int, str, int]]:
    prepared: list[tuple[int, str, int]] = []
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError(f"{path.name}:{lineno}: use multiples of two spaces for indentation")
        prepared.append((indent, stripped, lineno))
    return prepared


def _parse_yaml_block(lines: list[tuple[int, str, int]], index: int, indent: int):
    if index >= len(lines):
        return {}, index
    current_indent, current_text, lineno = lines[index]
    if current_indent != indent:
        raise ValueError(f"unexpected indentation at line {lineno}")

    container = [] if current_text.startswith("- ") else {}

    while index < len(lines):
        current_indent, current_text, lineno = lines[index]
        if current_indent < indent:
            break
        if current_indent != indent:
            raise ValueError(f"unexpected indentation at line {lineno}")

        if isinstance(container, list):
            if not current_text.startswith("- "):
                raise ValueError(f"expected list item at line {lineno}")
            item_text = current_text[2:].strip()
            index += 1
            if not item_text:
                nested, index = _parse_yaml_block(lines, index, indent + 2)
                container.append(nested)
                continue
            if item_text.endswith(":"):
                key = item_text[:-1].strip()
                nested, index = _parse_yaml_block(lines, index, indent + 2)
                container.append({key: nested})
                continue
            container.append(parse_scalar(item_text))
            continue

        if current_text.startswith("- "):
            raise ValueError(f"unexpected list item at line {lineno}")
        if current_text.endswith(":"):
            key = current_text[:-1].strip()
            if index + 1 < len(lines) and lines[index + 1][0] > indent:
                nested, index = _parse_yaml_block(lines, index + 1, indent + 2)
            else:
                nested = {}
                index += 1
            container[key] = nested
            continue
        if ":" not in current_text:
            raise ValueError(f"expected key/value pair at line {lineno}")
        key, value = current_text.split(":", 1)
        container[key.strip()] = parse_scalar(value.strip())
        index += 1

    return container, index


def load_simple_yaml(path: Path):
    lines = _prepare_yaml_lines(path)
    if not lines:
        raise ValueError(f"{path.name}: empty YAML file")
    payload, index = _parse_yaml_block(lines, 0, 0)
    if index != len(lines):
        raise ValueError(f"{path.name}: failed to consume full YAML file")
    return payload


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name}: schema file must contain a JSON object")
    return payload


def get_nested(mapping: dict, path: list[str]):
    current = mapping
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def evaluate_gate_payload(
    payload: dict, checks: list[str], artifacts: list[str], blockers: list[str]
) -> tuple[bool, list[str]]:
    gate = payload["gate"] if "gate" in payload else payload
    missing_checks = [item for item in gate["required_checks"] if item not in checks]
    missing_artifacts = [item for item in gate["audit_artifacts"] if item not in artifacts]
    active_blockers = [item for item in blockers if item in gate["blockers"]]

    messages: list[str] = []
    if missing_checks:
        messages.append(f"Missing checks: {', '.join(missing_checks)}")
    if missing_artifacts:
        messages.append(f"Missing artifacts: {', '.join(missing_artifacts)}")
    if active_blockers:
        messages.append(f"Active blockers: {', '.join(active_blockers)}")

    return not messages, messages
