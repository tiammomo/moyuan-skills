#!/usr/bin/env python3
"""Smoke check for the build-skills teaching bundle."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "SKILL.md"
REQUIRED_FILES = (
    ROOT / "references" / "design-flow.md",
    ROOT / "references" / "resource-planning.md",
    ROOT / "references" / "validation-loop.md",
    ROOT / "assets" / "skill-design-canvas.md",
)
REQUIRED_SKILL_SECTIONS = (
    "## Task Router",
    "## Progressive Loading",
    "## Default Workflow",
)
REQUIRED_TEMPLATE_SECTIONS = (
    "## 0. Skill Identity",
    "## 1. Trigger Examples",
    "## 3. Progressive Loading Plan",
    "## 5. Validation Loop",
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

    asset_text = (ROOT / "assets" / "skill-design-canvas.md").read_text(encoding="utf-8")
    for section in REQUIRED_TEMPLATE_SECTIONS:
        if section not in asset_text:
            errors.append(f"skill-design-canvas.md missing section: {section}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("build-skills teaching bundle check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
