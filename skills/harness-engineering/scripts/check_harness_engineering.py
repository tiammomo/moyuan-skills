#!/usr/bin/env python3
"""Smoke check for the harness-engineering teaching bundle."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "SKILL.md"
REQUIRED_FILES = (
    ROOT / "references" / "harness-primitives.md",
    ROOT / "references" / "evals-and-feedback.md",
    ROOT / "references" / "tool-contracts.md",
    ROOT / "references" / "safety-gates.md",
    ROOT / "references" / "automation-patterns.md",
    ROOT / "references" / "future-roadmap.md",
    ROOT / "assets" / "harness-blueprint.md",
    ROOT / "assets" / "tool-contract-template.yaml",
    ROOT / "assets" / "safety-gate-template.yaml",
    ROOT / "assets" / "automation-spec-template.toml",
)
REQUIRED_SKILL_SECTIONS = (
    "## Task Router",
    "## Progressive Loading",
    "## Default Workflow",
)
REQUIRED_TEMPLATE_SECTIONS = (
    "## 0. System Goal",
    "## 1. Routing Surface",
    "## 4. Eval and Feedback",
    "## 6. Rollout Plan",
)
REQUIRED_TOOL_TEMPLATE_STRINGS = (
    'id: "skill-name.command"',
    'skill: "skill-name"',
)


def main() -> int:
    errors: list[str] = []

    if not SKILL_MD.is_file():
        errors.append("missing SKILL.md")
    else:
        text = SKILL_MD.read_text(encoding="utf-8")
        for section in REQUIRED_SKILL_SECTIONS:
            if section not in text:
                errors.append(f"SKILL.md missing section: {section}")

    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT).as_posix()}")

    asset_text = (ROOT / "assets" / "harness-blueprint.md").read_text(encoding="utf-8")
    for section in REQUIRED_TEMPLATE_SECTIONS:
        if section not in asset_text:
            errors.append(f"harness-blueprint.md missing section: {section}")

    tool_template = (ROOT / "assets" / "tool-contract-template.yaml").read_text(encoding="utf-8")
    for snippet in REQUIRED_TOOL_TEMPLATE_STRINGS:
        if snippet not in tool_template:
            errors.append(f"tool-contract-template.yaml missing expected snippet: {snippet}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("harness-engineering teaching bundle check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
