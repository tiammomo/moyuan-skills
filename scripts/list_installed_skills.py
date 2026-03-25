#!/usr/bin/env python3
"""List installed skills recorded in skills.lock.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from market_utils import load_lock_payload, resolve_target_root


DEFAULT_TARGET = Path("dist/installed-skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List installed skills from skills.lock.json.")
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET, help="Installation root directory.")
    parser.add_argument("--json", action="store_true", help="Print the lock payload as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_root = resolve_target_root(args.target_root)
    lock_path, lock_payload = load_lock_payload(target_root)
    installed = sorted(lock_payload.get("installed", []), key=lambda item: item.get("skill_id", ""))

    if args.json:
        print(json.dumps({"lock_path": str(lock_path), "installed": installed}, indent=2, ensure_ascii=False))
        return 0

    if not installed:
        print(f"No installed skills recorded in {lock_path}")
        return 0

    print(f"Installed skills in {lock_path}:")
    for entry in installed:
        print(f"- {entry.get('skill_id', '<unknown>')} [{entry.get('channel', '?')}]")
        print(f"  version: {entry.get('version', '?')}")
        print(f"  target: {entry.get('install_target', '?')}")
        print(f"  lifecycle: {entry.get('lifecycle_status', '?')}")
        sources = entry.get("sources", [])
        if isinstance(sources, list) and sources:
            summary = ", ".join(
                f"{item.get('kind', '?')}:{item.get('id', '?')}"
                for item in sources
                if isinstance(item, dict)
            )
            if summary:
                print(f"  sources: {summary}")
        if entry.get("installed_at"):
            print(f"  installed_at: {entry['installed_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
