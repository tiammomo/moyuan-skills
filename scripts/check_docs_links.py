#!/usr/bin/env python3
"""Validate local markdown links across repository docs."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#+\s+(.*)$", re.MULTILINE)
SCAN_PATTERNS = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/**/*.md",
    "templates/**/*.md",
    "examples/lint-fixtures/README.md",
)


def slugify(text: str) -> str:
    slug = text.strip().lower().replace("`", "")
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug.strip("-")


def markdown_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in SCAN_PATTERNS:
        files.update(ROOT.glob(pattern))
    return sorted(path for path in files if path.is_file())


def resolve_anchor(target: Path, anchor: str) -> bool:
    if not target.is_file() or target.suffix.lower() != ".md":
        return True
    text = target.read_text(encoding="utf-8")
    slugs = {slugify(match.group(1)) for match in HEADING_RE.finditer(text)}
    return anchor.lower() in slugs


def should_ignore(token: str) -> bool:
    return (
        not token
        or token.startswith("#")
        or "://" in token
        or token.startswith(("mailto:", "data:"))
    )


def main() -> int:
    errors: list[str] = []

    for source in markdown_files():
        text = source.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            raw_target = match.group(1).strip().strip("<>")
            if not raw_target:
                continue
            token = raw_target.split()[0]
            if should_ignore(token):
                continue
            path_part, _, anchor = token.partition("#")
            resolved = (source.parent / path_part).resolve()
            if not resolved.exists():
                errors.append(
                    f"{source.relative_to(ROOT).as_posix()}: missing link target '{path_part}'"
                )
                continue
            if anchor and not resolve_anchor(resolved, anchor):
                errors.append(
                    f"{source.relative_to(ROOT).as_posix()}: missing anchor '#{anchor}' in '{path_part}'"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Documentation link check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
