#!/usr/bin/env python3
"""Validate progressive-skill conventions for this repository."""

from __future__ import annotations

import re
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
DOCS_DIR = ROOT / "docs"
TEACHING_DIR = DOCS_DIR / "teaching"
LINT_FIXTURES_DIR = ROOT / "examples" / "lint-fixtures"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
SECONDARY_HEADING_RE = re.compile(r"^## (.+?)\s*$")
CONTENTS_LINK_RE = re.compile(r"\[[^\]]+\]\(#([^)]+)\)")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TOP_LEVEL_SECTION_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*$")
INTERFACE_FIELD_RE = re.compile(r"^  ([A-Za-z_][\w-]*):\s*(.+?)\s*$")
QUOTED_STRING_RE = re.compile(r'^"(.*)"$')
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
REQUIRED_HEADINGS = (
    "## Safety First",
    "## Task Router",
    "## Progressive Loading",
    "## Default Workflow",
)
REQUIRED_INTERFACE_FIELDS = (
    "display_name",
    "short_description",
    "default_prompt",
)
REFERENCE_TOC_LINE_THRESHOLD = 100
MAX_REFERENCE_HOPS = 2
DISALLOWED_HEADINGS = (
    "## When to Use",
    "## When to Use This Skill",
    "## Installation",
    "## Setup",
)
ROUTER_ACTION_HINTS = ("Read ", "Use ", "Run ", "Open ", "Copy ")
REQUIRED_TEACHING_FILES = (
    "README.md",
    "01-learning-map.md",
    "02-read-the-repo.md",
    "03-build-your-first-skill.md",
    "04-progressive-disclosure-workshop.md",
    "05-harness-roadmap.md",
    "06-exercises-and-capstone.md",
    "07-case-gradient.md",
    "08-evals-and-prototypes.md",
    "09-project-learning-roadmap.md",
    "10-learner-path.md",
    "11-skill-author-path.md",
    "12-maintainer-path.md",
    "13-harness-builder-path.md",
    "14-first-hour-onboarding.md",
)
REQUIRED_LINT_FIXTURES = (
    "README.md",
    "bad-router.md",
    "bad-setup-heading.md",
    "bad-openai.yaml",
)
MIN_DESCRIPTION_LENGTH = 120
MAX_DESCRIPTION_LENGTH = 420


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None

    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            return None
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def has_nonempty_dir(path: Path) -> bool:
    return path.is_dir() and any(path.iterdir())


def slugify_heading(heading: str) -> str:
    slug = heading.strip().lower().replace("`", "")
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s", "-", slug)
    return slug.strip("-")


def extract_secondary_headings(lines: list[str]) -> list[tuple[str, int]]:
    headings: list[tuple[str, int]] = []
    for index, line in enumerate(lines):
        match = SECONDARY_HEADING_RE.match(line)
        if match:
            headings.append((match.group(1).strip(), index))
    return headings


def extract_contents_slugs(
    lines: list[str], headings: list[tuple[str, int]], contents_index: int
) -> set[str]:
    start = headings[contents_index][1] + 1
    if contents_index + 1 < len(headings):
        end = headings[contents_index + 1][1]
    else:
        end = len(lines)

    slugs: set[str] = set()
    for line in lines[start:end]:
        for match in CONTENTS_LINK_RE.finditer(line):
            slugs.add(match.group(1).strip().lower())
    return slugs


def extract_reference_targets(source_file: Path, skill_dir: Path) -> tuple[set[Path], list[str]]:
    targets: set[Path] = set()
    errors: list[str] = []
    skill_root = skill_dir.resolve()
    text = source_file.read_text(encoding="utf-8")

    for match in MARKDOWN_LINK_RE.finditer(text):
        raw_target = match.group(1).strip()
        if not raw_target:
            continue
        target_token = raw_target.split()[0].strip("<>")
        if not target_token or target_token.startswith("#"):
            continue
        if "://" in target_token or target_token.startswith(("mailto:", "data:")):
            continue

        path_part = target_token.split("#", 1)[0]
        if not path_part:
            continue

        resolved = (source_file.parent / Path(path_part)).resolve()
        try:
            relative_target = resolved.relative_to(skill_root)
        except ValueError:
            continue

        if resolved.suffix.lower() != ".md":
            continue
        if not relative_target.parts or relative_target.parts[0] != "references":
            continue
        if not resolved.is_file():
            source_label = source_file.relative_to(skill_root).as_posix()
            errors.append(
                f"{skill_dir.name}:{source_label} links to missing reference '{relative_target.as_posix()}'"
            )
            continue
        targets.add(resolved)

    return targets, errors


def validate_reference_reachability(skill_dir: Path, skill_md: Path, reference_files: list[Path]) -> list[str]:
    errors: list[str] = []
    graph: dict[Path, set[Path]] = {}

    skill_targets, skill_errors = extract_reference_targets(skill_md, skill_dir)
    graph[skill_md.resolve()] = skill_targets
    errors.extend(skill_errors)

    for reference_file in reference_files:
        targets, target_errors = extract_reference_targets(reference_file, skill_dir)
        graph[reference_file.resolve()] = targets
        errors.extend(target_errors)

    depths: dict[Path, int] = {}
    queue: deque[tuple[Path, int]] = deque((target, 1) for target in graph.get(skill_md.resolve(), set()))

    while queue:
        current, depth = queue.popleft()
        previous_depth = depths.get(current)
        if previous_depth is not None and previous_depth <= depth:
            continue
        depths[current] = depth
        for neighbor in graph.get(current, set()):
            queue.append((neighbor, depth + 1))

    for reference_file in reference_files:
        resolved = reference_file.resolve()
        reference_label = f"{skill_dir.name}:{reference_file.name}"
        if resolved not in depths:
            errors.append(
                f"{reference_label}: reference file is unreachable from SKILL.md; link it directly or from a directly linked routing reference"
            )
            continue
        if depths[resolved] > MAX_REFERENCE_HOPS:
            errors.append(
                f"{reference_label}: reference file is only reachable after {depths[resolved]} hops; keep reference routing within {MAX_REFERENCE_HOPS} hops from SKILL.md"
            )

    return errors


def validate_reference_file(skill_dir: Path, reference_file: Path) -> list[str]:
    errors: list[str] = []
    lines = reference_file.read_text(encoding="utf-8").splitlines()
    headings = extract_secondary_headings(lines)
    if not headings:
        return errors

    contents_index = next((i for i, (heading, _) in enumerate(headings) if heading == "Contents"), None)
    long_reference = len(lines) > REFERENCE_TOC_LINE_THRESHOLD
    reference_label = f"{skill_dir.name}:{reference_file.name}"

    if long_reference and contents_index is None:
        errors.append(
            f"{reference_label}: reference files over {REFERENCE_TOC_LINE_THRESHOLD} lines should start with a '## Contents' section"
        )
        return errors

    if contents_index is None:
        return errors

    if headings[0][0] != "Contents":
        errors.append(f"{reference_label}: '## Contents' should be the first secondary heading for easier routing")

    target_headings = [heading for heading, _ in headings if heading != "Contents"]
    if not target_headings:
        errors.append(f"{reference_label}: '## Contents' should point to at least one task-specific section")
        return errors

    contents_slugs = extract_contents_slugs(lines, headings, contents_index)
    missing_headings = [heading for heading in target_headings if slugify_heading(heading) not in contents_slugs]
    if missing_headings:
        errors.append(
            f"{reference_label}: '## Contents' is missing links for {', '.join(repr(heading) for heading in missing_headings)}"
        )

    return errors


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    section_lines: list[str] = []
    capture = False
    for line in lines:
        if line == heading:
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture:
            section_lines.append(line)
    return "\n".join(section_lines).strip()


def split_router_blocks(section_text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in section_text.splitlines():
        if line.startswith("- "):
            if current:
                blocks.append(current)
            current = [line]
        elif current and (line.startswith("  ") or not line.strip()):
            current.append(line)
        elif current:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def validate_task_router(skill_dir: Path, text: str) -> list[str]:
    errors: list[str] = []
    router_section = extract_section(text, "## Task Router")
    if not router_section:
        return errors

    router_blocks = split_router_blocks(router_section)
    if not router_blocks:
        errors.append(f"{skill_dir.name}: '## Task Router' should contain at least one routed bullet")
        return errors

    for index, block in enumerate(router_blocks, start=1):
        first_line = block[0]
        if ":" not in first_line:
            errors.append(
                f"{skill_dir.name}: router bullet #{index} should describe a scenario and end with a colon"
            )
        block_text = "\n".join(block)
        if not any(hint in block_text for hint in ROUTER_ACTION_HINTS):
            errors.append(
                f"{skill_dir.name}: router bullet #{index} should tell the reader to Read, Use, Run, Open, or Copy a resource"
            )
        reference_count = block_text.count("references/")
        if reference_count > 2:
            errors.append(
                f"{skill_dir.name}: router bullet #{index} routes to too many references ({reference_count}); keep each route narrow"
            )

    return errors


def extract_skill_title(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def parse_openai_yaml(path: Path) -> tuple[dict[str, str], list[str]]:
    interface: dict[str, str] = {}
    errors: list[str] = []
    current_top: str | None = None

    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        top_match = TOP_LEVEL_SECTION_RE.match(line)
        if top_match and not line.startswith(" "):
            current_top = top_match.group(1)
            continue

        if current_top != "interface":
            continue

        field_match = INTERFACE_FIELD_RE.match(line)
        if not field_match:
            errors.append(f"{path.name}:{lineno}: unsupported interface structure")
            continue

        key, raw_value = field_match.groups()
        if key in interface:
            errors.append(f"{path.name}:{lineno}: duplicate interface.{key} field")
            continue

        quoted_match = QUOTED_STRING_RE.match(raw_value.strip())
        if not quoted_match:
            errors.append(f"{path.name}:{lineno}: interface.{key} should use quoted string values")
            continue

        interface[key] = quoted_match.group(1)

    return interface, errors


def validate_openai_yaml(skill_dir: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    agents_dir = skill_dir / "agents"
    openai_yaml = agents_dir / "openai.yaml"

    if agents_dir.exists() and any(agents_dir.iterdir()) and not openai_yaml.is_file():
        errors.append(f"{skill_dir.name}: agents/ is present but missing agents/openai.yaml")
        return errors

    if not openai_yaml.is_file():
        return errors

    interface, parse_errors = parse_openai_yaml(openai_yaml)
    for error in parse_errors:
        errors.append(f"{skill_dir.name}:agents/{error}")

    skill_title = extract_skill_title(skill_text)
    if not skill_title:
        errors.append(f"{skill_dir.name}: SKILL.md should contain a top-level '# ...' title for openai.yaml consistency checks")
        return errors

    for field in REQUIRED_INTERFACE_FIELDS:
        if field not in interface:
            errors.append(f"{skill_dir.name}: agents/openai.yaml is missing interface.{field}")

    display_name = interface.get("display_name", "")
    short_description = interface.get("short_description", "")
    default_prompt = interface.get("default_prompt", "")
    brand_color = interface.get("brand_color")

    if display_name and display_name != skill_title:
        errors.append(
            f"{skill_dir.name}: interface.display_name should match the SKILL.md title '{skill_title}'"
        )

    if short_description:
        if not 25 <= len(short_description) <= 64:
            errors.append(
                f"{skill_dir.name}: interface.short_description must be 25-64 characters (got {len(short_description)})"
            )

    if default_prompt and f"${skill_dir.name}" not in default_prompt:
        errors.append(
            f"{skill_dir.name}: interface.default_prompt must explicitly mention ${skill_dir.name}"
        )

    for icon_field in ("icon_small", "icon_large"):
        icon_path = interface.get(icon_field)
        if icon_path:
            resolved = (skill_dir / icon_path).resolve()
            if not resolved.is_file():
                errors.append(
                    f"{skill_dir.name}: interface.{icon_field} points to missing file '{icon_path}'"
                )

    if brand_color and not HEX_COLOR_RE.match(brand_color):
        errors.append(
            f"{skill_dir.name}: interface.brand_color must be a hex color like #3B82F6"
        )

    return errors


def validate_skill_antipatterns(skill_dir: Path, text: str) -> list[str]:
    errors: list[str] = []

    if "[TODO" in text or "TODO:" in text:
        errors.append(f"{skill_dir.name}: SKILL.md still contains TODO placeholders")

    for heading in DISALLOWED_HEADINGS:
        if heading in text:
            errors.append(
                f"{skill_dir.name}: avoid a '{heading}' section; trigger guidance belongs in frontmatter, not the body"
            )

    extra_markdown = [
        path.name
        for path in skill_dir.glob("*.md")
        if path.name != "SKILL.md"
    ]
    if extra_markdown:
        errors.append(
            f"{skill_dir.name}: do not keep extra top-level markdown files in the skill dir ({', '.join(sorted(extra_markdown))})"
        )

    return errors


def validate_teaching_docs() -> list[str]:
    errors: list[str] = []
    if not TEACHING_DIR.is_dir():
        return ["docs: missing docs/teaching directory"]

    for filename in REQUIRED_TEACHING_FILES:
        path = TEACHING_DIR / filename
        if not path.is_file():
            errors.append(f"docs: missing teaching file '{filename}'")

    teaching_readme = TEACHING_DIR / "README.md"
    docs_readme = DOCS_DIR / "README.md"

    if teaching_readme.is_file():
        teaching_text = teaching_readme.read_text(encoding="utf-8")
        for filename in REQUIRED_TEACHING_FILES:
            if filename == "README.md":
                continue
            if f"./{filename}" not in teaching_text:
                errors.append(f"docs: teaching README should link to '{filename}'")

    if docs_readme.is_file():
        docs_text = docs_readme.read_text(encoding="utf-8")
        if "teaching/" not in docs_text:
            errors.append("docs: docs/README.md should expose the teaching directory")
        for filename in REQUIRED_TEACHING_FILES:
            if filename == "README.md":
                continue
            if f"./teaching/{filename}" not in docs_text:
                errors.append(f"docs: docs/README.md should link to teaching file '{filename}'")

    for path in TEACHING_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if "[TODO" in text or "TODO:" in text:
            errors.append(f"docs: teaching file '{path.name}' still contains TODO placeholders")
        if not any(line.startswith("# ") for line in text.splitlines()):
            errors.append(f"docs: teaching file '{path.name}' should start with a top-level title")

    return errors


def validate_lint_fixtures() -> list[str]:
    errors: list[str] = []
    if not LINT_FIXTURES_DIR.is_dir():
        return ["examples: missing examples/lint-fixtures directory"]

    for filename in REQUIRED_LINT_FIXTURES:
        path = LINT_FIXTURES_DIR / filename
        if not path.is_file():
            errors.append(f"examples: missing lint fixture '{filename}'")

    return errors


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir.name}: missing SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    if line_count > 500:
        errors.append(f"{skill_dir.name}: SKILL.md has {line_count} lines; keep it under 500 for progressive loading")

    frontmatter = parse_frontmatter(text)
    if frontmatter is None:
        errors.append(f"{skill_dir.name}: SKILL.md is missing valid YAML frontmatter")
    else:
        expected_keys = {"name", "description"}
        actual_keys = set(frontmatter)
        if actual_keys != expected_keys:
            errors.append(
                f"{skill_dir.name}: frontmatter keys must be exactly {sorted(expected_keys)}, found {sorted(actual_keys)}"
            )
        if frontmatter.get("name") != skill_dir.name:
            errors.append(f"{skill_dir.name}: frontmatter name must match directory name")
        description = frontmatter.get("description", "")
        if not MIN_DESCRIPTION_LENGTH <= len(description) <= MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"{skill_dir.name}: description should be {MIN_DESCRIPTION_LENGTH}-{MAX_DESCRIPTION_LENGTH} characters (got {len(description)})"
            )
        if "Use when" not in description:
            errors.append(f"{skill_dir.name}: description should include an explicit 'Use when ...' trigger clause")
        if "Codex needs to" not in description and "Codex needs" not in description:
            errors.append(f"{skill_dir.name}: description should describe what Codex needs to do, not only the artifact name")

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{skill_dir.name}: missing required section '{heading}'")

    references_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"
    assets_dir = skill_dir / "assets"

    if has_nonempty_dir(references_dir):
        reference_files = sorted(references_dir.glob("*.md"))
        if "## Reference Files" not in text:
            errors.append(f"{skill_dir.name}: skills with references/ should expose a '## Reference Files' section")
        if "references/" not in text:
            errors.append(f"{skill_dir.name}: SKILL.md should route to at least one references/ file")
        for reference_file in reference_files:
            errors.extend(validate_reference_file(skill_dir, reference_file))
        errors.extend(validate_reference_reachability(skill_dir, skill_md, reference_files))

    if has_nonempty_dir(scripts_dir) and "scripts/" not in text:
        errors.append(f"{skill_dir.name}: SKILL.md should mention bundled scripts/ when scripts are present")

    if any(has_nonempty_dir(path) for path in (scripts_dir, references_dir, assets_dir)):
        if "## Bundled Resources" not in text:
            errors.append(f"{skill_dir.name}: skills with bundled resources should include a '## Bundled Resources' section")

    progressive_hints = (
        "Read only",
        "Load only",
        "Do not preload",
    )
    if not any(hint in text for hint in progressive_hints):
        errors.append(f"{skill_dir.name}: '## Progressive Loading' should explain how to load references on demand")

    errors.extend(validate_task_router(skill_dir, text))
    errors.extend(validate_skill_antipatterns(skill_dir, text))
    errors.extend(validate_openai_yaml(skill_dir, text))

    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print("ERROR: missing skills/ directory")
        return 1

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    all_errors: list[str] = []
    for skill_dir in skill_dirs:
        all_errors.extend(validate_skill(skill_dir))
    all_errors.extend(validate_teaching_docs())
    all_errors.extend(validate_lint_fixtures())

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Progressive skill validation passed for {len(skill_dirs)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
