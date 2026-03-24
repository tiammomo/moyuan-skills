#!/usr/bin/env python3
"""Smoke check for the progressive-disclosure teaching bundle."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "SKILL.md"
REQUIRED_FILES = (
    ROOT / "references" / "loading-splits.md",
    ROOT / "references" / "routing-patterns.md",
    ROOT / "references" / "refactor-playbook.md",
    ROOT / "assets" / "loading-plan-template.md",
)
REQUIRED_SKILL_SECTIONS = (
    "## Task Router",
    "## Progressive Loading",
    "## Default Workflow",
)
REQUIRED_TEMPLATE_SECTIONS = (
    "## Current State",
    "## Target Layering",
    "## Router Rewrite",
    "## Validation",
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

    asset_text = (ROOT / "assets" / "loading-plan-template.md").read_text(encoding="utf-8")
    for section in REQUIRED_TEMPLATE_SECTIONS:
        if section not in asset_text:
            errors.append(f"loading-plan-template.md missing section: {section}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("progressive-disclosure teaching bundle check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
