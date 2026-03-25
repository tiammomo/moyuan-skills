#!/usr/bin/env python3
"""Update an installed skill by resolving the latest install spec from a channel index."""

from __future__ import annotations

import argparse
from pathlib import Path

import install_skill
from market_utils import ROOT, load_json, load_lock_payload, match_installed_entry, resolve_target_root


DEFAULT_TARGET = Path("dist/installed-skills")
DEFAULT_INDEX = Path("dist/market/channels/stable.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update an installed skill from a generated channel index.")
    parser.add_argument("skill", help="Installed skill id, name, or install target.")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="Channel index JSON used to resolve the latest install spec.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--dry-run", action="store_true", help="Only print the resolved update plan.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_root = resolve_target_root(args.target_root)
    lock_path, lock_payload = load_lock_payload(target_root)
    installed = lock_payload.get("installed", [])
    entry = next((item for item in installed if match_installed_entry(item, args.skill)), None)
    if entry is None:
        print(f"ERROR: could not find installed skill matching '{args.skill}' in {lock_path}")
        return 1

    index_path = args.index if args.index.is_absolute() else (ROOT / args.index)
    if not index_path.is_file():
        print(f"ERROR: missing channel index {index_path}")
        return 1
    index_payload = load_json(index_path)
    matched = next(
        (
            skill
            for skill in index_payload.get("skills", [])
            if str(skill.get("id", "")).lower() == str(entry.get("skill_id", "")).lower()
        ),
        None,
    )
    if matched is None:
        print(f"ERROR: {entry.get('skill_id')} is not present in {index_path}")
        return 1

    install_spec = str(matched.get("install_spec", ""))
    if not install_spec:
        print(f"ERROR: channel index entry for {entry.get('skill_id')} does not define an install spec")
        return 1

    print(
        f"Resolved update for {entry.get('skill_id')} "
        f"{entry.get('version', '?')} -> {matched.get('version', '?')}"
    )
    forwarded_args = [install_spec, "--target-root", str(target_root)]
    if args.dry_run:
        forwarded_args.append("--dry-run")
    return install_skill.main(forwarded_args)


if __name__ == "__main__":
    raise SystemExit(main())
