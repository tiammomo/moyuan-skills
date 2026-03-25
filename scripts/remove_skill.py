#!/usr/bin/env python3
"""Remove an installed skill and update skills.lock.json."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from market_utils import load_lock_payload, match_installed_entry, resolve_target_root, write_lock_payload


DEFAULT_TARGET = Path("dist/installed-skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Remove an installed skill from the target root.")
    parser.add_argument("skill", help="Skill id, name, or install target.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--dry-run", action="store_true", help="Only print planned removal without deleting files.")
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

    skill_dir = target_root / str(entry.get("install_target", ""))
    if args.dry_run:
        print(f"Dry run: would remove {entry.get('skill_id')} from {skill_dir}")
        return 0

    if skill_dir.exists():
        shutil.rmtree(skill_dir)
    remaining = [item for item in installed if item.get("skill_id") != entry.get("skill_id")]
    lock_payload["installed"] = remaining
    write_lock_payload(lock_path, lock_payload)

    print(f"Removed {entry.get('skill_id')} from {skill_dir}")
    print(f"Updated lock file: {lock_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
