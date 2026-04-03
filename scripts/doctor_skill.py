#!/usr/bin/env python3
"""Run a local health check for a skill directory."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

from market_utils import BUNDLES_DIR, PUBLISHERS_DIR, ROOT, SKILLS_DIR, repo_relative_path, validate_market_manifest


SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TOP_LEVEL_SECTION_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*$")
INTERFACE_FIELD_RE = re.compile(r"^  ([A-Za-z_][\w-]*):\s*(.+?)\s*$")
QUOTED_STRING_RE = re.compile(r'^"(.*)"$')
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


def is_python_interpreter(token: str) -> bool:
    return Path(token).name.lower().startswith("python")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect a skill and report authoring or market-readiness gaps.")
    parser.add_argument("skill", help="Skill directory name or path.")
    parser.add_argument("--run-checker", action="store_true", help="Execute the checker command from market/skill.json when available.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output.")
    return parser


def resolve_skill_dir(token: str) -> Path:
    candidate = Path(token)
    options: list[Path] = []
    if candidate.is_absolute():
        options.append(candidate)
    else:
        options.append((ROOT / candidate).resolve())
        options.append((SKILLS_DIR / token).resolve())

    for option in options:
        if option.is_dir():
            try:
                option.relative_to(ROOT)
            except ValueError:
                continue
            return option
    raise ValueError(f"could not resolve skill directory from '{token}'")


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, ["SKILL.md is missing YAML frontmatter"]

    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            errors.append("SKILL.md frontmatter contains an invalid line")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, errors


def parse_interface_fields(text: str) -> tuple[dict[str, str], list[str]]:
    fields: dict[str, str] = {}
    errors: list[str] = []
    current_section = ""

    for raw_line in text.splitlines():
        top_level_match = TOP_LEVEL_SECTION_RE.match(raw_line)
        if top_level_match:
            current_section = top_level_match.group(1)
            continue
        if current_section != "interface":
            continue
        field_match = INTERFACE_FIELD_RE.match(raw_line)
        if not field_match:
            continue
        key = field_match.group(1)
        raw_value = field_match.group(2).strip()
        quoted = QUOTED_STRING_RE.match(raw_value)
        if quoted is None:
            errors.append(f"agents/openai.yaml interface field '{key}' should use double-quoted strings")
            continue
        fields[key] = quoted.group(1)
    return fields, errors


def inspect_python_command(command: str, *, label: str) -> tuple[list[str], str | None]:
    errors: list[str] = []
    try:
        tokens = shlex.split(command)
    except ValueError as error:
        return [f"{label}: could not parse command: {error}"], None

    if not tokens:
        return [f"{label}: command is empty"], None
    if not is_python_interpreter(tokens[0]):
        return [f"{label}: command should start with a Python interpreter in this repository"], None
    if len(tokens) < 2:
        return [f"{label}: command should include a Python script path"], None
    if tokens[1] == "-m":
        return [f"{label}: module-style commands are not yet supported by doctor-skill"], None

    script_path = (ROOT / tokens[1]).resolve()
    if not script_path.is_file():
        errors.append(f"{label}: referenced script does not exist: {tokens[1]}")
    return errors, tokens[1]


def run_python_command(command: str) -> tuple[int, str, str]:
    tokens = shlex.split(command)
    adapted = [sys.executable if index == 0 and is_python_interpreter(token) else token for index, token in enumerate(tokens)]
    result = subprocess.run(
        adapted,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def doctor_skill(skill_dir: Path, *, run_checker: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    manifest_payload: dict = {}

    checks.append(f"resolved skill directory: {repo_relative_path(skill_dir)}")
    if not SKILL_NAME_RE.match(skill_dir.name):
        errors.append("skill directory name must use lowercase letters, numbers, and hyphens only")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append("missing SKILL.md")
    else:
        text = skill_md.read_text(encoding="utf-8")
        frontmatter, frontmatter_errors = parse_frontmatter(text)
        errors.extend(frontmatter_errors)
        if frontmatter:
            if set(frontmatter) != {"name", "description"}:
                extras = sorted(set(frontmatter) - {"name", "description"})
                missing = sorted({"name", "description"} - set(frontmatter))
                if missing:
                    errors.append(f"SKILL.md frontmatter is missing required field(s): {', '.join(missing)}")
                if extras:
                    errors.append(f"SKILL.md frontmatter should only contain name and description, found: {', '.join(extras)}")
            if frontmatter.get("name") and frontmatter["name"] != skill_dir.name:
                errors.append("SKILL.md frontmatter 'name' should match the skill directory name")
            if "Use when" not in frontmatter.get("description", ""):
                errors.append("SKILL.md frontmatter 'description' should include an explicit 'Use when' trigger")

        for heading in REQUIRED_HEADINGS:
            if heading not in text:
                errors.append(f"SKILL.md is missing required heading: {heading}")

    agents_yaml = skill_dir / "agents" / "openai.yaml"
    if not agents_yaml.is_file():
        errors.append("missing agents/openai.yaml")
    else:
        fields, field_errors = parse_interface_fields(agents_yaml.read_text(encoding="utf-8"))
        errors.extend(field_errors)
        for field in REQUIRED_INTERFACE_FIELDS:
            if field not in fields:
                errors.append(f"agents/openai.yaml is missing interface field '{field}'")
        default_prompt = fields.get("default_prompt", "")
        if default_prompt and f"${skill_dir.name}" not in default_prompt:
            errors.append("agents/openai.yaml default_prompt should include the skill token")

    manifest_path = skill_dir / "market" / "skill.json"
    if not manifest_path.is_file():
        warnings.append("market/skill.json is missing; add market metadata before packaging or publishing this skill")
    else:
        manifest_payload, manifest_errors = validate_market_manifest(manifest_path)
        errors.extend(manifest_errors)
        if manifest_payload:
            publisher = str(manifest_payload.get("publisher", "")).strip()
            if publisher:
                publisher_path = PUBLISHERS_DIR / f"{publisher}.json"
                if not publisher_path.is_file():
                    errors.append(f"publisher profile is missing: {repo_relative_path(publisher_path)}")
            for bundle_id in manifest_payload.get("distribution", {}).get("starter_bundle_ids", []):
                bundle_path = BUNDLES_DIR / f"{bundle_id}.json"
                if not bundle_path.is_file():
                    warnings.append(f"starter bundle id does not resolve to a local bundle file: {bundle_id}")

            for key in ("checker", "eval"):
                command = str(manifest_payload.get("quality", {}).get(key, "")).strip()
                if not command:
                    errors.append(f"market/skill.json quality.{key} is missing")
                    continue
                command_errors, _ = inspect_python_command(command, label=f"quality.{key}")
                errors.extend(command_errors)

            if run_checker:
                checker_command = str(manifest_payload.get("quality", {}).get("checker", "")).strip()
                if checker_command:
                    returncode, stdout, stderr = run_python_command(checker_command)
                    if returncode != 0:
                        errors.append("checker command failed")
                        if stdout.strip():
                            warnings.append(f"checker stdout:\n{stdout.strip()}")
                        if stderr.strip():
                            warnings.append(f"checker stderr:\n{stderr.strip()}")
                    else:
                        checks.append("checker command passed")

    status = "passed" if not errors else "failed"
    return {
        "status": status,
        "skill_dir": repo_relative_path(skill_dir),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        skill_dir = resolve_skill_dir(args.skill)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1

    payload = doctor_skill(skill_dir, run_checker=args.run_checker)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Skill doctor {payload['status']} for {payload['skill_dir']}")
        if payload["checks"]:
            print("Checks:")
            for item in payload["checks"]:
                print(f"- {item}")
        if payload["warnings"]:
            print("Warnings:")
            for item in payload["warnings"]:
                print(f"- {item}")
        if payload["errors"]:
            print("Errors:")
            for item in payload["errors"]:
                print(f"- {item}")

    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
