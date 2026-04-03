#!/usr/bin/env python3
"""Scaffold a new skill from a local template pack."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

from market_utils import ROOT, iter_publisher_profile_paths, load_json, repo_relative_path


TEMPLATES_DIR = ROOT / "templates" / "skills"
TEMPLATE_CHOICES = ("beginner", "advanced", "market-ready")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def default_publisher() -> str:
    profiles = iter_publisher_profile_paths()
    if not profiles:
        return "moyuan"
    try:
        payload = load_json(profiles[0])
    except Exception:
        return profiles[0].stem
    publisher_id = str(payload.get("id", "")).strip()
    return publisher_id or profiles[0].stem


def title_from_skill_name(skill_name: str) -> str:
    return " ".join(part.capitalize() for part in skill_name.split("-"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold a new skill from a bundled template.")
    parser.add_argument("skill_name", help="Skill directory name, for example release-note-writer.")
    parser.add_argument(
        "--template",
        choices=TEMPLATE_CHOICES,
        default="market-ready",
        help="Template pack to scaffold. Defaults to market-ready.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("skills"),
        help="Repo-relative parent directory for the generated skill. Defaults to skills.",
    )
    parser.add_argument("--title", help="Optional display title. Defaults to a titleized form of the skill name.")
    parser.add_argument("--publisher", default=default_publisher(), help="Publisher id used by market-ready manifests.")
    parser.add_argument("--channel", default="internal", help="Release channel for market-ready manifests.")
    parser.add_argument("--version", default="0.1.0", help="Initial version for market-ready manifests.")
    parser.add_argument("--summary", help="Optional market summary for market-ready scaffolds.")
    parser.add_argument("--description", help="Optional market description for market-ready scaffolds.")
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help="Category value for market-ready manifests. Repeat to add multiple categories.",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Tag value for market-ready manifests. Repeat to add multiple tags.",
    )
    parser.add_argument(
        "--keyword",
        action="append",
        default=[],
        help="Search keyword value for market-ready manifests. Repeat to add multiple keywords.",
    )
    return parser


def ensure_repo_relative(path: Path) -> Path:
    resolved = path if path.is_absolute() else (ROOT / path)
    resolved = resolved.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"path must stay inside the repository root: {resolved}") from exc
    return resolved


def json_value(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def suggested_python_command() -> str:
    executable = Path(sys.executable)
    if executable.name == "python":
        return "python"
    return shlex.quote(str(executable))


def build_replacements(args: argparse.Namespace, skill_dir: Path) -> dict[str, str]:
    skill_name = args.skill_name
    skill_title = args.title or title_from_skill_name(skill_name)
    skill_name_py = skill_name.replace("-", "_")
    skill_id = f"{args.publisher}.{skill_name}"
    short_description = f"Use ${skill_name} to handle the {skill_title.lower()} workflow."
    market_summary = args.summary or (
        f"Draft, review, and package {skill_title.lower()} workflows with a reusable skill skeleton ready for local market validation."
    )
    market_description = args.description or (
        f"A market-ready starter skill for {skill_title.lower()} workflows that includes progressive routing, a local checker, "
        "bundled references and assets, and enough metadata to pass local market validation before the skill is reviewed or published."
    )
    categories = args.category or ["workflow"]
    tags = args.tag or [skill_name, "template", "draft"]
    keywords = args.keyword or [skill_title.lower(), f"{skill_name} workflow", f"{skill_title.lower()} skill"]
    docs_path = ROOT / "docs" / "skills" / f"{skill_name}.md"
    source_dir = repo_relative_path(skill_dir)
    checker_command = f"python {source_dir}/scripts/check_{skill_name_py}.py"
    eval_command = checker_command

    replacements = {
        "skill_name": skill_name,
        "skill_name_py": skill_name_py,
        "skill_title": skill_title,
        "skill_title_lower": skill_title.lower(),
        "publisher": args.publisher,
        "channel": args.channel,
        "version": args.version,
        "skill_id": skill_id,
        "display_name": skill_title,
        "short_description": short_description,
        "default_prompt": f"Use ${skill_name} to handle the {skill_title.lower()} workflow.",
        "skill_frontmatter_description": (
            f"Explain the exact {skill_title.lower()} workflow, the input shape, and the review boundary. "
            f"Use when Codex needs to draft, review, or package this workflow through a reusable skill."
        ),
        "market_summary": market_summary,
        "market_description": market_description,
        "source_dir": source_dir,
        "entrypoint": f"{source_dir}/SKILL.md",
        "docs_path": repo_relative_path(docs_path),
        "checker_command": checker_command,
        "eval_command": eval_command,
        "lifecycle_notes": "Starter market-ready scaffold waiting for skill-specific review and evaluator upgrades.",
        "categories_json": json_value(categories),
        "tags_json": json_value(tags),
        "keywords_json": json_value(keywords),
        "capabilities_json": json_value([f"{skill_name}-workflow"]),
        "starter_bundle_ids_json": json_value([]),
        "skill_id_json": json_value(skill_id),
        "publisher_json": json_value(args.publisher),
        "skill_name_json": json_value(skill_name),
        "skill_title_json": json_value(skill_title),
        "version_json": json_value(args.version),
        "channel_json": json_value(args.channel),
        "market_summary_json": json_value(market_summary),
        "market_description_json": json_value(market_description),
        "source_dir_json": json_value(source_dir),
        "entrypoint_json": json_value(f"{source_dir}/SKILL.md"),
        "docs_path_json": json_value(repo_relative_path(docs_path)),
        "checker_command_json": json_value(checker_command),
        "eval_command_json": json_value(eval_command),
        "lifecycle_notes_json": json_value(
            "Starter market-ready scaffold waiting for skill-specific review and evaluator upgrades."
        ),
    }
    return replacements


def render_text(text: str, replacements: dict[str, str]) -> str:
    rendered = text
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def destination_for_template(
    template_root: Path,
    template_path: Path,
    *,
    skill_dir: Path,
    skill_name: str,
) -> Path:
    relative = template_path.relative_to(template_root)
    parts = list(relative.parts)
    filename = parts[-1]

    if parts[0] == "docs":
        return ROOT / "docs" / "skills" / f"{skill_name}.md"

    if filename == "agents.openai.yaml.template":
        return skill_dir / "agents" / "openai.yaml"

    output_name = filename[: -len(".template")]
    if output_name == "check_skill.py":
        output_name = f"check_{skill_name.replace('-', '_')}.py"
    parts[-1] = output_name
    return skill_dir.joinpath(*parts)


def scaffold_skill(args: argparse.Namespace) -> int:
    if not SKILL_NAME_RE.match(args.skill_name):
        print("ERROR: skill_name must use lowercase letters, numbers, and hyphens only")
        return 1

    template_root = TEMPLATES_DIR / f"{args.template}-skill"
    if not template_root.is_dir():
        print(f"ERROR: template pack does not exist: {template_root}")
        return 1

    parent_dir = ensure_repo_relative(args.path)
    skill_dir = parent_dir / args.skill_name
    docs_path = ROOT / "docs" / "skills" / f"{args.skill_name}.md"

    if skill_dir.exists():
        print(f"ERROR: skill directory already exists: {repo_relative_path(skill_dir)}")
        return 1

    will_create_docs = any(path.relative_to(template_root).parts[0] == "docs" for path in template_root.rglob("*.template"))
    if will_create_docs and docs_path.exists():
        print(f"ERROR: documentation file already exists: {repo_relative_path(docs_path)}")
        return 1

    replacements = build_replacements(args, skill_dir)
    created: list[Path] = []

    for template_path in sorted(template_root.rglob("*.template")):
        destination = destination_for_template(
            template_root,
            template_path,
            skill_dir=skill_dir,
            skill_name=args.skill_name,
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        source_text = template_path.read_text(encoding="utf-8")
        destination.write_text(render_text(source_text, replacements), encoding="utf-8")
        created.append(destination)

    print(f"Scaffolded {args.template} skill at {repo_relative_path(skill_dir)}")
    if created:
        print("Created files:")
        for path in created:
            print(f"- {repo_relative_path(path)}")

    skill_name_py = args.skill_name.replace("-", "_")
    python_command = suggested_python_command()
    print("Suggested next steps:")
    print(f"- {python_command} scripts/skills_market.py doctor-skill {repo_relative_path(skill_dir)}")
    if args.template == "market-ready":
        print(f"- {python_command} scripts/skills_market.py validate {repo_relative_path(skill_dir / 'market' / 'skill.json')}")
        print(f"- {python_command} scripts/skills_market.py package {repo_relative_path(skill_dir)}")
        print(f"- {python_command} scripts/skills_market.py provenance-check dist/market/install/{args.skill_name}-{args.version}.json")
    checker_path = skill_dir / "scripts" / f"check_{skill_name_py}.py"
    if checker_path.is_file():
        print(f"- {python_command} {repo_relative_path(checker_path)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return scaffold_skill(args)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
