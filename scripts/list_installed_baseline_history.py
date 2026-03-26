#!/usr/bin/env python3
"""List installed-state baseline promotion history."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from market_utils import ROOT, load_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List installed-state baseline promotion history.")
    parser.add_argument("history", type=Path, help="Baseline history JSON file.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    history_path = resolve_repo_path(args.history)
    payload = load_json(history_path)
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []
        payload["entries"] = entries

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"Installed baseline history in {history_path}:")
    print(f"- Baseline path: {payload.get('baseline_path', '?')}")
    print(f"- Baseline Markdown path: {payload.get('baseline_markdown_path', '?')}")
    print(f"- Archive dir: {payload.get('archive_dir', '?')}")
    print(f"- Entries: {len(entries)}")
    print(f"- Next sequence: {payload.get('next_sequence', '?')}")
    if not entries:
        print("- No baseline promotions recorded.")
        return 0

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        summary = entry.get("summary", {})
        print(f"- #{entry.get('sequence', '?')} promoted_at={entry.get('promoted_at', '?')}")
        print(f"  target_root: {entry.get('target_root', '?')}")
        print(f"  installed_count: {summary.get('installed_count', '?')}")
        print(f"  bundle_count: {summary.get('bundle_count', '?')}")
        print(f"  replaced_existing_baseline: {entry.get('replaced_existing_baseline', False)}")
        print(f"  archived_baseline_path: {entry.get('archived_baseline_path', '?')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
